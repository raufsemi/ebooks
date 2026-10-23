# Sample Book Title

<!--
QUICK RULES
  #    = ignored (use it for the book title)
  ##   = chapter: own page + table-of-contents entry
  ###  = section inside a chapter
  Leave a blank line between every block.
  Never start a line with # inside a code block.
-->

## Basics

### Headings

Use `##` for a chapter and `###` for a section. Deeper levels (`####`, `#####`) also work.

Each chapter becomes its own page. Write your text under the headings.

### Text

```markdown
**bold**  *italic*  `code`  [link](https://example.com)

> A quote becomes a soft callout box.

---
```

Result: **bold**, *italic*, `code`, and a [link](https://example.com).

> A quote becomes a soft callout box.

---

Three dashes make the dotted divider above.

### Lists

```markdown
- Bullet
  - Nested bullet

1. First
2. Second
```

- Bullet
  - Nested bullet

1. First
2. Second

## Images

### Add an image

Put your files in `images/`, then write:

```markdown
![Caption goes here](images/image.png)
```

The image must be on its own line, with a blank line above and below. The text in the brackets is the caption. Leave it empty (`![](...)`) for no caption.

![Caption goes here](images/image.png)

### Size and style

Add classes in curly braces right after the image:

```markdown
![Weekly chart](images/sample-chart.png){.medium .frame}
```

![Weekly chart](images/sample-chart.png){.medium .frame}

![Phone screenshot](images/sample-screen.png){.portrait}

![Cropped to a fixed height](images/sample-landscape.png){.crop}

| Class | Effect |
|---|---|
| `.large` | Full width (default) |
| `.medium` | 80% width |
| `.small` | 60% width |
| `.tiny` | 35% width |
| `.portrait` | 55% width, for screenshots |
| `.frame` | Thin border |
| `.crop` | Fixed height, cropped to fill |
| `.icon` | Small round avatar |
| `.cover` | Edge to edge, no rounding |
| `.left` / `.right` | Float beside text |

Tip: use the same aspect ratio (such as 16:9) for all photos so they look consistent.

## Extras

### Tables

```markdown
| Item  | Qty |
|-------|-----|
| Apple | 3   |
```

| Item  | Qty |
|-------|-----|
| Apple | 3   |

### Code

````markdown
```python
print("Hello")
```
````

```python
print("Hello")
```

### Footnotes

Add a marker in the text[^1] and define it in the same section, not in another one.

```markdown
Add a marker in the text[^1].

[^1]: The note text.
```

[^1]: This is the footnote.