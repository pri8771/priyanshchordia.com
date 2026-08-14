#!/usr/bin/env python3
"""Generate the dependency-free public site: catalog, journal, and app store pages.

Visual direction: "Signal Catalog" (design/concepts/signal-catalog.html on the
design-concepts branch). The site is a product catalogue plus a journal — it is
deliberately not a personal/biographical site.

Sources of truth:
  data/registry.public.json  sanitized product projection (never edit by hand)
  data/apps.json             per-app store metadata for privacy/support routes
  data/landing_pages.json    reviewed copy and three design directions per app
  content/posts/*.md         journal posts (front matter + markdown subset)
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "registry.public.json"
APPS = ROOT / "data" / "apps.json"
LANDING_PAGES = ROOT / "data" / "landing_pages.json"
POSTS = ROOT / "content" / "posts"
OUT = ROOT / "site"
ASSETS = ROOT / "assets"
THEMES_DIR = ROOT / "scripts" / "themes"
EXPERIENCES_DIR = ROOT / "scripts" / "experiences"

# Set to the apex domain ONLY after DNS resolves to GitHub Pages. Emitting a
# CNAME file early makes Pages redirect github.io -> the domain, which darks
# the site until propagation completes. None = keep serving on github.io.
CUSTOM_DOMAIN: str | None = "priyanshchordia.com"

SITE_NAME = "priyanshchordia.com"
DESCRIPTION = "Six private, focused iOS apps in beta."
BASE_URL = f"https://{CUSTOM_DOMAIN or 'pri8771.github.io/priyanshchordia.com'}"
CANDIDATE_POLICY_DATE_ISO = "2026-07-29"
CANDIDATE_POLICY_DATE_LABEL = "July 29, 2026"

# Minimal inline favicon (dark rounded square, one dot — echoes the nav's status
# dot) so browser tabs aren't blank. No binary asset file, no external request,
# consistent with the rest of the site.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E"
    "%3Crect%20width='32'%20height='32'%20rx='7'%20fill='%23141414'/%3E"
    "%3Ccircle%20cx='16'%20cy='16'%20r='6'%20fill='%23d7ff4a'/%3E"
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
    parts.append((THEMES_DIR / "finishing.css").read_text(encoding="utf-8"))
    parts.append((THEMES_DIR / "app-landings.css").read_text(encoding="utf-8"))
    parts.append((THEMES_DIR / "landing-system.css").read_text(encoding="utf-8"))
    return "\n".join(parts)

CSS = _load_css()
APP_THEMES_JS = (ROOT / "scripts" / "app-themes.js").read_text(encoding="utf-8")
WAITLIST_JS = (ROOT / "scripts" / "waitlist.js").read_text(encoding="utf-8")


def esc(value: object) -> str:
    return html.escape(str(value or ""))


# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------

def load_products() -> list[dict[str, object]]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = data.get("products", [])
    if not isinstance(products, list):
        raise ValueError("Public registry products must be a list")
    seen: set[str] = set()
    for product in products:
        if not isinstance(product, dict):
            raise ValueError("Every public registry product must be an object")
        slug = str(product.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe product slug: {slug!r}")
        if slug in seen:
            raise ValueError(f"Duplicate product slug: {slug!r}")
        seen.add(slug)
        for field in ("name", "summary", "stage", "portfolio_lane"):
            if not isinstance(product.get(field), str) or not str(product[field]).strip():
                raise ValueError(f"{slug}: missing or invalid {field}")
        if product.get("public_tier") not in {"featured", "lab"}:
            raise ValueError(f"Non-public tier entered public snapshot: {product.get('id')}")
    products.sort(key=lambda p: (p.get("public_tier") != "featured", str(p.get("name", ""))))
    return products


def load_apps(products: list[dict[str, object]]) -> list[dict[str, object]]:
    """Store metadata for App Store privacy/support routes.

    Route generation is explicit. An enabled route must map to one public
    product and provide app-specific privacy copy plus a real support contact.
    Legal approval is separate: unapproved routes are served with ``noindex``
    and omitted from the sitemap. Legal claims never use a generic fallback.
    """
    if not APPS.exists():
        return []
    apps = json.loads(APPS.read_text(encoding="utf-8")).get("apps", [])
    if not isinstance(apps, list):
        raise ValueError("App Store metadata apps must be a list")
    product_slugs = {str(product["slug"]) for product in products}
    seen: set[str] = set()
    seen_registry: set[str] = set()
    for app in apps:
        if not isinstance(app, dict):
            raise ValueError("Every App Store metadata entry must be an object")
        slug = str(app.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe app slug: {slug!r}")
        if slug in RESERVED_ROUTES:
            raise ValueError(f"App slug {slug!r} collides with a reserved top-level route")
        if slug in seen:
            raise ValueError(f"Duplicate app slug: {slug!r}")
        seen.add(slug)
        registry_slug = str(app.get("registry_slug", ""))
        if registry_slug not in product_slugs:
            raise ValueError(f"{slug}: unknown registry_slug {registry_slug!r}")
        if registry_slug in seen_registry:
            raise ValueError(f"Duplicate app registry mapping: {registry_slug!r}")
        seen_registry.add(registry_slug)
        if not str(app.get("name", "")).strip() or not str(app.get("store_name", "")).strip():
            raise ValueError(f"{slug}: missing name or store_name")
        contact = str(app.get("support_contact", ""))
        if contact and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact):
            raise ValueError(f"{slug}: invalid support_contact")
        app_store_id = app.get("app_store_id")
        if app_store_id not in (None, "") and not re.fullmatch(r"\d{9,12}", str(app_store_id)):
            raise ValueError(f"{slug}: invalid App Store ID")
        if not isinstance(app.get("route_enabled"), bool):
            raise ValueError(f"{slug}: route_enabled must be true or false")
        if not isinstance(app.get("legal_approved"), bool):
            raise ValueError(f"{slug}: legal_approved must be true or false")
        if app.get("legal_approved") is True and app.get("route_enabled") is not True:
            raise ValueError(f"{slug}: legal approval requires an enabled route")
        policy_effective_date = app.get("policy_effective_date")
        if policy_effective_date not in (None, ""):
            try:
                date.fromisoformat(str(policy_effective_date))
            except ValueError as exc:
                raise ValueError(f"{slug}: policy_effective_date must be YYYY-MM-DD") from exc
        if app.get("legal_approved") is True and policy_effective_date in (None, ""):
            raise ValueError(f"{slug}: approved legal copy requires policy_effective_date")
        if app.get("route_enabled") is True:
            if not contact or "example.com" in contact or "TODO" in contact.upper():
                raise ValueError(f"{slug}: enabled route has unresolved support_contact")
            privacy_body = app.get("privacy_body")
            if not isinstance(privacy_body, str) or len(privacy_body.strip()) < 200:
                raise ValueError(f"{slug}: enabled route requires an app-specific privacy_body")
    return apps


def load_landing_pages(products: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    """Load reviewed public landing-page copy and exactly three themes per app."""
    payload = json.loads(LANDING_PAGES.read_text(encoding="utf-8"))
    apps = payload.get("apps")
    if not isinstance(apps, dict):
        raise ValueError("Landing-page data must contain an apps object")
    product_slugs = {str(product["slug"]) for product in products}
    if set(apps) != product_slugs:
        missing = sorted(product_slugs - set(apps))
        extra = sorted(set(apps) - product_slugs)
        raise ValueError(f"Landing-page/product mismatch; missing={missing}, extra={extra}")
    seen_themes: set[str] = set()
    required_text = ("eyebrow", "headline", "lede", "audience", "privacy", "limitation", "cta")
    for slug, landing in apps.items():
        if not isinstance(landing, dict):
            raise ValueError(f"{slug}: landing page must be an object")
        for field in required_text:
            if not isinstance(landing.get(field), str) or not str(landing[field]).strip():
                raise ValueError(f"{slug}: missing landing-page field {field}")
        benefits = landing.get("benefits")
        if not isinstance(benefits, list) or len(benefits) != 3:
            raise ValueError(f"{slug}: exactly three benefits are required")
        for benefit in benefits:
            if not isinstance(benefit, dict) or not all(
                isinstance(benefit.get(field), str) and str(benefit[field]).strip()
                for field in ("title", "body")
            ):
                raise ValueError(f"{slug}: invalid benefit")
        steps = landing.get("steps")
        if not isinstance(steps, list) or len(steps) != 3 or not all(
            isinstance(step, str) and step.strip() for step in steps
        ):
            raise ValueError(f"{slug}: exactly three non-empty steps are required")
        themes = landing.get("themes")
        if not isinstance(themes, list) or len(themes) != 3:
            raise ValueError(f"{slug}: exactly three themes are required")
        for theme in themes:
            if not isinstance(theme, dict):
                raise ValueError(f"{slug}: invalid theme")
            theme_id = str(theme.get("id", ""))
            if not re.fullmatch(rf"{re.escape(slug)}-0[1-3]", theme_id):
                raise ValueError(f"{slug}: invalid theme id {theme_id!r}")
            if theme_id in seen_themes:
                raise ValueError(f"Duplicate app theme id: {theme_id}")
            seen_themes.add(theme_id)
            for field in ("name", "principle", "icon"):
                if not isinstance(theme.get(field), str) or not str(theme[field]).strip():
                    raise ValueError(f"{slug}: theme {theme_id} missing {field}")
    return apps


RESERVED_ROUTES = {"products", "journal", "apps", "assets", "static", "index"}


FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


def load_posts() -> list[dict[str, object]]:
    if not POSTS.exists():
        return []
    posts: list[dict[str, object]] = []
    seen: set[str] = set()
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
        if slug in seen:
            raise ValueError(f"{path.name}: duplicate post slug {slug!r}")
        seen.add(slug)
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
    """Render the deliberately small Markdown subset used by public copy.

    Headings are line-delimited rather than blank-block-delimited. This matters
    for legal documents: a heading followed immediately by a paragraph must
    never turn the paragraph into heading text.
    """
    blocks: list[str] = []
    paragraph: list[str] = []
    items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if items:
            blocks.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for raw_line in body.strip().splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_list()
        elif line.startswith(("## ", "# ")):
            flush_paragraph()
            flush_list()
            heading = line[3:] if line.startswith("## ") else line[2:]
            blocks.append(f"<h2>{inline(heading.strip())}</h2>")
        elif line.startswith(("- ", "* ")):
            flush_paragraph()
            items.append(line[2:].strip())
        else:
            flush_list()
            paragraph.append(line)
    flush_paragraph()
    flush_list()
    return "".join(blocks)


def safe_script_json(value: object) -> str:
    """JSON safe to embed in an HTML script element.

    Escaping the HTML-significant characters prevents a registry value
    containing ``</script>`` from ending the payload and creating executable
    markup. The Unicode separators are escaped for older JavaScript parsers.
    """
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


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
APP_THEME_V = ""


DEFAULT_THEME = "unknown-signal"


def options_html() -> str:
    return "".join(
        f'<option value="{k}"{" selected" if k == DEFAULT_THEME else ""}>{v}</option>'
        for k, v in THEMES
    )


def canonical_url(path: str) -> str:
    normalized = "/" + path.strip("/")
    if normalized != "/" and "." not in normalized.rsplit("/", 1)[-1]:
        normalized += "/"
    return BASE_URL + normalized


def chrome(title: str, body: str, prefix: str = "", active: str = "",
           description: str = DESCRIPTION, extra: str = "", path: str = "/",
           fixed_theme: str | None = None, robots: str = "index,follow",
           structured_data: object | None = None, body_class: str = "") -> str:
    def nav_attrs(name: str) -> str:
        return ' class="active" aria-current="page"' if active == name else ""

    options = options_html()
    theme = fixed_theme or DEFAULT_THEME
    allowed = safe_script_json([slug for slug, _name in THEMES])
    if fixed_theme:
        preload = ""
        switcher = ""
        theme_control = ""
    else:
        # Applied in <head> so a valid stored theme paints on the first frame.
        preload = (
            "<script>(function(){var a=" + allowed + ";try{var t=localStorage.getItem('pc-theme');"
            "if(a.indexOf(t)>=0)document.documentElement.setAttribute('data-theme',t);"
            "else if(t)localStorage.removeItem('pc-theme')}catch(e){}})()</script>"
        )
        switcher = (
            "<script>(function(){var a=" + allowed + ",ss=[].slice.call(document.querySelectorAll('.themer'));"
            "if(!ss.length)return;try{var t=localStorage.getItem('pc-theme');"
            "if(a.indexOf(t)>=0)ss.forEach(function(s){s.value=t})}catch(e){}"
            "ss.forEach(function(s){s.addEventListener('change',function(){var v=s.value;"
            "if(a.indexOf(v)<0)return;document.documentElement.setAttribute('data-theme',v);"
            "ss.forEach(function(o){o.value=v});try{localStorage.setItem('pc-theme',v)}catch(e){}"
            "requestAnimationFrame(function(){var xp=document.documentElement.classList.contains('has-xp');"
            "var target=document.querySelector(xp?'#themer2':'#themer');"
            "if(target&&target!==document.activeElement)target.focus()})})})})()</script>"
        )
        theme_control = f'<select id="themer" class="themer" aria-label="Site design">{options}</select>'

    url = canonical_url(path)
    social_asset = "og-five-apps.png"
    social_alt = "Five apps, fifteen directions: abstract marks for Mala, Anjali, Svara, Roam, and Hindsight."
    social_image = (
        f'<meta property="og:image" content="{BASE_URL}/{social_asset}">'
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="630">'
        f'<meta property="og:image:alt" content="{esc(social_alt)}">'
        f'<meta name="twitter:image" content="{BASE_URL}/{social_asset}">'
        f'<meta name="twitter:image:alt" content="{esc(social_alt)}">'
        if (ASSETS / social_asset).exists() else ""
    )
    json_ld = (
        f'<script type="application/ld+json">{safe_script_json(structured_data)}</script>'
        if structured_data is not None else ""
    )
    body_attr = f' class="{esc(body_class)}"' if body_class else ""
    return f"""<!doctype html>
