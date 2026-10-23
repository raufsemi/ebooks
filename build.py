from pathlib import Path
from io import BytesIO
from html import escape
from urllib.parse import unquote
import mimetypes
import re

import yaml
import markdown
from PIL import Image
from ebooklib import epub


ROOT = Path(__file__).resolve().parent
META_FILE = ROOT / "book.yaml"
TEXT_FILE = ROOT / "manuscript" / "book.md"
IMPRINT_FILE = ROOT / "manuscript" / "imprint.md"
CSS_FILE = ROOT / "styles" / "ebook.css"
ASSET_DIR = ROOT / "assets"
OUT_DIR = ROOT / "output"

# ---- Image settings -------------------------------------------------
MAX_IMAGE_WIDTH = 1600  # wider images are scaled down to keep the EPUB light

IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
SRC_ATTR = re.compile(r'src="([^"]+)"')
ALT_ATTR = re.compile(r'alt="([^"]*)"')
LONE_IMG = re.compile(r"<p>\s*(<img\b[^>]*>)\s*</p>", re.I)

# Matches {{ publisher }}, {{editor}}, etc. in imprint.md
PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")

DEFAULT_IMPRINT = """# About This Edition

Published by {{ publisher }}

Edited by {{ editor }}

{{ imprint_note }}
"""

# Remembers which images were already added: {source path: path in EPUB}
IMAGE_REGISTRY = {}


def create_cover():
    cover_path = next(
        (
            ASSET_DIR / name
            for name in ("cover.png", "cover.jpg", "cover.jpeg")
            if (ASSET_DIR / name).is_file()
        ),
        None,
    )

    if cover_path is None:
        raise SystemExit(
            "Add your cover to assets/cover.png, cover.jpg, or cover.jpeg."
        )

    width, height = 1600, 2400

    with Image.open(cover_path) as original:
        image = original.convert("RGB")

        source_ratio = image.width / image.height
        target_ratio = width / height

        if source_ratio > target_ratio:
            new_width = int(image.height * target_ratio)
            left = (image.width - new_width) // 2
            image = image.crop(
                (left, 0, left + new_width, image.height)
            )
        else:
            new_height = int(image.width / target_ratio)
            top = (image.height - new_height) // 2
            image = image.crop(
                (0, top, image.width, top + new_height)
            )

        image = image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95, optimize=True)

    return buffer.getvalue()


def slugify(value):
    return (
        re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        or "ebook"
    )


# =====================================================================
# IMAGE HANDLING
# =====================================================================

def find_image(src):
    """
    Locate an image referenced in the Markdown.
    Tries: relative to manuscript/, then the project root,
    then the images/ folder by file name.
    """

    candidates = [
        (TEXT_FILE.parent / src),
        (ROOT / src),
        (ROOT / "images" / Path(src).name),
    ]

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue

        if resolved.is_file():
            return resolved

    return None


def optimize_image(path):
    """
    Scale down very wide images and compress them.
    Falls back to the original bytes if anything goes wrong
    (e.g. SVG, GIF, WebP).
    """

    suffix = path.suffix.lower()

    if suffix not in (".png", ".jpg", ".jpeg"):
        return path.read_bytes()

    try:
        with Image.open(path) as original:
            image = original.copy()

        if image.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / image.width
            image = image.resize(
                (MAX_IMAGE_WIDTH, round(image.height * ratio)),
                Image.Resampling.LANCZOS,
            )

        buffer = BytesIO()

        if suffix == ".png":
            image.save(buffer, format="PNG", optimize=True)
        else:
            image.convert("RGB").save(
                buffer, format="JPEG", quality=88, optimize=True
            )

        return buffer.getvalue()

    except Exception:
        return path.read_bytes()


