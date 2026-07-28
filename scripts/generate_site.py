#!/usr/bin/env python3
"""Generate the dependency-free public site: catalog, journal, and app store pages.

Visual direction: "Signal Catalog" (design/concepts/signal-catalog.html on the
design-concepts branch). The site is a product catalogue plus a journal — it is
deliberately not a personal/biographical site.

Sources of truth:
  data/registry.public.json  sanitized product projection (never edit by hand)
  data/apps.json             per-app store metadata for privacy/support routes
  content/posts/*.md         journal posts (front matter + markdown subset)
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "registry.public.json"
APPS = ROOT / "data" / "apps.json"
POSTS = ROOT / "content" / "posts"
OUT = ROOT / "site"
THEMES_DIR = ROOT / "scripts" / "themes"
EXPERIENCES_DIR = ROOT / "scripts" / "experiences"

# Set to the apex domain ONLY after DNS resolves to GitHub Pages. Emitting a
# CNAME file early makes Pages redirect github.io -> the domain, which darks
# the site until propagation completes. None = keep serving on github.io.
CUSTOM_DOMAIN: str | None = "priyanshchordia.com"

SITE_NAME = "priyanshchordia.com"
DESCRIPTION = "A catalogue of independent software — games, private utilities, and tools for clearer work."

# Minimal inline favicon (dark rounded square, one dot — echoes the nav's status
# dot) so browser tabs aren't blank. No binary asset file, no external request,
# consistent with the rest of the site.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='7' fill='%23141414'/%3E"
    "%3Ccircle cx='16' cy='16' r='6' fill='%23d7ff4a'/%3E"
    "%3C/svg%3E"
)

THEMES = [
    ("signal", "Signal Catalog"),
    ("editorial", "Editorial Ledger"),
    ("instrument", "Instrument Panel"),
    ("gallery", "Living Gallery"),
    ("monolith", "Monolith"),
    ("overworld", "Overworld"),
    ("unknown-signal", "Unknown Signal"),
    ("cabinet", "Cabinet"),
    ("parallel", "Parallel Universes"),
    ("workshop", "Hidden Workshop"),
    ("department", "Department"),
]


def _load_css() -> str:
    """Assemble the site stylesheet from scripts/themes/: base.css plus one
    file per theme, concatenated in THEMES order (base first). Keeping each
    theme's CSS in its own file is what makes them separately reviewable and
    editable -- the generated output is unchanged, just its source layout.
    """
    parts = [(THEMES_DIR / "base.css").read_text(encoding="utf-8")]
    for slug, _name in THEMES:
        parts.append((THEMES_DIR / f"{slug}.css").read_text(encoding="utf-8"))
    return "\n".join(parts)

CSS = _load_css()


def esc(value: object) -> str:
    return html.escape(str(value or ""))


# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------

def load_products() -> list[dict[str, object]]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = data.get("products", [])
    for product in products:
        slug = str(product.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe product slug: {slug!r}")
        if product.get("public_tier") not in {"featured", "lab"}:
            raise ValueError(f"Non-public tier entered public snapshot: {product.get('id')}")
    products.sort(key=lambda p: (p.get("public_tier") != "featured", str(p.get("name", ""))))
    return products


def load_apps() -> list[dict[str, object]]:
    """Store metadata for App Store privacy/support routes.

    An app with an unresolved support_contact is skipped, never rendered with a
    placeholder — a fabricated support address on a live listing is worse than
    a missing page.
    """
    if not APPS.exists():
        return []
    apps = json.loads(APPS.read_text(encoding="utf-8")).get("apps", [])
    seen: set[str] = set()
    for app in apps:
        slug = str(app.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe app slug: {slug!r}")
        if slug in RESERVED_ROUTES:
            raise ValueError(f"App slug {slug!r} collides with a reserved top-level route")
        if slug in seen:
            raise ValueError(f"Duplicate app slug: {slug!r}")
        seen.add(slug)
    return apps


RESERVED_ROUTES = {"products", "journal", "apps", "assets", "static", "index"}


FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


def load_posts() -> list[dict[str, object]]:
    if not POSTS.exists():
        return []
    posts: list[dict[str, object]] = []
    for path in sorted(POSTS.glob("*.md")):
        if path.stem.startswith("_") or path.name.lower() == "readme.md":
            continue  # docs, not posts
        raw = path.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(raw)
        if not match:
            raise ValueError(f"{path.name}: missing front matter (--- title/date --- block)")
        meta: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip().strip('"')
        slug = meta.get("slug") or path.stem
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"{path.name}: unsafe slug {slug!r}")
        body = match.group(2)
        posts.append({
            "slug": slug,
            "title": meta.get("title") or path.stem.replace("-", " ").title(),
            "date": meta.get("date", ""),
            "summary": meta.get("summary", ""),
            "body": body,
            "minutes": max(1, round(len(body.split()) / 200)),
        })
    posts.sort(key=lambda p: str(p.get("date", "")), reverse=True)
    return posts


# --------------------------------------------------------------------------
# tiny markdown subset — no third-party dependencies on the Pages runner
# --------------------------------------------------------------------------

def inline(text: str) -> str:
    out = esc(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+|/[^\s)]*)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", out)
    return out


def markdown(body: str) -> str:
    blocks: list[str] = []
    for chunk in re.split(r"\n\s*\n", body.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith("## "):
            blocks.append(f"<h2>{inline(chunk[3:].strip())}</h2>")
        elif chunk.startswith("# "):
            blocks.append(f"<h2>{inline(chunk[2:].strip())}</h2>")
        elif all(line.lstrip().startswith(("- ", "* ")) for line in chunk.splitlines()):
            items = "".join(f"<li>{inline(l.lstrip()[2:])}</li>" for l in chunk.splitlines())
            blocks.append(f"<ul>{items}</ul>")
        else:
            blocks.append(f"<p>{inline(chunk)}</p>")
    return "".join(blocks)


# --------------------------------------------------------------------------
# page chrome
# --------------------------------------------------------------------------

def asset_hash(text: str) -> str:
    """Short content hash so a deploy always invalidates cached CSS/JS."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