<html lang="en" data-theme="{theme}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description)}"><meta name="robots" content="{esc(robots)}">
<meta name="color-scheme" content="dark light"><meta name="theme-color" content="#0a0806">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">{social_image}
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<title>{esc(title)}</title>{preload}<link rel="icon" href="{FAVICON}" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}styles.css?v={CSS_V}"></head>
<body{body_attr}><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><div class="left">
{theme_control}
<a class="brand" href="{prefix}index.html">P/C <span class="status" aria-hidden="true">&#9679;</span></a></div>
<nav aria-label="Primary"><a{nav_attrs('work')} href="{prefix}index.html#work">Work</a><a{nav_attrs('apps')} href="{prefix}apps/">App URLs</a><a{nav_attrs('journal')} href="{prefix}journal/">Journal</a></nav></header>
<main id="main">{body}</main>
<footer><span>{esc(SITE_NAME)}</span><span>Independent software, built with privacy in mind.</span></footer>
</div>{extra}{switcher}{json_ld}</body></html>"""


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
        journal = '<p class="empty">Writing will appear here as it is published.</p>'
    body = f"""<section class="hero"><div><div class="kicker">Independent software / live index</div>
<h1>Useful<br>signals.</h1></div>
<p class="lede">{len(products)} independent iOS apps in private beta &mdash; private, focused, and built for everyday use.</p></section>
<section id="work"><div class="section-head"><span class="label">01 / Catalog</span><h2>Everything transmitting.</h2></div>
<div class="products">{tiles}</div></section>
<section id="journal"><div class="section-head"><span class="label">02 / Journal</span><h2>Notes from the workbench.</h2></div>
{journal}</section>"""
    payload = safe_script_json([
        {"name": p["name"], "summary": p["summary"], "href": f"products/{p['slug']}/",
         "lane": str(p.get("portfolio_lane", "")).replace("-", " ")}
        for p in products
    ])
    extra = (
        '<select id="themer2" class="themer xp-switch" aria-label="Design">' + options_html() + "</select>"
        '<div id="xp" class="xp"></div>'
        f'<script>window.__PRODUCTS={payload}</script>'
        f'<script src="experiences.js?v={XP_V}" defer></script>'
    )
    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": BASE_URL + "/",
        "description": DESCRIPTION,
    }
    return chrome(
        f"{SITE_NAME} — software catalogue", body, active="work", extra=extra,
        path="/", structured_data=structured_data,
    )


def landing_scene(theme: dict[str, object], active: bool) -> str:
    theme_id = str(theme["id"])
    hidden = "" if active else " hidden"
    return f"""<div class="app-scene scene-{esc(theme_id)}" data-app-scene="{esc(theme_id)}"{hidden}
