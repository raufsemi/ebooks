# Minimal EPUB Template

Write your book in Markdown. Run one command to get an EPUB.

## Setup

You need Python 3. In the project folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

## Build

```bash
python3 build.py
```

Your EPUB appears in `output/`. Run it again after every change.

## What to edit

| File | What it is |
|---|---|
| `book.yaml` | Title, author, language, publisher |
| `manuscript/book.md` | Your book |
| `manuscript/imprint.md` | The "About this edition" page |
| `assets/cover.png` | Cover |
| `assets/logo.png` | Logo (optional) |
| `styles/ebook.css` | Look of the book |

`manuscript/book.md` is also a short tutorial. Read it, then replace it with your own text.

## Writing

- `##` starts a chapter. Each chapter gets its own page and a table of contents entry.
- `###` starts a section inside a chapter.
- `#` is ignored. Use it for the book title.
- `\pagebreak` on its own line starts a new page.
- Footnotes: write `[^1]` in your text and `[^1]: Your note.` anywhere in the same chapter.

## Images

Put pictures in `images/`, then add this to `book.md`:

```markdown
![Caption](images/photo.png)
![Caption](images/photo.png){.medium .frame}
```

Rules:

- Put the image on its own line, with an empty line above and below.
- The text in the brackets is the caption.
- Images wider than 1600 px are shrunk automatically.
- Use the same shape for similar pictures (for example 16:9) so they look even.

Add these words in `{ }` after the image:

| Word | Effect |
|---|---|
| `.large` | Full width (default) |
| `.medium` | 80% width |
| `.small` | 60% width |
| `.tiny` | 35% width |
| `.portrait` | 55% width, good for screenshots |
| `.frame` | Thin border |
| `.crop` | Fixed height, cropped to fill |
| `.icon` | Small round picture |
| `.cover` | Edge to edge, no rounded corners |
| `.left` / `.right` | Float beside the text |

## Imprint

In `manuscript/imprint.md`, `{{ publisher }}`, `{{ editor }}` and `{{ imprint_note }}` are filled in from `book.yaml`. A line is removed if its value is empty.

## Folders

```
.
├── assets/        cover and logo
├── images/        pictures used in the book
├── manuscript/    book.md and imprint.md
├── styles/        ebook.css
├── output/        the finished EPUB
├── book.yaml
├── build.py
└── requirements.txt
```

## Notes

- Readers show some styles differently. Check your EPUB in Apple Books, Calibre or Kindle Previewer.
- Only publish texts you have the right to share. Public-domain rules are different in each country.

## License

Add a license before you share this.