EXPERIENCE_FILES = ["unknown-signal", "overworld", "cabinet", "parallel"]


def _load_js() -> str:
    """Assemble scripts/experiences.js from scripts/experiences/: common.js
    (shared IIFE setup -- product data, root/host handles, the `el()` helper)
    first, then one file per interactive experience, then dispatch.js (the
    REGISTRY/`sync()` router plus the closing of the shared IIFE opened by
    common.js). common.js and dispatch.js are two halves of one wrapper, not
    two independent modules -- the whole original file is a single IIFE, so
    the opening half must load first and the closing half must load last for
    the concatenated result to parse. The four experience files sandwiched
    between them are order-independent (top-level function declarations are
    hoisted within that shared scope). Keeping each experience in its own
    file is what makes them separately reviewable and editable -- the
    generated output is unchanged, just its source layout.
    """
    parts = [(EXPERIENCES_DIR / "common.js").read_text(encoding="utf-8")]
    for slug in EXPERIENCE_FILES:
        parts.append((EXPERIENCES_DIR / f"{slug}.js").read_text(encoding="utf-8"))
    parts.append((EXPERIENCES_DIR / "dispatch.js").read_text(encoding="utf-8"))
    return "\n".join(parts)


EXPERIENCES = _load_js()
CSS_V = ""
XP_V = ""


DEFAULT_THEME = "unknown-signal"


def options_html() -> str:
    return "".join(
        f'<option value="{k}"{" selected" if k == DEFAULT_THEME else ""}>{v}</option>'
        for k, v in THEMES
    )


def chrome(title: str, body: str, prefix: str = "", active: str = "",
           description: str = DESCRIPTION, extra: str = "") -> str:
    def cls(name: str) -> str:
        return ' class="active"' if active == name else ""
    options = options_html()
    # Applied in <head> so the stored theme paints on first frame, no flash.
    preload = ("<script>(function(){try{var t=localStorage.getItem('pc-theme');"
               "if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}})()</script>")
    switcher = ("<script>(function(){var ss=[].slice.call(document.querySelectorAll('.themer'));"
                "if(!ss.length)return;try{var t=localStorage.getItem('pc-theme');"
                "if(t)ss.forEach(function(s){s.value=t})}catch(e){}"
                "ss.forEach(function(s){s.addEventListener('change',function(){var v=s.value;"
                "document.documentElement.setAttribute('data-theme',v);"
                "ss.forEach(function(o){o.value=v});"
                "try{localStorage.setItem('pc-theme',v)}catch(e){}})})})()</script>")
    return f"""<!doctype html>
<html lang="en" data-theme="{DEFAULT_THEME}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)}</title>{preload}<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{prefix}styles.css?v={CSS_V}"></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><div class="left">
<select id="themer" class="themer" aria-label="Colour theme">{options}</select>
<a class="brand" href="{prefix}index.html">P/C <span class="status" aria-hidden="true">&#9679;</span></a></div>
<nav aria-label="Primary"><a{cls('work')} href="{prefix}index.html#work">Work</a><a{cls('journal')} href="{prefix}journal/">Journal</a></nav></header>
<main id="main">{body}</main>
<footer><span>{esc(SITE_NAME)}</span><span>Generated from a sanitized public registry</span></footer>
</div>{extra}{switcher}</body></html>"""