aria-label="{esc(theme['name'])} visual concept">
<span class="scene-label">{esc(theme['name'])}</span>
<span class="scene-shape shape-a"></span><span class="scene-shape shape-b"></span>
<span class="scene-shape shape-c"></span><span class="scene-shape shape-d"></span>
<span class="scene-line line-a"></span><span class="scene-line line-b"></span>
<span class="scene-line line-c"></span><span class="scene-line line-d"></span>
<span class="scene-dot dot-a"></span><span class="scene-dot dot-b"></span>
<span class="scene-dot dot-c"></span><span class="scene-dot dot-d"></span>
<span class="scene-icon" aria-label="Icon direction: {esc(theme['icon'])}"><i></i><b></b></span>
</div>"""


def product_page(product: dict[str, object], landing: dict[str, object],
                 app: dict[str, object] | None = None) -> str:
    slug = str(product["slug"])
    name = str(product["name"])
    lane = str(product.get("portfolio_lane", "software")).replace("-", " ")
    subject = quote(f"{name} beta")
    system = {
        "mala": {
            "positioning": "A quiet digital mala.",
            "hero": "Keep your place. Feel each count. Finish without looking. One tap advances one bead — and the count survives a phone call, a locked screen, or the rest of the day.",
            "shots": "Five screens. That is the whole app.",
            "benefits": "Three things a physical mala already does well.",
            "steps": "Four steps, then you can put the screen away.",
            "trust": "There is no server to send anything to.",
            "fit": "Useful to a few people. Not to everyone.",
            "faq": "What Mala does, and what it will not do.",
            "features": ["Choose a round size", "Name it, or don't", "Tap to advance", "Finish without looking", "No account or cloud backend", "TestFlight builds expire"],
        },
        "anjali": {
            "positioning": "A sacred pause, not a session.",
            "hero": "One short prayer for the moment you are in — with the Devanagari, a transliteration, and a plain-English meaning on the same screen. Then you close the app.",
            "shots": "One prayer, held on one screen.",
            "benefits": "Built to be closed after the prayer.",
            "steps": "Three steps, then put it down.",
            "trust": "A prayer is not an event to be logged.",
            "fit": "A small app for a small moment.",
            "faq": "Asked, and answered honestly.",
            "features": ["Short on purpose", "Read it three ways", "Browse by moment", "Chant or silent", "Offline and accountless", "No recorded audio"],
        },
        "svara": {
            "positioning": "Practice. Learn. Return.",
            "hero": "A private daily companion for spiritual practice and cultural reconnection: short guided practices, an ordered learning path called Aaroh, and the stories behind what you already do.",
            "shots": "Something to do today, and somewhere it leads.",
            "benefits": "Rooted, private, and possible on a normal day.",
            "steps": "Four steps you will repeat.",
            "trust": "Local-first, and made by one person.",
            "fit": "Especially useful if you are finding your way back.",
            "faq": "What Svara claims, and what it does not.",
            "features": ["Start with today", "Follow Aaroh at your pace", "Read the why", "Return when ready", "No social feed", "Everything free while testing"],
        },
        "roam": {
            "positioning": "Your travels, coloured in.",
            "hero": "A private map of the places you have explored. Switch tracking on and Roam fills in supported U.S. Census ZIP Code Areas as you move. Anywhere else in the world, add countries and cities by hand.",
            "shots": "The same map, at six levels of zoom.",
            "benefits": "Detailed enough to be interesting. Private enough to keep.",
            "steps": "Four steps, and one of them is optional.",
            "trust": "Location history is the most sensitive data you own.",
            "fit": "Map people, mostly.",
            "faq": "The precise answers.",
            "features": ["Decide about tracking", "Travel", "Add the rest by hand", "Keep control of it", "Export and delete", "Synthetic map data in the preview"],
        },
        "aurafit": {
            "positioning": "An outfit check that stays on your phone.",
            "hero": "Capture or import a full-body photo and get a Fit Score for outfit, colour, pose, lighting, framing, and background — computed entirely on your iPhone. The photo never leaves the device.",
            "shots": "Scan, score, share if you want.",
            "benefits": "Honest feedback, with nobody else looking.",
            "steps": "Three steps before you head out.",
            "trust": "Your mirror photos are yours alone.",
            "fit": "For people who check the fit before they leave.",
            "faq": "What the score is, and what it is not.",
            "features": ["Scan a full-body photo", "Read the weighted Fit Score", "Follow concrete tips", "Keep a private history", "On-device analysis only", "Share only what you export"],
        },
        "hindsight": {
            "positioning": "Make the decision. Remember the reasoning.",
            "hero": "A private journal for learning how you decide. Write down what you believed and how sure you were — then come back when reality has answered, and grade the outcome and the process separately.",
            "shots": "Capture, wait, review.",
            "benefits": "Hindsight is only useful if it is honest.",
            "steps": "Four steps, spread over months.",
            "trust": "You will only be honest in it if nobody else can read it.",
            "fit": "People willing to be wrong on the record.",
            "faq": "What Build 1 is, and is not.",
            "features": ["Write the decision down", "Commit to a prediction", "Set a review date", "Review without flinching", "Insights stay on device", "Export and full deletion"],
        },
    }[slug]
    positioning = system["positioning"]
    hero_body = system["hero"]
    shots_heading = system["shots"]
    benefits_heading = system["benefits"]
    steps_heading = system["steps"]
    trust_heading = system["trust"]
    fit_heading = system["fit"]
    faq_heading = system["faq"]
    benefits = "".join(f'<article><span>{index + 1:02d}</span><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></article>' for index, item in enumerate(landing["benefits"]))
    steps = "".join(f'<li><span>{index + 1:02d}</span><p>{esc(item)}</p></li>' for index, item in enumerate(landing["steps"]))
    captions = {
        "mala": ["Practice surface", "Round complete", "Personal label", "Mala styles", "History"],
        "anjali": ["Prayer detail", "Browse by moment", "Chant or silent"],
        "svara": ["Today", "Aaroh path", "A practice", "Stories"],
        "roam": ["Coverage map", "Location choice", "Saved places", "Export summary"],
        "hindsight": ["New prediction", "Sealed entry", "Outcome review", "Reflection"],
        "aurafit": ["Scan", "Fit Score", "Coaching tips", "History"],
    }[slug]
    shot_files = {
        "mala": ["01-practice.png", "02-completion.png", "03-label.png", "04-style.png", "05-history.png"],
        "anjali": ["01-prayer.png", "02-moment.png", "03-chant.png"],
        "svara": ["01-today.png", "02-aaroh.png", "03-practice.png", "04-story.png"],
        "roam": ["01-map.png", "02-zcta.png", "03-places.png", "04-progress.png", "05-controls.png"],
        "hindsight": ["01-capture.png", "02-confidence.png", "03-review.png", "04-insights.png", "05-export.png"],
        "aurafit": ["01-scan.png", "02-score.png", "03-tips.png", "04-history.png"],
    }[slug]
    shot_parts = []
    for caption, filename in zip(captions, shot_files):
        asset = ASSETS / "apps" / slug / "shots" / filename
        image = (
            f'<img src="../../assets/apps/{esc(slug)}/shots/{esc(filename)}" '
            f'alt="{esc(caption)} in {esc(name)}" loading="lazy">'
            if asset.exists() else ""
        )
        placeholder = "" if image else "<span>Screenshot pending</span>"
        shot_parts.append(
            f'<figure><div class="product-shot" aria-label="{esc(caption)} screenshot placeholder">'
            f'{image}{placeholder}</div><figcaption>{esc(caption)}</figcaption></figure>'
        )
    shots = "".join(shot_parts)
    features = "".join(
        f'<div><dt>{esc(feature)}</dt><dd>{index + 1:02d}</dd></div>'
        for index, feature in enumerate(system["features"])
    )
    legal = (f'<a href="../../apps/{esc(app["slug"])}/privacy/">Privacy notice</a><a href="../../apps/{esc(app["slug"])}/support/">Support</a>' if app and app.get("route_enabled") is True else '<a href="mailto:support@priyanshchordia.com">Support</a>')
    body = f"""<article class="product-system product-system--{esc(slug)}" data-app="{esc(slug)}">
