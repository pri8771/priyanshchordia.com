# Journal posts

One markdown file per post. The filename stem is the URL slug unless `slug:` is set.
Posts render at `/journal/<slug>/` and are listed newest-first by `date`.

```markdown
---
title: "The Repo Is the Agent"
date: "2026-09-20"
summary: "Why portable project context matters more than model loyalty."
series: "Own Your AI Stack"
status: "draft"
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

`status` may be `published` or `draft`. Drafts remain reachable and are shown
in the journal, but their pages emit `noindex,follow` and are omitted from the
sitemap until promoted to `published`.