def register_images(book, html, prefix="../"):
    """
    Add every local image used in the HTML to the EPUB
    and rewrite its src so it works from the page's folder.

    prefix="../" for pages inside sections/, "" for pages in the root.
    """

    def replace(match):
        tag = match.group(0)
        src_match = SRC_ATTR.search(tag)

        if not src_match:
            return tag

        src = unquote(src_match.group(1))

        # Skip web links, data URIs, etc.
        if re.match(r"^[a-z][a-z0-9+.-]*:", src, re.I):
            return tag

        path = find_image(src)

        if path is None:
            print(f"WARNING: image not found -> {src}")
            return tag

        if path not in IMAGE_REGISTRY:
            number = len(IMAGE_REGISTRY) + 1
            epub_name = (
                f"images/content-{number:03}-{slugify(path.stem)}"
                f"{path.suffix.lower()}"
            )
            media_type = mimetypes.guess_type(path.name)[0] or "image/png"

            book.add_item(
                epub.EpubItem(
                    uid=f"content-image-{number}",
                    file_name=epub_name,
                    media_type=media_type,
                    content=optimize_image(path),
                )
            )

            IMAGE_REGISTRY[path] = epub_name
            print(f"Image added: {src} -> {epub_name}")

        new_src = f'src="{prefix}{IMAGE_REGISTRY[path]}"'
        return tag.replace(src_match.group(0), new_src)

    return IMG_TAG.sub(replace, html)


def wrap_figures(html):
    """
    A paragraph containing only an image becomes a <figure>.
    The alt text becomes the caption.
    """

    def replace(match):
        img = match.group(1)
        alt = ALT_ATTR.search(img)
        caption = alt.group(1).strip() if alt else ""

        if not caption:
            return f"<figure>{img}</figure>"

        return f"<figure>{img}<figcaption>{caption}</figcaption></figure>"

    return LONE_IMG.sub(replace, html)


def fill_placeholders(text, meta):
    """
    Replace {{ key }} with values from book.yaml.
    A line whose placeholders are all empty is dropped,
    so unused fields leave no blank gaps.
    """

    lines = []

    for line in text.splitlines():
        keys = PLACEHOLDER.findall(line)

        if keys and not any(meta.get(key) for key in keys):
            continue

        lines.append(
            PLACEHOLDER.sub(
                lambda m: escape(str(meta.get(m.group(1)) or ""), quote=False),
                line,
            )
        )

    return "\n".join(lines)


# =====================================================================
# MANUSCRIPT PARSING
# =====================================================================

def parse_manuscript(source):
    """
    Parse Markdown into major sections and nested subsections.

    ## creates a major EPUB section.
    ### and deeper headings create nested navigation entries.
    Content before the first ## heading is preserved.
    """

    pattern = re.compile(
        r"(?m)^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$"
    )

    matches = list(pattern.finditer(source))
    sections = []
    preamble = source[:matches[0].start()].strip() if matches else source.strip()

    if preamble:
        sections.append(
            {
                "title": None,
                "level": 2,
                "content": preamble,
                "children": [],
            }
        )

    current_section = None
    stack = []

    for index, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(source)
        )

        content = source[match.end():end].strip()

        # H1 is treated as document-level metadata, not a content section.
        if level == 1:
            continue

        node = {
            "title": title,
            "level": level,
            "content": content,
            "children": [],
        }

        if level == 2:
            sections.append(node)
            current_section = node
            stack = [node]
            continue

        # A subsection before the first major section becomes its own section.
        if current_section is None:
            sections.append(node)
            current_section = node
            stack = [node]
            continue

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
            stack.append(node)
        else:
            sections.append(node)
            current_section = node
            stack = [node]

    return sections


def render_markdown(content):
    # "extra" already includes attr_list, so {.medium .frame} works.
    return markdown.markdown(
        content,
        extensions=["extra", "footnotes", "sane_lists"],
        output_format="html5",
    )


def create_section_node(book, style, node, index, language):
    """
    Create an EPUB document for a major section.
    Subsections remain within the same XHTML file.
    """

    filename = f"sections/section-{index:03}.xhtml"

    body = render_markdown(node["content"])

    def render_children(children):
        rendered = []

        for child in children:
            heading_level = min(child["level"], 6)
            child_content = render_markdown(child["content"])

            rendered.append(
                f'<section class="subsection">'
                f'<h{heading_level}>{escape(child["title"])}</h{heading_level}>'
                f'{child_content}'
                f'{render_children(child["children"])}'
                f'</section>'
            )

        return "\n".join(rendered)

    title = node["title"] or "Untitled Section"

    heading = (
        f"<h1>{escape(title)}</h1>"
        if node["title"]
        else ""
    )

    page = epub.EpubHtml(
        title=title,
        file_name=filename,
        lang=language,
    )

    html = (
        f'<section class="book-section">'
        f'{heading}'
        f'{body}'
        f'{render_children(node["children"])}'
        f'</section>'
    )

    # Images: make figures, then add the files into the EPUB.
    html = wrap_figures(html)
    html = register_images(book, html)

    page.content = html

    page.add_item(style)
    book.add_item(page)

    return page