<header class="product-nav"><a class="product-wordmark" href="../../index.html">Priyansh Chordia <span>· iOS</span></a><nav aria-label="Product"><a href="../../index.html#work">Products</a><a href="#top">{esc(name)}</a><a href="#waitlist">Join waitlist</a></nav></header>
<div id="top"><section class="product-hero"><div><p class="product-kicker">{esc(name)}</p><h1>{esc(positioning)}</h1><p class="product-hero-body">{esc(hero_body)}</p><p class="product-hero-note">In TestFlight beta — not on the App Store yet. {esc(landing['privacy'])}</p><div class="product-actions"><a class="product-button" href="#waitlist">Join the waitlist</a><a href="#how-it-works">See how it works <span aria-hidden="true">↓</span></a></div></div><div class="product-motif" aria-hidden="true"><span></span><i></i><b></b></div></section>
<section class="product-shots"><div class="product-section-heading"><p>The app</p><h2>{esc(shots_heading)}</h2></div><div class="product-shots-grid">{shots}</div></section>
<section class="product-benefits"><div class="product-section-heading"><p>Why it exists</p><h2>{esc(benefits_heading)}</h2></div><div class="product-triad">{benefits}</div></section>
<section id="how-it-works" class="product-steps"><div class="product-section-heading"><p>How it works</p><h2>{esc(steps_heading)}</h2></div><ol>{steps}</ol></section>
<section class="product-trust"><div><p>Privacy and trust</p><h2>{esc(trust_heading)}</h2><p>{esc(landing['privacy'])}</p><div class="product-legal-links">{legal}</div></div><aside><p>Honest boundary</p><strong>{esc(landing['limitation'])}</strong></aside></section>
<section class="product-features"><div class="product-section-heading"><p>Feature highlights</p><h2>Everything in the beta build.</h2></div><dl>{features}</dl></section>
<section class="product-fit"><div class="product-section-heading"><p>Who the beta is for</p><h2>{esc(fit_heading)}</h2></div><div><article><h3>A good fit if you</h3><p>{esc(landing['audience'])}</p></article><article><h3>{esc(name)} is deliberately not</h3><p>{esc(landing['limitation'])}</p></article></div></section>
<section id="waitlist" class="product-waitlist"><div><p>Waitlist</p><h2>Ask for a TestFlight invitation.</h2><p>No account is created. Your email is stored only to send {esc(name)} beta invitations.</p></div><form data-waitlist data-app-name="{esc(name)}" action="mailto:support@priyanshchordia.com?subject={subject}" method="post"><label>Email address <em>(required)</em><input type="email" name="email" autocomplete="email" placeholder="you@example.com" required></label><label>First name <em>(optional)</em><input type="text" name="first_name" autocomplete="given-name"></label><label>Device and iOS version, or what you want to test <em>(optional)</em><textarea name="device" aria-describedby="device-hint"></textarea><small id="device-hint">Helps prioritise invitations across devices. Leave blank if you would rather not say.</small></label><label class="product-consent"><input type="checkbox" name="consent" required> Email me about TestFlight access and occasional updates for {esc(name)}. I can unsubscribe at any time.</label><button class="product-button" type="submit">Join the {esc(name)} waitlist</button><p class="waitlist-status" role="status" aria-live="polite" tabindex="-1"></p><p class="waitlist-fallback">The signup service is not connected yet. Email <a href="mailto:support@priyanshchordia.com?subject={subject}">support@priyanshchordia.com</a> with the subject “{esc(name)} beta” and you will be added by hand.</p></form></section>
<section class="product-faq"><div class="product-section-heading"><p>Questions and limits</p><h2>{esc(faq_heading)}</h2></div><details><summary>Can I download {esc(name)} from the App Store?</summary><p>No. {esc(name)} is in TestFlight beta and is not available on the App Store yet.</p></details><details><summary>How soon will I get an invitation?</summary><p>Invitations are sent in small groups as testing capacity opens. There is no queue position or promised timeline.</p></details><details><summary>What do you do with my email address?</summary><p>It is used only to send beta invitations and occasional updates. You can ask to be removed at any time.</p></details><div class="product-limits"><p>Honest limitations</p><strong>{esc(landing['limitation'])}</strong></div></section>
<footer class="product-footer"><p>More from this portfolio</p><h2>Independent iOS apps, built one at a time.</h2><div>{legal}<a href="../../index.html#work">All products</a><a href="mailto:support@priyanshchordia.com">support@priyanshchordia.com</a></div><small>© 2026 Priyansh Chordia. {esc(name)} is in TestFlight beta and is not available on the App Store.</small></footer></div></article>"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": str(product["name"]),
        "description": str(product["summary"]),
        "url": canonical_url(f"/products/{product['slug']}/"),
        "applicationCategory": lane.title(),
        "operatingSystem": "iOS" if app else "Not specified",
    }
    return chrome(
        f"{product['name']} — {SITE_NAME}", body, prefix="../../", active="work",
        description=str(product.get("summary", DESCRIPTION)),
        path=f"/products/{product['slug']}/", structured_data=structured_data,
        fixed_theme="signal", body_class="product-page",
        extra=f'<script src="../../waitlist.js?v={asset_hash(WAITLIST_JS)}" defer></script>',
    )


