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

SITE_NAME = "priyanshchordia.com"
DESCRIPTION = "A catalogue of independent software — games, private utilities, and tools for clearer work."

CSS = """
:root{--bg:#070908;--panel:#0d110f;--ink:#e9fff1;--muted:#83a28e;--line:#1d3024;--acid:#a7ff8a;--amber:#f5be65}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
a{color:inherit}.wrap{width:min(1380px,calc(100% - 32px));margin:auto}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;padding:10px 14px;background:var(--acid);color:#071008;z-index:9}
.top{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:24px;padding:18px 0;background:rgba(7,9,8,.92);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}
.brand{font-weight:800;letter-spacing:.12em;text-decoration:none}.status{color:var(--acid)}
nav{display:flex;gap:18px}nav a{color:var(--muted);text-decoration:none}nav a:hover,nav a:focus,nav a.active{color:var(--ink)}
.hero{min-height:72vh;display:grid;grid-template-columns:1.5fr .5fr;align-items:end;gap:40px;padding:9vw 0 48px;border-bottom:1px solid var(--line)}
.kicker,.label{color:var(--acid);font-size:12px;letter-spacing:.15em;text-transform:uppercase}
h1{max-width:950px;margin:16px 0 0;font:700 clamp(64px,12vw,176px)/.78 Arial,sans-serif;letter-spacing:-.075em}
.hero p{max-width:32ch;color:var(--muted);line-height:1.6}
section{padding:80px 0;border-bottom:1px solid var(--line)}
.section-head{display:grid;grid-template-columns:180px 1fr;gap:24px;margin-bottom:36px}
.section-head h2{margin:0;font:700 clamp(38px,6vw,78px)/.95 Arial,sans-serif;letter-spacing:-.05em}
.products{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}
.product{min-height:230px;padding:22px;display:flex;flex-direction:column;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--panel);text-decoration:none;transition:background .2s ease,color .2s ease}
.product:hover,.product:focus{background:var(--acid);color:#071008}.product:hover .meta,.product:focus .meta{color:#17361c}.product:hover p,.product:focus p{color:#1c3b22}
.num{font-size:11px;color:var(--acid)}.product h3{margin:auto 0 14px;font:700 28px/1 Arial,sans-serif;letter-spacing:-.04em}
.product p{margin:0;color:var(--muted);font:13px/1.5 Arial,sans-serif}
.meta{margin-top:16px;color:var(--amber);font-size:10px;text-transform:uppercase}
.journal-index{border-top:1px solid var(--line)}
.entry{display:grid;grid-template-columns:90px 1fr auto;gap:16px;padding:20px 0;border-bottom:1px solid var(--line);text-decoration:none;align-items:baseline}
.entry span{color:var(--muted);font-size:12px}.entry strong{font:700 17px/1.3 Arial,sans-serif}.entry:hover strong,.entry:focus strong{color:var(--acid)}
.post,.detail{padding:clamp(28px,5vw,72px);background:var(--panel);border:1px solid var(--line)}
.post h1,.detail h1{margin:14px 0 24px;font:700 clamp(36px,5vw,68px)/.95 Arial,sans-serif;letter-spacing:-.05em;max-width:20ch}
.post h2{margin:36px 0 12px;font:700 clamp(22px,3vw,30px)/1.2 Arial,sans-serif;letter-spacing:-.03em}
.post p,.post li{max-width:65ch;color:#b8c8bd;line-height:1.75;font-family:Arial,sans-serif}
.post code{background:#0a0f0c;border:1px solid var(--line);padding:1px 5px}
.post a,.detail a{color:var(--acid)}
.facts{display:grid;grid-template-columns:repeat(2,1fr);margin-top:36px;border-top:1px solid var(--line)}
.fact{padding:18px 0;border-bottom:1px solid var(--line)}.fact small{display:block;color:var(--muted);margin-bottom:8px}
.empty{padding:42px;border:1px dashed var(--line);background:var(--panel);color:var(--muted)}
.back{display:inline-block;margin-top:42px;color:var(--muted)}
footer{display:flex;justify-content:space-between;gap:16px;padding:28px 0;color:var(--muted);font-size:11px;text-transform:uppercase}
@media(max-width:900px){.products{grid-template-columns:repeat(2,1fr)}.hero{grid-template-columns:1fr}.section-head{grid-template-columns:1fr}.hero p{max-width:60ch}.facts{grid-template-columns:1fr}}
@media(max-width:560px){.wrap{width:min(100% - 20px,1380px)}.top{align-items:flex-start}.status{display:none}nav{gap:10px;font-size:12px}.hero{min-height:64vh;padding-top:90px}.products{grid-template-columns:1fr}.product{min-height:190px}.entry{grid-template-columns:58px 1fr}.entry span:last-child{display:none}footer{flex-direction:column}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.product{transition:none}}
"""


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
    for app in apps:
        if not re.fullmatch(r"[a-z0-9-]+", str(app.get("slug", ""))):
            raise ValueError(f"Unsafe app slug: {app.get('slug')!r}")
    return apps


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

def chrome(title: str, body: str, prefix: str = "", active: str = "", description: str = DESCRIPTION) -> str:
    def cls(name: str) -> str:
        return ' class="active"' if active == name else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)}</title><style>{CSS}</style></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><a class="brand" href="{prefix}index.html">P/C <span class="status" aria-hidden="true">&#9679;</span></a>
<nav aria-label="Primary"><a{cls('work')} href="{prefix}index.html#work">Work</a><a{cls('journal')} href="{prefix}journal/">Journal</a></nav></header>
<main id="main">{body}</main>
<footer><span>{esc(SITE_NAME)}</span><span>Generated from a sanitized public registry</span></footer>
</div></body></html>"""


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
    return chrome(f"{SITE_NAME} — software catalogue", body, active="work")


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
    products = load_products()
    posts = load_posts()
    apps = load_apps()

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write(OUT / ".nojekyll", "")
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