def product_tile(product: dict[str, object], index: int, prefix: str = "") -> str:
    lane = str(product.get("portfolio_lane", "software")).replace("-", " ")
    return (
        f'<a class="product" href="{prefix}products/{esc(product["slug"])}/">'
        f'<span class="num">{index:02d}</span><h3>{esc(product["name"])}</h3>'
        f'<p>{esc(product["summary"])}</p>'
        f'<span class="meta">{esc(lane)} / {esc(product.get("public_tier", ""))}</span></a>'
    )


def entry_row(post: dict[str, object], index: int, prefix: str = "") -> str:
    return (
        f'<a class="entry" href="{prefix}journal/{esc(post["slug"])}/">'
        f'<span>{index:03d}</span><strong>{esc(post["title"])}</strong>'
        f'<span>{esc(post["minutes"])} min</span></a>'
    )


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def home(products: list[dict[str, object]], posts: list[dict[str, object]]) -> str:
    tiles = "".join(product_tile(p, i + 1) for i, p in enumerate(products))
    if posts:
        rows = "".join(entry_row(p, i + 1) for i, p in enumerate(posts[:5]))
        journal = f'<div class="journal-index">{rows}</div>'
    else:
        journal = '<p class="empty">No entries published yet.</p>'
    body = f"""<section class="hero"><div><div class="kicker">Independent software / live index</div>
<h1>Useful<br>signals.</h1></div>
<p>{len(products)} focused products. Games, private utilities, spiritual practice, and tools for clearer work &mdash; catalogued for direct browsing.</p></section>
<section id="work"><div class="section-head"><span class="label">01 / Catalog</span><h2>Everything transmitting.</h2></div>
<div class="products" aria-label="All products">{tiles}</div></section>
<section id="journal"><div class="section-head"><span class="label">02 / Journal</span><h2>Notes from the workbench.</h2></div>
{journal}</section>"""
    payload = json.dumps([
        {"name": p["name"], "summary": p["summary"], "href": f"products/{p['slug']}/",
         "lane": str(p.get("portfolio_lane", "")).replace("-", " ")}
        for p in products
    ], ensure_ascii=False)
    extra = (
        '<div id="xp" class="xp"></div>'
        '<select id="themer2" class="themer xp-switch" aria-label="Design">' + options_html() + "</select>"
        f'<script>window.__PRODUCTS={payload}</script>'
        f'<script src="experiences.js?v={XP_V}" defer></script>'
    )
    return chrome(f"{SITE_NAME} — software catalogue", body, active="work", extra=extra)


def product_page(product: dict[str, object]) -> str:
    lane = str(product.get("portfolio_lane", "software")).replace("-", " ")
    tier = "Featured" if product.get("public_tier") == "featured" else "Lab"
    body = f"""<section><div class="section-head"><span class="label">Product record</span><h2>One signal, expanded.</h2></div>
<article class="detail"><span class="label">{esc(tier)} / {esc(lane)}</span>
<h1>{esc(product["name"])}</h1><p>{esc(product["summary"])}</p>
<div class="facts">
<div class="fact"><small>Stage</small>{esc(str(product.get("stage", "building")).title())}</div>
<div class="fact"><small>Portfolio lane</small>{esc(lane.title())}</div>
<div class="fact"><small>Public tier</small>{esc(tier)}</div>
<div class="fact"><small>Publishing rule</small>Only verified public fields are rendered.</div>
</div></article><a class="back" href="../../index.html#work">&larr; Back to the catalog</a></section>"""
    return chrome(
        f"{product['name']} — {SITE_NAME}", body, prefix="../../", active="work",
        description=str(product.get("summary", DESCRIPTION)),
    )