def journal_index(posts: list[dict[str, object]]) -> str:
    if posts:
        rows = "".join(entry_row(p, i + 1, "../") for i, p in enumerate(posts))
        listing = f'<div class="journal-index">{rows}</div>'
    else:
        listing = '<p class="empty">No entries published yet. Check back for notes from the workbench.</p>'
    body = f"""<section><div class="section-head"><span class="label">Journal</span><h1>Notes from the workbench.</h1></div>
{listing}</section>"""
    return chrome(
        f"Journal — {SITE_NAME}", body, prefix="../", active="journal",
        path="/journal/", description="Notes on independent software, product craft, and the work behind the catalogue.",
    )


def post_page(post: dict[str, object]) -> str:
    meta = " / ".join(x for x in [str(post.get("date", "")), f"{post['minutes']} min read"] if x)
    body = f"""<section><article class="post"><span class="label">{esc(meta)}</span>
<h1>{esc(post["title"])}</h1>{markdown(str(post["body"]))}</article>
<a class="back" href="../">&larr; All entries</a></section>"""
    return chrome(
        f"{post['title']} — {SITE_NAME}", body, prefix="../../", active="journal",
        description=str(post.get("summary") or post["title"]),
        path=f"/journal/{post['slug']}/",
    )


def apps_index(apps: list[dict[str, object]]) -> str:
    enabled = [app for app in apps if app.get("route_enabled") is True]
    cards_list: list[str] = []
    for app in enabled:
        app_store_id = app.get("app_store_id")
        if app_store_id:
            status = "iOS / available"
            summary = "Public privacy, support, and App Store download destinations."
            store_link = (
                f'<a class="resource-link" href="https://apps.apple.com/app/id{esc(app_store_id)}" '
                'rel="external">App Store</a>'
            )
        else:
            status = "iOS / in development"
            summary = (
                "Public pages prepared for App Store Connect. "
                "No public App Store listing is available yet."
            )
            store_link = ""
        cards_list.append(
            f"""<article class="app-card"><span class="label">{esc(status)}</span>
<h2>{esc(app.get("store_name") or app.get("name"))}</h2>
<p>{esc(summary)}</p>
<div class="resource-links"><a class="resource-link" href="{esc(app['slug'])}/privacy/">Privacy policy</a>
<a class="resource-link" href="{esc(app['slug'])}/support/">Support</a>{store_link}</div></article>"""
        )
    cards = "".join(cards_list)
    body = f"""<section><div class="section-head"><span class="label">App Store resources</span>
<h1>Public app URLs.</h1></div>
<p class="directory-lede">Privacy and support destinations for App Store submissions. These are
public web pages, not App Store download links; listings appear only after Apple release.</p>
<div class="app-directory">{cards}</div></section>"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "App Store resources",
        "url": BASE_URL + "/apps/",
        "hasPart": [
            {"@type": "WebPage", "name": str(app.get("store_name") or app.get("name")),
             "url": canonical_url(f"/apps/{app['slug']}/privacy/")}
            for app in enabled if app.get("legal_approved") is True
        ],
    }
    return chrome(
        f"App Store resources — {SITE_NAME}", body, prefix="../", active="apps",
        path="/apps/", description="Privacy and support URLs for iOS apps in the catalogue.",
        structured_data=structured_data,
    )


def app_legal_page(app: dict[str, object], kind: str) -> str:
    name = str(app.get("store_name") or app.get("name"))
    contact = str(app["support_contact"])
    effective_date = app.get("policy_effective_date")
    if effective_date:
        parsed_date = date.fromisoformat(str(effective_date))
        date_label = f"Effective {parsed_date.strftime('%B')} {parsed_date.day}, {parsed_date.year}"
        date_modified = str(effective_date)
    else:
        date_label = f"Draft updated {CANDIDATE_POLICY_DATE_LABEL}"
        date_modified = CANDIDATE_POLICY_DATE_ISO
    if kind == "privacy":
        heading, label = f"{name} privacy policy", "Privacy"
        sections = markdown(str(app["privacy_body"]).replace("{app}", name))
    else:
        heading, label = f"{name} support", "Support"
        sections = markdown(str(app.get("support_body") or DEFAULT_SUPPORT).replace("{app}", name))
    slug = str(app["slug"])
    body = f"""<section><article class="post legal"><span class="label">{esc(label)} / {esc(name)}</span>
