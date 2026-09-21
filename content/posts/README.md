# Blog posts

One markdown file per post. The filename stem is the URL slug unless `slug:` is set.
Posts render at `/blogs/<slug>/` and are listed newest-first by `date`.

The old `/journal/` routes are compatibility redirects only. New links should always
use `/blogs/`.

```markdown
---
title: "The Repo Is the Agent"
date: "2026-09-20"
summary: "Why portable project context matters more than model loyalty."
series: "Own Your AI Stack"
status: "published"
internal_status: "working-draft"
---

Opening paragraph.

## A heading

Body text with **bold**, *italic*, `inline code`, and [links](https://example.com).

```python
print("Fenced code blocks preserve whitespace.")
```

- list item
- another
```

Supported: `#` / `##` / `###` headings, paragraphs, unordered lists, bold,
italic, inline code, fenced code blocks with an optional language name, and links.
Everything is HTML-escaped before formatting is applied.

`status` controls public behavior. `published` pages are indexable and included in
the sitemap; `draft` pages remain reachable but emit `noindex,follow`.

For the current essay series, use `status: published` and
`internal_status: working-draft`: readers see a normal published article while the
internal field records that we may continue polishing the copy. The generator
intentionally ignores `internal_status`.
