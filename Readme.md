# Minimal EPUB Template

Write a book in Markdown, get a clean, modern EPUB.
Includes a ready-made stylesheet, captioned images, and a customizable imprint page.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build.py
```

Your book appears in `output/`.

## Project structure

```
.
├── book.yaml            # title, author, language, publisher...
├── build.py             # the build script
├── manuscript/
│   ├── book.md          # your book
│   └── imprint.md       # "About this edition" page
├── images/              # images used in book.md
├── assets/
│   ├── cover.png        # cover (any size, auto-cropped to 2:3)
│   └── logo.png         # publisher logo (optional)
├── styles/ebook.css     # the design
└── output/              # generated EPUB
```

## Writing

- `##` starts a chapter (own page and table-of-contents entry).
- `###` and deeper are sections inside a chapter.
- `#` is ignored, so you can use it as the book title in your editor.

## Images

```markdown
![Caption text](images/photo.png)
![Caption](images/chart.png){.medium .frame}
```

Put the image on its own line with blank lines around it. The alt text becomes the caption.

| Class | Effect |
|---|---|
| `.large` | Full width (default) |
| `.medium` / `.small` / `.tiny` | 80% / 60% / 35% width |
| `.portrait` | 55% width, for phone screenshots |
| `.frame` | Thin border |
| `.crop` | Fixed height, cropped to fill |
| `.icon` | Small round avatar |
| `.cover` | Edge to edge, no rounding |
| `.left` / `.right` | Float beside text |

Images are resized to 1600 px wide at most and optimized automatically.
For a consistent look, use the same aspect ratio (e.g. 16:9) for photos.

## Imprint placeholders

In `manuscript/imprint.md`, `{{ publisher }}`, `{{ editor }}` and `{{ imprint_note }}`
are filled from `book.yaml`. Any line whose placeholders are all empty is removed.

## Notes

- Test your EPUB in more than one reader (Apple Books, Calibre, Kindle Previewer).
  Readers support CSS differently, so cropping and drop caps may vary.
- Only use texts you have the right to publish. Public-domain rules differ by country.

## License

Add a license of your choice (for example MIT) before publishing.