<h1>{esc(heading)}</h1><p class="policy-date">{esc(date_label)}</p>{sections}
<h2>Contact</h2><p>Email <a href="mailto:{esc(contact)}">{esc(contact)}</a> for support or privacy questions.</p>
<nav class="resource-links" aria-label="{esc(name)} legal pages">
<a class="resource-link" href="../privacy/">Privacy policy</a>
<a class="resource-link" href="../support/">Support</a>
<a class="resource-link" href="../../">All app URLs</a></nav></article></section>"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": heading,
        "url": canonical_url(f"/apps/{slug}/{kind}/"),
        "dateModified": date_modified,
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": BASE_URL + "/"},
    }
    return chrome(
        f"{heading} — {SITE_NAME}", body, prefix="../../../", active="apps",
        description=f"{label} information for {name}.", path=f"/apps/{slug}/{kind}/",
        fixed_theme="signal",
        robots="index,follow" if app.get("legal_approved") is True else "noindex,follow",
        structured_data=structured_data,
    )

DEFAULT_SUPPORT = """Need help with {app}? Use the email address below.

## Reporting a problem
Include your device model, iOS version, and what you expected to happen. Screenshots help.

## Feature requests
Feature suggestions are welcome. Not every request can be built.

## Protect your privacy
Do not include passwords, payment information, precise location history, private notes, or other sensitive data in a support message.
"""


