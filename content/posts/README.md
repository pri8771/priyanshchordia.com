# Journal posts

One markdown file per post. The filename stem is the URL slug unless `slug:` is set.
Posts render at `/journal/<slug>/` and are listed newest-first by `date`.

```markdown
---
title: "Public product pages should be generated"
date: "2026-07-26"
summary: "One sanitized source, every page derived from it."
---

Opening paragraph.

## A heading

Body text with **bold**, *italic*, `code`, and [links](https://example.com).

- list item
- another
```

Supported: `##` headings, paragraphs, unordered lists, bold, italic, inline code,
and links. Everything is HTML-escaped before formatting is applied.
