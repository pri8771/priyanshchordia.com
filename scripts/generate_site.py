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

# Set to the apex domain ONLY after DNS resolves to GitHub Pages. Emitting a
# CNAME file early makes Pages redirect github.io -> the domain, which darks
# the site until propagation completes. None = keep serving on github.io.
CUSTOM_DOMAIN: str | None = "priyanshchordia.com"

SITE_NAME = "priyanshchordia.com"
DESCRIPTION = "A catalogue of independent software — games, private utilities, and tools for clearer work."

CSS = """
/* ---- base: structural only. Every theme below is a COMPLETE design. ---- */
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0}a{color:inherit}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;padding:10px 14px;background:#000;color:#fff;z-index:99}
.themer{font:inherit;font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:6px 8px;cursor:pointer;background:transparent;color:inherit;border:1px solid currentColor}
.left{display:flex;align-items:center;gap:14px}
img{max-width:100%}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}

/* ================= SIGNAL CATALOG — mono transmission index ================= */
[data-theme="signal"]{--bg:#070908;--panel:#0d110f;--ink:#e9fff1;--muted:#83a28e;--line:#1d3024;--acc:#a7ff8a;--on:#071008}
[data-theme="signal"] body{background:var(--bg);color:var(--ink);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
[data-theme="signal"] .wrap{width:min(1380px,calc(100% - 32px));margin:auto}
[data-theme="signal"] .top{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:24px;padding:18px 0;background:rgba(7,9,8,.92);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}
[data-theme="signal"] .brand{font-weight:800;letter-spacing:.12em;text-decoration:none}
[data-theme="signal"] .status{color:var(--acc)}
[data-theme="signal"] nav{display:flex;gap:18px}[data-theme="signal"] nav a{color:var(--muted);text-decoration:none}
[data-theme="signal"] nav a:hover,[data-theme="signal"] nav a.active{color:var(--ink)}
[data-theme="signal"] .hero{min-height:72vh;display:grid;grid-template-columns:1.5fr .5fr;align-items:end;gap:40px;padding:9vw 0 48px;border-bottom:1px solid var(--line)}
[data-theme="signal"] .kicker,[data-theme="signal"] .label{color:var(--acc);font-size:12px;letter-spacing:.15em;text-transform:uppercase}
[data-theme="signal"] h1{max-width:950px;margin:16px 0 0;font:700 clamp(64px,12vw,176px)/.78 Arial,sans-serif;letter-spacing:-.075em}
[data-theme="signal"] .lede{max-width:32ch;color:var(--muted);line-height:1.6}
[data-theme="signal"] section{padding:80px 0;border-bottom:1px solid var(--line)}
[data-theme="signal"] .section-head{display:grid;grid-template-columns:180px 1fr;gap:24px;margin-bottom:36px}
[data-theme="signal"] .section-head h2{margin:0;font:700 clamp(38px,6vw,78px)/.95 Arial,sans-serif;letter-spacing:-.05em}
[data-theme="signal"] .products{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line)}
[data-theme="signal"] .product{min-height:230px;padding:22px;display:flex;flex-direction:column;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--panel);text-decoration:none;transition:background .2s}
[data-theme="signal"] .product:hover{background:var(--acc);color:var(--on)}
[data-theme="signal"] .product:hover *{color:var(--on)}
[data-theme="signal"] .num{font-size:11px;color:var(--acc)}
[data-theme="signal"] .product h3{margin:auto 0 14px;font:700 28px/1 Arial,sans-serif;letter-spacing:-.04em}
[data-theme="signal"] .product p{margin:0;color:var(--muted);font:13px/1.5 Arial,sans-serif}
[data-theme="signal"] .meta{margin-top:16px;color:#f5be65;font-size:10px;text-transform:uppercase}
[data-theme="signal"] .journal-index{border-top:1px solid var(--line)}
[data-theme="signal"] .entry{display:grid;grid-template-columns:90px 1fr auto;gap:16px;padding:20px 0;border-bottom:1px solid var(--line);text-decoration:none;align-items:baseline}
[data-theme="signal"] .entry span{color:var(--muted);font-size:12px}
[data-theme="signal"] .entry strong{font:700 17px/1.3 Arial,sans-serif}
[data-theme="signal"] .post,[data-theme="signal"] .detail{padding:clamp(28px,5vw,72px);background:var(--panel);border:1px solid var(--line)}
[data-theme="signal"] .post p,[data-theme="signal"] .detail p{max-width:65ch;color:#b8c8bd;line-height:1.75;font-family:Arial,sans-serif}
[data-theme="signal"] .facts{display:grid;grid-template-columns:repeat(2,1fr);margin-top:36px;border-top:1px solid var(--line)}
[data-theme="signal"] .fact{padding:18px 0;border-bottom:1px solid var(--line)}
[data-theme="signal"] .fact small{display:block;color:var(--muted);margin-bottom:8px}
[data-theme="signal"] footer{display:flex;justify-content:space-between;gap:16px;padding:28px 0;color:var(--muted);font-size:11px;text-transform:uppercase}
[data-theme="signal"] .empty{padding:42px;border:1px dashed var(--line);color:var(--muted)}
[data-theme="signal"] .back{display:inline-block;margin-top:42px;color:var(--muted)}
[data-theme="signal"] .themer{color:var(--muted);background:var(--panel);border-color:var(--line)}

/* ================= EDITORIAL LEDGER — newsprint, 3-column ================= */
[data-theme="editorial"]{--paper:#f1eadb;--ink:#18201a;--red:#bd3d2c;--line:#aba393}
[data-theme="editorial"] body{background:var(--paper);color:var(--ink);font-family:Georgia,"Times New Roman",serif}
[data-theme="editorial"] .wrap{width:min(1240px,calc(100% - 38px));margin:auto}
[data-theme="editorial"] .top{display:flex;justify-content:space-between;align-items:end;padding:24px 0 14px;border-bottom:4px double var(--ink)}
[data-theme="editorial"] .brand{font:900 clamp(30px,5vw,58px)/.8 Georgia,serif;letter-spacing:-.06em;text-decoration:none}
[data-theme="editorial"] .status{display:none}
[data-theme="editorial"] nav{display:flex;gap:16px;font:12px Arial,sans-serif;text-transform:uppercase}
[data-theme="editorial"] nav a{text-decoration:none}[data-theme="editorial"] nav a:hover{color:var(--red)}
[data-theme="editorial"] .hero{display:grid;grid-template-columns:1.3fr .7fr;gap:30px;padding:70px 0 42px;border-bottom:1px solid var(--ink)}
[data-theme="editorial"] h1{margin:0;font:400 clamp(60px,10vw,128px)/.82 Georgia,serif;letter-spacing:-.075em}
[data-theme="editorial"] .kicker,[data-theme="editorial"] .label{font:700 11px Arial,sans-serif;color:var(--red);text-transform:uppercase;letter-spacing:.16em}
[data-theme="editorial"] .lede{align-self:end;font-size:20px;line-height:1.5;max-width:40ch}
[data-theme="editorial"] .lede:first-letter{float:left;color:var(--red);font-size:4.2em;line-height:.75;padding-right:10px}
[data-theme="editorial"] section{padding:60px 0;border-bottom:1px solid var(--ink)}
[data-theme="editorial"] .section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:10px 0 26px}
[data-theme="editorial"] .section-head h2{margin:0;font-size:clamp(40px,6vw,76px);line-height:.9;letter-spacing:-.055em}
[data-theme="editorial"] .products{columns:3;column-gap:0;border-top:1px solid var(--line);display:block}
[data-theme="editorial"] .product{break-inside:avoid;display:inline-block;width:100%;padding:22px 22px 30px 0;border-bottom:1px solid var(--line);text-decoration:none}
[data-theme="editorial"] .product:nth-child(3n+2),[data-theme="editorial"] .product:nth-child(3n){padding-left:22px;border-left:1px solid var(--line)}
[data-theme="editorial"] .product h3{margin:8px 0;font-size:28px;letter-spacing:-.03em}
[data-theme="editorial"] .product p{margin:0;line-height:1.5}
[data-theme="editorial"] .num{display:none}
[data-theme="editorial"] .meta,[data-theme="editorial"] .product small{font:10px Arial,sans-serif;text-transform:uppercase;color:var(--red)}
[data-theme="editorial"] .journal-index{border-top:1px solid var(--ink)}
[data-theme="editorial"] .entry{display:grid;grid-template-columns:60px 1fr auto;gap:16px;padding:18px 0;border-bottom:1px solid var(--line);text-decoration:none;align-items:baseline}
[data-theme="editorial"] .entry strong{font:400 23px/1.2 Georgia,serif}
[data-theme="editorial"] .entry span{font:10px Arial,sans-serif;text-transform:uppercase;color:var(--red)}
[data-theme="editorial"] .post,[data-theme="editorial"] .detail{padding:40px 0}
[data-theme="editorial"] .post p,[data-theme="editorial"] .detail p{max-width:62ch;font-size:19px;line-height:1.65}
[data-theme="editorial"] .facts{display:grid;grid-template-columns:repeat(2,1fr);margin-top:36px;border-top:1px solid var(--line)}
[data-theme="editorial"] .fact{padding:16px 0;border-bottom:1px solid var(--line)}
[data-theme="editorial"] .fact small{display:block;font:10px Arial,sans-serif;text-transform:uppercase;color:var(--red);margin-bottom:6px}
[data-theme="editorial"] footer{display:flex;justify-content:space-between;padding:26px 0;font:11px Arial,sans-serif;text-transform:uppercase}
[data-theme="editorial"] .empty{padding:36px;border:1px dashed var(--line)}
[data-theme="editorial"] .back{display:inline-block;margin-top:36px;font:12px Arial,sans-serif;text-transform:uppercase;color:var(--red)}
[data-theme="editorial"] .themer{border-color:var(--ink)}

/* ================= INSTRUMENT PANEL — blueprint modules ================= */
[data-theme="instrument"]{--navy:#071627;--blue:#0e2943;--line:#31506a;--ink:#dcecff;--muted:#87a4bd;--cyan:#63e5ff}
[data-theme="instrument"] body{background:linear-gradient(90deg,transparent 31px,#0a2035 32px),linear-gradient(transparent 31px,#0a2035 32px),var(--navy);background-size:32px 32px;color:var(--ink);font-family:Arial,Helvetica,sans-serif}
[data-theme="instrument"] .wrap{width:min(1420px,calc(100% - 28px));margin:auto}
[data-theme="instrument"] .top{display:flex;align-items:center;justify-content:space-between;padding:15px 18px;margin-top:14px;background:var(--blue);border:1px solid var(--line);box-shadow:6px 6px 0 #020b13}
[data-theme="instrument"] .brand{font-weight:900;text-decoration:none}
[data-theme="instrument"] .status{color:var(--cyan)}
[data-theme="instrument"] nav{display:flex;gap:14px;font:700 11px ui-monospace,monospace;text-transform:uppercase}
[data-theme="instrument"] nav a{text-decoration:none;color:var(--muted)}[data-theme="instrument"] nav a:hover{color:var(--cyan)}
[data-theme="instrument"] .hero{display:grid;grid-template-columns:1fr 320px;min-height:70vh;gap:16px;padding:16px 0;align-items:stretch}
[data-theme="instrument"] .hero>*{background:rgba(7,22,39,.94);border:1px solid var(--line);box-shadow:6px 6px 0 #020b13;padding:clamp(22px,4vw,56px)}
[data-theme="instrument"] h1{margin:8vh 0 20px;font:900 clamp(60px,11vw,150px)/.8 Arial,sans-serif;letter-spacing:-.07em}
[data-theme="instrument"] .kicker,[data-theme="instrument"] .label{color:var(--cyan);font:700 11px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.13em}
[data-theme="instrument"] .lede{max-width:50ch;color:var(--muted);font-size:18px;line-height:1.5}
[data-theme="instrument"] section{padding:54px 0}
[data-theme="instrument"] .section-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:18px}
[data-theme="instrument"] .section-head h2{margin:5px 0 0;font:900 clamp(38px,6vw,78px)/.9 Arial,sans-serif;letter-spacing:-.05em}
[data-theme="instrument"] .products{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
[data-theme="instrument"] .product{display:flex;flex-direction:column;padding:20px;background:var(--blue);border:1px solid var(--line);box-shadow:6px 6px 0 #020b13;text-decoration:none;min-height:200px}
[data-theme="instrument"] .product:hover{border-color:var(--cyan)}
[data-theme="instrument"] .num{font:700 11px ui-monospace,monospace;color:var(--cyan)}
[data-theme="instrument"] .product h3{margin:auto 0 10px;font:900 24px/1 Arial,sans-serif;letter-spacing:-.03em}
[data-theme="instrument"] .product p{margin:0;color:var(--muted);font-size:13px;line-height:1.5}
[data-theme="instrument"] .meta{margin-top:14px;font:700 10px ui-monospace,monospace;text-transform:uppercase;color:var(--cyan)}
[data-theme="instrument"] .journal-index{display:grid;gap:2px}
[data-theme="instrument"] .entry{display:grid;grid-template-columns:80px 1fr auto;gap:16px;padding:16px 18px;background:var(--blue);border:1px solid var(--line);text-decoration:none;align-items:baseline}
[data-theme="instrument"] .entry:hover{border-color:var(--cyan)}
[data-theme="instrument"] .entry span{font:700 11px ui-monospace,monospace;color:var(--muted)}
[data-theme="instrument"] .entry strong{font:900 16px Arial,sans-serif}
[data-theme="instrument"] .post,[data-theme="instrument"] .detail{padding:clamp(24px,4vw,56px);background:var(--blue);border:1px solid var(--line);box-shadow:6px 6px 0 #020b13}
[data-theme="instrument"] .post p,[data-theme="instrument"] .detail p{max-width:65ch;color:var(--muted);line-height:1.7}
[data-theme="instrument"] .facts{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;margin-top:30px;background:var(--line);border:1px solid var(--line)}
[data-theme="instrument"] .fact{padding:16px;background:var(--navy);font:700 15px ui-monospace,monospace}
[data-theme="instrument"] .fact small{display:block;color:var(--muted);font-weight:400;margin-bottom:6px;text-transform:uppercase;font-size:10px}
[data-theme="instrument"] footer{display:flex;justify-content:space-between;padding:22px 18px;margin-bottom:20px;background:var(--blue);border:1px solid var(--line);font:700 10px ui-monospace,monospace;text-transform:uppercase;color:var(--muted)}
[data-theme="instrument"] .empty{padding:36px;background:var(--blue);border:1px solid var(--line);color:var(--muted)}
[data-theme="instrument"] .back{display:inline-block;margin-top:30px;font:700 11px ui-monospace,monospace;text-transform:uppercase;color:var(--cyan)}
[data-theme="instrument"] .themer{color:var(--cyan);border-color:var(--line);background:var(--navy)}

/* ================= LIVING GALLERY — pill nav, asymmetric rooms ================= */
[data-theme="gallery"]{--bg:#0a0a0c;--ink:#f4f2ed;--muted:#a6a3a0;--lime:#d8ff58;--violet:#9f75ff;--pink:#ff6dba}
[data-theme="gallery"] body{background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif;overflow-x:clip}
[data-theme="gallery"] .wrap{width:min(1320px,calc(100% - 30px));margin:auto}
[data-theme="gallery"] .top{position:fixed;z-index:5;top:14px;left:50%;transform:translateX(-50%);width:min(660px,calc(100% - 28px));display:flex;justify-content:space-between;align-items:center;padding:10px 16px;border:1px solid #444;border-radius:999px;background:rgba(10,10,12,.8);backdrop-filter:blur(18px)}
[data-theme="gallery"] .brand{text-decoration:none;font-weight:900}
[data-theme="gallery"] .status{color:var(--lime)}
[data-theme="gallery"] nav{display:flex;gap:18px;font-size:12px}
[data-theme="gallery"] nav a{text-decoration:none;color:var(--muted)}[data-theme="gallery"] nav a:hover{color:var(--lime)}
[data-theme="gallery"] .hero{min-height:92vh;display:grid;align-content:center;text-align:center;position:relative}
[data-theme="gallery"] .hero:before,[data-theme="gallery"] .hero:after{content:"";position:absolute;width:34vw;aspect-ratio:1;border-radius:50%;filter:blur(90px);opacity:.18}
[data-theme="gallery"] .hero:before{background:var(--violet);left:-16vw}
[data-theme="gallery"] .hero:after{background:var(--lime);right:-16vw}
[data-theme="gallery"] h1{position:relative;margin:80px auto 20px;max-width:1100px;font:900 clamp(62px,11vw,150px)/.82 Arial,sans-serif;letter-spacing:-.08em}
[data-theme="gallery"] .kicker,[data-theme="gallery"] .label{display:inline-block;padding:7px 11px;border:1px solid #454545;border-radius:999px;color:var(--muted);font-size:11px;text-transform:uppercase;justify-self:center}
[data-theme="gallery"] .lede{position:relative;max-width:570px;margin:auto;color:var(--muted);font-size:18px;line-height:1.5}
[data-theme="gallery"] section{padding:80px 0}
[data-theme="gallery"] .section-head{text-align:center;margin-bottom:44px;display:grid;justify-items:center;gap:10px}
[data-theme="gallery"] .section-head h2{margin:0;font-size:clamp(46px,7vw,92px);line-height:.9;letter-spacing:-.06em}
[data-theme="gallery"] .products{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}
[data-theme="gallery"] .product{grid-column:span 4;display:flex;flex-direction:column;min-height:250px;padding:24px;border-radius:24px;background:#141416;border:1px solid #26262a;text-decoration:none;transition:transform .25s,background .25s}
[data-theme="gallery"] .product:nth-child(7n+1){grid-column:span 6;background:#17170c}
[data-theme="gallery"] .product:nth-child(7n+4){grid-column:span 6;background:#160f1c}
[data-theme="gallery"] .product:hover{transform:translateY(-6px);background:#1d1d21}
[data-theme="gallery"] .num{font-size:11px;color:var(--lime)}
[data-theme="gallery"] .product h3{margin:auto 0 12px;font:900 30px/1 Arial,sans-serif;letter-spacing:-.04em}
[data-theme="gallery"] .product p{margin:0;color:var(--muted);font-size:14px;line-height:1.5}
[data-theme="gallery"] .meta{margin-top:16px;font-size:10px;text-transform:uppercase;color:var(--pink)}
[data-theme="gallery"] .journal-index{display:grid;gap:12px;max-width:820px;margin:auto}
[data-theme="gallery"] .entry{display:grid;grid-template-columns:60px 1fr auto;gap:16px;padding:20px 24px;border-radius:18px;background:#141416;border:1px solid #26262a;text-decoration:none;align-items:baseline}
[data-theme="gallery"] .entry:hover{background:#1d1d21}
[data-theme="gallery"] .entry span{color:var(--muted);font-size:12px}
[data-theme="gallery"] .entry strong{font:900 18px/1.3 Arial,sans-serif}
[data-theme="gallery"] .post,[data-theme="gallery"] .detail{max-width:820px;margin:auto;padding:clamp(28px,5vw,64px);border-radius:28px;background:#141416;border:1px solid #26262a}
[data-theme="gallery"] .post p,[data-theme="gallery"] .detail p{max-width:64ch;color:#cfccc8;line-height:1.75;font-size:17px}
[data-theme="gallery"] .facts{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:32px}
[data-theme="gallery"] .fact{padding:18px;border-radius:16px;background:#1b1b1f}
[data-theme="gallery"] .fact small{display:block;color:var(--muted);margin-bottom:8px;font-size:11px;text-transform:uppercase}
[data-theme="gallery"] footer{display:flex;justify-content:space-between;gap:16px;padding:40px 0;color:var(--muted);font-size:11px;text-transform:uppercase}
[data-theme="gallery"] .empty{padding:42px;border-radius:24px;background:#141416;border:1px solid #26262a;color:var(--muted);text-align:center}
[data-theme="gallery"] .back{display:inline-block;margin-top:36px;color:var(--lime)}
[data-theme="gallery"] .themer{color:var(--muted);border-color:#444;border-radius:999px;background:transparent}
/* ---- detail/post titles must not inherit the hero h1 scale ---- */
[data-theme="signal"] .post h1,[data-theme="signal"] .detail h1{margin:14px 0 24px;font:700 clamp(34px,5vw,64px)/.95 Arial,sans-serif;letter-spacing:-.05em;max-width:20ch}
[data-theme="editorial"] .post h1,[data-theme="editorial"] .detail h1{margin:8px 0 22px;font:400 clamp(38px,6vw,72px)/.95 Georgia,serif;letter-spacing:-.05em;max-width:22ch}
[data-theme="instrument"] .post h1,[data-theme="instrument"] .detail h1{margin:10px 0 22px;font:900 clamp(34px,5vw,62px)/.95 Arial,sans-serif;letter-spacing:-.05em;max-width:20ch}
[data-theme="gallery"] .post h1,[data-theme="gallery"] .detail h1{margin:12px 0 24px;font:900 clamp(36px,5vw,66px)/.95 Arial,sans-serif;letter-spacing:-.05em;max-width:20ch}
[data-theme="signal"] .post h2,[data-theme="instrument"] .post h2,[data-theme="gallery"] .post h2{margin:34px 0 12px;font:700 clamp(21px,3vw,28px)/1.2 Arial,sans-serif}
[data-theme="editorial"] .post h2{margin:32px 0 10px;font:400 clamp(24px,3vw,32px)/1.2 Georgia,serif}
@media(max-width:900px){
[data-theme="signal"] .products{grid-template-columns:repeat(2,1fr)}
[data-theme="editorial"] .products{columns:2}
[data-theme="instrument"] .products{grid-template-columns:repeat(2,1fr)}
[data-theme="gallery"] .product,[data-theme="gallery"] .product:nth-child(7n+1),[data-theme="gallery"] .product:nth-child(7n+4){grid-column:span 6}
.hero,[data-theme="signal"] .hero,[data-theme="editorial"] .hero,[data-theme="instrument"] .hero{grid-template-columns:1fr!important}
.section-head,[data-theme="signal"] .section-head{grid-template-columns:1fr!important}
.facts{grid-template-columns:1fr!important}}
@media(max-width:560px){
[data-theme="signal"] .products,[data-theme="instrument"] .products{grid-template-columns:1fr}
[data-theme="editorial"] .products{columns:1}
[data-theme="editorial"] .product:nth-child(n){padding-left:0;border-left:0}
[data-theme="gallery"] .product,[data-theme="gallery"] .product:nth-child(7n+1),[data-theme="gallery"] .product:nth-child(7n+4){grid-column:span 12}
.entry{grid-template-columns:50px 1fr!important}.entry span:last-child{display:none}
footer{flex-direction:column}}
"""