# --------------------------------------------------------------------------

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def not_found_page() -> str:
    body = """<section><article class="detail"><span class="label">404 / not found</span>
<h1>Signal lost.</h1><p>The page you requested is not in the public catalogue.</p>
<div class="resource-links"><a class="resource-link" href="/index.html">Browse the catalogue</a>
<a class="resource-link" href="/apps/">App URLs</a></div></article></section>"""
    return chrome(
        f"Page not found — {SITE_NAME}", body, prefix="/", path="/404.html",
        description="The requested page was not found.", fixed_theme="signal",
        robots="noindex,follow",
    )


def sitemap(products: list[dict[str, object]], posts: list[dict[str, object]],
            apps: list[dict[str, object]]) -> str:
    paths = ["/", "/journal/", "/apps/"]
    paths.extend(f"/products/{product['slug']}/" for product in products)
    paths.extend(f"/journal/{post['slug']}/" for post in posts)
    for app in apps:
        if app.get("legal_approved") is True:
            paths.extend((f"/apps/{app['slug']}/privacy/", f"/apps/{app['slug']}/support/"))
    urls = "".join(f"<url><loc>{esc(canonical_url(path))}</loc></url>" for path in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'


def main() -> int:
    global CSS_V, XP_V, APP_THEME_V
    CSS_V = asset_hash(CSS)
    XP_V = asset_hash(EXPERIENCES)
    APP_THEME_V = asset_hash(APP_THEMES_JS)
    products = load_products()
    landing_pages = load_landing_pages(products)
    posts = load_posts()
    apps = load_apps(products)
    enabled_apps = [app for app in apps if app.get("route_enabled") is True]
    apps_by_registry = {str(app["registry_slug"]): app for app in apps}

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write(OUT / ".nojekyll", "")
    write(OUT / "styles.css", CSS)
    write(OUT / "experiences.js", EXPERIENCES)
    write(OUT / "app-themes.js", APP_THEMES_JS)
    write(OUT / "waitlist.js", WAITLIST_JS)
    if CUSTOM_DOMAIN:
        # Regenerated every build; site/ is wiped each run, so Pages would
        # otherwise lose the custom domain on the next deploy.
        write(OUT / "CNAME", CUSTOM_DOMAIN + "\n")
    write(OUT / "index.html", home(products, posts))
    write(OUT / "journal" / "index.html", journal_index(posts))
    write(OUT / "apps" / "index.html", apps_index(apps))
    write(OUT / "404.html", not_found_page())
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    write(OUT / "sitemap.xml", sitemap(products, posts, apps))

    for product in products:
        app = apps_by_registry.get(str(product["slug"]))
        write(
            OUT / "products" / str(product["slug"]) / "index.html",
            product_page(product, landing_pages[str(product["slug"])], app),
        )
    for post in posts:
        write(OUT / "journal" / str(post["slug"]) / "index.html", post_page(post))

    for app in enabled_apps:
        base = OUT / "apps" / str(app["slug"])
        write(base / "privacy" / "index.html", app_legal_page(app, "privacy"))
        write(base / "support" / "index.html", app_legal_page(app, "support"))

    if ASSETS.exists():
        for source in ASSETS.rglob("*"):
            if source.is_symlink():
                raise ValueError(f"Asset symlinks are not allowed: {source.relative_to(ASSETS)}")
            if source.is_file():
                destination = OUT / source.relative_to(ASSETS)
                if destination.exists():
                    raise ValueError(
                        f"Asset collides with a generated route: {source.relative_to(ASSETS)}"
                    )
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

    print(f"generated: catalog + {len(products)} product pages, "
          f"journal + {len(posts)} posts, {len(enabled_apps)} app store page pairs")
    disabled = [str(app["slug"]) for app in apps if app.get("route_enabled") is not True]
    if disabled:
        print(f"routes withheld: {', '.join(disabled)}")
    pending_review = [str(app["slug"]) for app in enabled_apps if app.get("legal_approved") is not True]
    if pending_review:
        print(f"legal review pending (noindex): {', '.join(pending_review)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