def build_toc(nodes, pages, parent_level=0):
    """
    Build nested EPUB navigation from the manuscript heading hierarchy.
    """

    result = []

    for node, page in zip(nodes, pages):
        entry = epub.Link(
            page.file_name,
            node["title"] or "Opening",
            f"section-{id(node)}",
        )

        children = build_toc(
            node["children"],
            [page] * len(node["children"]),
            parent_level + 1,
        )

        if children:
            result.append((entry, children))
        else:
            result.append(entry)

    return result


def main():
    for path in (META_FILE, TEXT_FILE, CSS_FILE):
        if not path.is_file():
            raise SystemExit(f"Missing required file: {path}")

    IMAGE_REGISTRY.clear()

    meta = yaml.safe_load(
        META_FILE.read_text(encoding="utf-8")
    ) or {}

    source = TEXT_FILE.read_text(
        encoding="utf-8-sig"
    ).strip()

    css = CSS_FILE.read_text(encoding="utf-8")

    for field in ("title", "author", "language", "identifier"):
        if not meta.get(field):
            raise SystemExit(f"Missing metadata: {field}")

    title = str(meta["title"])
    author = str(meta["author"])
    language = str(meta["language"])
    publisher = str(meta.get("publisher", ""))

    book = epub.EpubBook()
    book.set_identifier(str(meta["identifier"]))
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)

    if meta.get("description"):
        book.add_metadata(
            "DC",
            "description",
            str(meta["description"]),
        )

    if publisher:
        book.add_metadata("DC", "publisher", publisher)

    style = epub.EpubItem(
        uid="ebook-css",
        file_name="styles/ebook.css",
        media_type="text/css",
        content=css.encode("utf-8"),
    )

    book.add_item(style)
    book.set_cover("cover.jpg", create_cover())

    # Title page
    title_page = epub.EpubHtml(
        title="Title Page",
        file_name="title.xhtml",
        lang=language,
    )

    subtitle = str(meta.get("subtitle", ""))
    translator = str(meta.get("translator", ""))

    title_page.content = f"""
    <section class="title-page">
        <h1>{escape(title)}</h1>
        {f'<p class="subtitle">{escape(subtitle)}</p>' if subtitle else ''}
        <p class="author">{escape(author)}</p>
        {f'<p class="translator">Translated by {escape(translator)}</p>' if translator else ''}
    </section>
    """

    title_page.add_item(style)
    book.add_item(title_page)

    # Imprint page (manuscript/imprint.md, with {{ placeholders }})
    imprint_source = (
        IMPRINT_FILE.read_text(encoding="utf-8-sig")
        if IMPRINT_FILE.is_file()
        else DEFAULT_IMPRINT
    )

    imprint_html = render_markdown(fill_placeholders(imprint_source, meta))
    imprint_html = register_images(book, imprint_html, prefix="")

    imprint_page = epub.EpubHtml(
        title="About This Edition",
        file_name="imprint.xhtml",
        lang=language,
    )

    imprint_page.content = f'<section class="imprint-page">{imprint_html}</section>'

    imprint_page.add_item(style)
    book.add_item(imprint_page)

    # Parse manuscript
    sections = parse_manuscript(source)

    if not sections:
        raise SystemExit("No readable content found in manuscript/book.md.")

    # Create one XHTML page per major section.
    section_pages = []

    for index, section in enumerate(sections, start=1):
        page = create_section_node(
            book,
            style,
            section,
            index,
            language,
        )

        section_pages.append(page)

    # Navigation: major sections are linked to their XHTML pages.
    # Nested subsection navigation can be added separately once
    # subsection fragments are generated.
    book.toc = tuple(
        epub.Link(
            page.file_name,
            section["title"] or "Opening",
            f"section-{index}",
        )
        for index, (section, page) in enumerate(
            zip(sections, section_pages),
            start=1,
        )
    )

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = [
        title_page,
        imprint_page,
        *section_pages,
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    destination = OUT_DIR / f"{slugify(title)}.epub"

    epub.write_epub(str(destination), book)

    print(f"\nSUCCESS: {destination}")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Publisher: {publisher or '(not set)'}")
    print(f"Major sections: {len(section_pages)}")
    print(f"Content images: {len(IMAGE_REGISTRY)}")


if __name__ == "__main__":
    main()