THEMES = [
    ("signal", "Signal Catalog"),
    ("editorial", "Editorial Ledger"),
    ("instrument", "Instrument Panel"),
    ("gallery", "Living Gallery"),
]


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

def chrome(title: str, body: str, prefix: str = "", active: str = "", description: str = DESCRIPTION) -> str:
    def cls(name: str) -> str:
        return ' class="active"' if active == name else ""
    options = "".join(f'<option value="{k}">{v}</option>' for k, v in THEMES)
    # Applied in <head> so the stored theme paints on first frame, no flash.
    preload = ("<script>(function(){try{var t=localStorage.getItem('pc-theme');"
               "if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}})()</script>")
    switcher = ("<script>(function(){var s=document.getElementById('themer');if(!s)return;"
                "try{var t=localStorage.getItem('pc-theme');if(t)s.value=t}catch(e){}"
                "s.addEventListener('change',function(){var v=s.value;"
                "document.documentElement.setAttribute('data-theme',v);"
                "try{localStorage.setItem('pc-theme',v)}catch(e){}})})()</script>")
    return f"""<!doctype html>
<html lang="en" data-theme="signal"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(description)}">
<title>{esc(title)}</title>{preload}<style>{CSS}</style></head>
<body><a class="skip" href="#main">Skip to content</a><div class="wrap">
<header class="top"><div class="left">
<select id="themer" class="themer" aria-label="Colour theme">{options}</select>
<a class="brand" href="{prefix}index.html">P/C <span class="status" aria-hidden="true">&#9679;</span></a></div>
<nav aria-label="Primary"><a{cls('work')} href="{prefix}index.html#work">Work</a><a{cls('journal')} href="{prefix}journal/">Journal</a></nav></header>
<main id="main">{body}</main>
<footer><span>{esc(SITE_NAME)}</span><span>Generated from a sanitized public registry</span></footer>
</div>{switcher}</body></html>"""


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
