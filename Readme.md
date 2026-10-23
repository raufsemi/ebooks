Minimal EPUB Template

Write your book in Markdown and turn it into a clean, modern EPUB.

A lightweight template with customizable styling, captioned images, and an optional imprint page.

⸻

Getting Started

1. Install Dependencies

Install Python 3 if you haven’t already.

Open your terminal in the project folder and run:

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

Windows

Activate the virtual environment using:

.venv\Scripts\activate

2. Write Your Book

Edit the following files to customize your book:

File	Description
book.yaml	Book title, author, language, and publisher
manuscript/book.md	Main book content
manuscript/imprint.md	About this edition
assets/cover.png	Book cover
assets/logo.png	Optional publisher logo
styles/ebook.css	EPUB styling

Write your manuscript using Markdown.

* ## starts a new chapter, with its own page and table-of-contents entry.
* ### creates a section within a chapter.
* # is ignored by the chapter parser, so you can use it as a title in your editor.

3. Add Images

Place your images in manuscript/images/.

Reference them in manuscript/book.md using Markdown:

![Image caption](images/photo.png)

You can customize the appearance of individual images using classes:

![A photograph](images/photo.png){.medium .frame}

Image Classes

Class	Description
.large	Full width (default)
.medium	80% width
.small	60% width
.tiny	35% width
.portrait	55% width, ideal for screenshots
.frame	Adds a thin border
.crop	Crops to a fixed height
.left	Floats the image to the left
.right	Floats the image to the right
.cover	Edge-to-edge image without rounded corners
.icon	Small, rounded image

Image guidelines

* Place each image on its own line, with a blank line before and after it.
* The alt text becomes the image caption.
* Images are automatically resized to a maximum width of 1600 pixels and optimized during the build.
* For consistent results, use the same aspect ratio for similar images, such as 16:9.

4. Build Your EPUB

Generate your book by running:

python3 build.py

Your finished EPUB will appear in the output/ directory.

Tip: Run the build command again whenever you update your manuscript, cover, images, or styling.

5. Customize the Imprint

Edit manuscript/imprint.md to customize the information about your edition.

The following placeholders are automatically populated using values from book.yaml:

* {{ publisher }}
* {{ editor }}
* {{ imprint_note }}

Lines whose placeholders are all empty are automatically removed.

⸻

Project Structure

.
├── assets/
│   ├── cover.png
│   └── logo.png
├── manuscript/
│   ├── book.md
│   ├── imprint.md
│   └── images/
├── styles/
│   └── ebook.css
├── output/
├── book.yaml
├── build.py
└── requirements.txt

Path	Purpose
assets/	Book cover and optional logo
manuscript/	Manuscript, imprint, and images
styles/	EPUB stylesheet
output/	Generated EPUB files
book.yaml	Book metadata
build.py	EPUB build script
requirements.txt	Python dependencies

⸻

Notes

* Test your EPUB: Use Apple Books, Calibre, or Kindle Previewer.
* Reader compatibility: EPUB readers may render some CSS features differently.
* Copyright: Only distribute content you have the right to publish. Public-domain rules vary by country.

License

Add a license of your choice before distributing this template.