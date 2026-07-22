#!/usr/bin/env python3
"""Generate the dependency-free public portfolio and registry-backed product pages."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "registry.public.json"
OUT = ROOT / "site"

CSS = """
:root {
  --paper:#f3eddf; --paper-deep:#e8dcc7; --ink:#17342f; --muted:#5e6d63;
  --line:rgba(23,52,47,.18); --coral:#d85e43; --marigold:#e6a935;
  --card:rgba(255,252,244,.7); --white:#fffdf7;
}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);background:radial-gradient(circle at 82% 8%,rgba(230,169,53,.25),transparent 30rem),radial-gradient(circle at 8% 68%,rgba(216,94,67,.13),transparent 27rem),repeating-linear-gradient(105deg,transparent 0 22px,rgba(23,52,47,.018) 22px 23px),var(--paper);font-family:"Avenir Next","Gill Sans",sans-serif;min-height:100vh}
a{color:inherit}.shell{width:min(1180px,calc(100% - 40px));margin:0 auto}
header{display:flex;align-items:center;justify-content:space-between;padding:28px 0;border-bottom:1px solid var(--line)}
.mark{font:700 13px/1 "Avenir Next",sans-serif;letter-spacing:.17em;text-transform:uppercase;text-decoration:none}
nav{display:flex;gap:24px;font-size:14px}nav a{text-decoration:none}.active{color:var(--coral)}
main{padding:clamp(72px,11vw,150px) 0 48px}.eyebrow{margin:0 0 22px;color:var(--coral);font-weight:700;letter-spacing:.16em;text-transform:uppercase;font-size:12px}
h1{max-width:980px;margin:0;font:500 clamp(58px,10vw,132px)/.9 "Iowan Old Style",Baskerville,Palatino,serif;letter-spacing:-.055em;text-wrap:balance}h1 em{color:var(--coral);font-weight:500}
.intro{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(230px,.6fr);gap:48px;align-items:end;margin-top:54px}.intro p,.lede{max-width:700px;margin:0;color:var(--muted);font:400 clamp(18px,2.2vw,27px)/1.45 "Iowan Old Style",Baskerville,serif}
.stamp{justify-self:end;width:210px;aspect-ratio:1;display:grid;place-items:center;border:1px solid var(--line);border-radius:50%;transform:rotate(5deg);text-align:center;background:rgba(255,252,244,.28)}.stamp strong{display:block;font:500 42px/1 "Iowan Old Style",serif}.stamp span{color:var(--muted);font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.section-head{display:flex;align-items:end;justify-content:space-between;gap:24px;margin:clamp(90px,14vw,180px) 0 28px}.section-head h2{margin:0;font:500 clamp(34px,5vw,66px)/1 "Iowan Old Style",Baskerville,serif;letter-spacing:-.035em}.section-head a{text-underline-offset:5px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{min-height:265px;display:flex;flex-direction:column;padding:clamp(24px,4vw,42px);border:1px solid var(--line);border-radius:2px 34px 2px 34px;background:var(--card);text-decoration:none;box-shadow:0 24px 70px rgba(55,43,27,.06);transition:transform .25s ease,background .25s ease}.card:hover{transform:translateY(-5px);background:var(--white)}
.card small,.meta{color:var(--coral);font-weight:700;font-size:11px;letter-spacing:.13em;text-transform:uppercase}.card h3{margin:26px 0 12px;font:500 clamp(31px,4vw,52px)/1 "Iowan Old Style",Baskerville,serif;letter-spacing:-.035em}.card p{max-width:48ch;margin:0 0 28px;color:var(--muted);line-height:1.55}.arrow{margin-top:auto;font-size:23px}
.page-hero{padding-bottom:clamp(30px,6vw,80px);border-bottom:1px solid var(--line)}.page-hero h1{font-size:clamp(62px,12vw,150px)}.page-hero .lede{margin-top:40px}
.detail{display:grid;grid-template-columns:.55fr 1.45fr;gap:48px;padding:clamp(42px,8vw,100px) 0}.detail h2{margin:0;font:500 clamp(34px,5vw,62px)/1 "Iowan Old Style",serif}.facts{display:grid;gap:0;border-top:1px solid var(--line)}.fact{display:grid;grid-template-columns:140px 1fr;gap:24px;padding:20px 0;border-bottom:1px solid var(--line)}.fact dt{color:var(--muted);font-size:12px;letter-spacing:.12em;text-transform:uppercase}.fact dd{margin:0}
.back{display:inline-block;margin-top:42px;text-underline-offset:5px}.empty{padding:42px;border:1px solid var(--line);background:var(--card)}
footer{display:flex;justify-content:space-between;gap:20px;margin-top:72px;padding:26px 0 34px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;letter-spacing:.06em;text-transform:uppercase}
.reveal{opacity:0;transform:translateY(22px);animation:arrive .8s cubic-bezier(.2,.75,.2,1) forwards}.reveal:nth-child(2){animation-delay:.12s}.reveal:nth-child(3){animation-delay:.24s}@keyframes arrive{to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.reveal{opacity:1;transform:none;animation:none}.card{transition:none}}
@media(max-width:720px){.shell{width:min(100% - 26px,1180px)}header{padding:20px 0}nav{gap:14px}.intro,.detail{grid-template-columns:1fr}.stamp{justify-self:start;width:150px}.stamp strong{font-size:32px}.grid{grid-template-columns:1fr}.fact{grid-template-columns:1fr;gap:7px}footer{flex-direction:column}}
"""


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def load_products() -> list[dict[str, object]]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = data.get("products", [])
    for product in products:
        slug = str(product.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe product slug: {slug!r}")
        if product.get("public_tier") not in {"featured", "lab"}:
            raise ValueError(f"Non-public tier entered public snapshot: {product.get('id')}")
    return products


def chrome(title: str, body: str, prefix: str = "", active: str = "") -> str:
    work_class = ' class="active"' if active == "work" else ""
    lab_class = ' class="active"' if active == "lab" else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Independent software studio building careful tools for work and everyday life.">
<title>{esc(title)}</title><style>{CSS}</style></head>
<body><div class="shell"><header><a class="mark" href="{prefix}index.html">Priyansh Chordia</a>
<nav aria-label="Primary"><a{work_class} href="{prefix}index.html#work">Selected work</a><a{lab_class} href="{prefix}lab/">Lab</a></nav></header>
{body}<footer><span>Built deliberately, published selectively.</span><span>Independent software studio</span></footer></div></body></html>"""


def product_card(product: dict[str, object], prefix: str = "") -> str:
    lane = str(product.get("portfolio_lane", "software")).replace("-", " ")
    return f"""<a class="card" href="{prefix}products/{esc(product['slug'])}/">
<small>{esc(lane)}</small><h3>{esc(product['name'])}</h3><p>{esc(product['summary'])}</p><span class="arrow" aria-hidden="true">↗</span></a>"""


def home(products: list[dict[str, object]]) -> str:
    featured = [product for product in products if product.get("public_tier") == "featured"]
    cards = "".join(product_card(product) for product in featured) or '<p class="empty">Selected work is being prepared.</p>'
    body = f"""<main><p class="eyebrow reveal">Independent software studio</p>
<h1 class="reveal">Careful software for <em>clearer work</em> and quieter lives.</h1>
<div class="intro reveal" id="approach"><p>I build focused products where privacy, evidence, and restraint are part of the experience — from document operations to thoughtful everyday tools.</p>
<div class="stamp" aria-label="Selected portfolio count"><div><strong>{len(featured)}</strong><span>selected projects<br>near release</span></div></div></div>
<div class="section-head" id="work"><div><p class="eyebrow">Selected work</p><h2>Close to the world.</h2></div><a href="lab/">Visit the Lab</a></div>
<section class="grid" aria-label="Selected products">{cards}</section></main>"""
    return chrome("Priyansh Chordia — Independent Software Studio", body, active="work")


def lab_page(products: list[dict[str, object]]) -> str:
    lab = [product for product in products if product.get("public_tier") == "lab"]
    cards = "".join(product_card(product, "../") for product in lab) or '<p class="empty">The Lab is quiet right now.</p>'
    body = f"""<main><section class="page-hero"><p class="eyebrow reveal">The Lab</p><h1 class="reveal">Work being <em>proven</em>.</h1>
<p class="lede reveal">Experiments and substantial builds stay here until their evidence, finish, and purpose earn a place in Selected Work.</p></section>
<div class="section-head"><div><p class="eyebrow">{len(lab)} active records</p><h2>Still in motion.</h2></div></div><section class="grid">{cards}</section></main>"""
    return chrome("The Lab — Priyansh Chordia", body, prefix="../", active="lab")


def product_page(product: dict[str, object]) -> str:
    name = esc(product["name"])
    lane = str(product.get("portfolio_lane", "software")).replace("-", " ")
    tier = "Selected work" if product.get("public_tier") == "featured" else "The Lab"
    body = f"""<main><section class="page-hero"><p class="eyebrow reveal">{esc(tier)} · {esc(lane)}</p><h1 class="reveal">{name}</h1>
<p class="lede reveal">{esc(product['summary'])}</p></section>
<section class="detail"><h2>Built with a narrow promise.</h2><dl class="facts">
<div class="fact"><dt>Portfolio</dt><dd>{esc(tier)}</dd></div><div class="fact"><dt>Lifecycle</dt><dd>{esc(product.get('stage', 'building'))}</dd></div>
<div class="fact"><dt>Practice</dt><dd>{esc(lane.title())}</dd></div><div class="fact"><dt>Publishing rule</dt><dd>Only verified public product facts are rendered from the sanitized registry.</dd></div>
</dl></section><a class="back" href="../../{'index.html#work' if product.get('public_tier') == 'featured' else 'lab/'}">← Back to {esc(tier)}</a></main>"""
    return chrome(f"{product['name']} — Priyansh Chordia", body, prefix="../../", active="work" if product.get("public_tier") == "featured" else "lab")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    products = load_products()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    write(OUT / ".nojekyll", "")
    write(OUT / "index.html", home(products))
    write(OUT / "lab" / "index.html", lab_page(products))
    for product in products:
        write(OUT / "products" / str(product["slug"]) / "index.html", product_page(product))
    print(f"generated homepage, Lab, and {len(products)} product pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