def journal_index(posts: list[dict[str, object]]) -> str:
    if posts:
        rows = "".join(entry_row(p, i + 1, "../") for i, p in enumerate(posts))
        listing = f'<div class="journal-index">{rows}</div>'
    else:
        listing = ('<p class="empty">No entries published yet. Posts are markdown files in '
                   '<code>content/posts/</code> &mdash; see the README there for the format.</p>')
    body = f"""<section><div class="section-head"><span class="label">Journal</span><h2>Notes from the workbench.</h2></div>
{listing}</section>"""
    return chrome(f"Journal — {SITE_NAME}", body, prefix="../", active="journal")


def post_page(post: dict[str, object]) -> str:
    meta = " / ".join(x for x in [str(post.get("date", "")), f"{post['minutes']} min read"] if x)
    body = f"""<section><article class="post"><span class="label">{esc(meta)}</span>
<h1>{esc(post["title"])}</h1>{markdown(str(post["body"]))}</article>
<a class="back" href="../">&larr; All entries</a></section>"""
    return chrome(
        f"{post['title']} — {SITE_NAME}", body, prefix="../../", active="journal",
        description=str(post.get("summary") or post["title"]),
    )


def app_legal_page(app: dict[str, object], kind: str) -> str:
    name = str(app.get("store_name") or app.get("name"))
    contact = str(app["support_contact"])
    if kind == "privacy":
        heading, label = f"{name} privacy policy", "Privacy"
        sections = markdown(str(app.get("privacy_body") or DEFAULT_PRIVACY).replace("{app}", name))
    else:
        heading, label = f"{name} support", "Support"
        sections = markdown(str(app.get("support_body") or DEFAULT_SUPPORT).replace("{app}", name))
    body = f"""<section><article class="post"><span class="label">{esc(label)} / {esc(name)}</span>
<h1>{esc(heading)}</h1>{sections}
<p>Contact: <a href="mailto:{esc(contact)}">{esc(contact)}</a></p></article></section>"""
    return chrome(f"{heading} — {SITE_NAME}", body, prefix="../../../",
                  description=f"{label} information for {name}.")


DEFAULT_PRIVACY = """{app} is designed to keep your data on your device.

## What is collected
Nothing is collected by default. {app} has no account system and no advertising or
analytics SDKs. Any data you create stays in the app's local storage on your device.

## What is shared
Nothing is sold, rented, or shared with third parties.

## Deleting your data
Deleting the app removes all locally stored data. There is no server-side copy to request.

## Children
{app} is not directed at children under 13 and collects no personal information.

## Changes
Material changes to this policy will be published on this page.
"""

DEFAULT_SUPPORT = """Need help with {app}? Email is the fastest route and reaches a real person.

## Reporting a problem
Include your device model, iOS version, and what you expected to happen. Screenshots help.

## Feature requests
Genuinely read and genuinely considered, though not all are built.

## Response time
Usually within a few days.
"""


# --------------------------------------------------------------------------

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    global CSS_V, XP_V
    CSS_V = asset_hash(CSS)
    XP_V = asset_hash(EXPERIENCES)
    products = load_products()
    posts = load_posts()
    apps = load_apps()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write(OUT / ".nojekyll", "")
    write(OUT / "styles.css", CSS)
    write(OUT / "experiences.js", EXPERIENCES)
    if CUSTOM_DOMAIN:
        # Regenerated every build; site/ is wiped each run, so Pages would
        # otherwise lose the custom domain on the next deploy.
        write(OUT / "CNAME", CUSTOM_DOMAIN + "\n")
    write(OUT / "index.html", home(products, posts))
    write(OUT / "journal" / "index.html", journal_index(posts))

    for product in products:
        write(OUT / "products" / str(product["slug"]) / "index.html", product_page(product))
    for post in posts:
        write(OUT / "journal" / str(post["slug"]) / "index.html", post_page(post))

    rendered_apps, skipped = 0, []
    for app in apps:
        contact = app.get("support_contact")
        if not contact or "example.com" in str(contact) or "TODO" in str(contact).upper():
            skipped.append(str(app.get("slug")))
            continue
        base = OUT / "apps" / str(app["slug"])
        write(base / "privacy" / "index.html", app_legal_page(app, "privacy"))
        write(base / "support" / "index.html", app_legal_page(app, "support"))
        rendered_apps += 1

    print(f"generated: catalog + {len(products)} product pages, "
          f"journal + {len(posts)} posts, {rendered_apps} app store page pairs")
    if skipped:
        print(f"SKIPPED app pages (unresolved support_contact): {', '.join(skipped)}")
        print("  -> set data/apps.json support_contact to a real address to publish them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
