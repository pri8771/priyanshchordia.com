#!/usr/bin/env python3
"""Generate the dependency-free public portfolio skeleton."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "registry.public.json"
OUT = ROOT / "site"


def load_counts() -> tuple[int, int]:
    if not DATA.exists():
        return 0, 0
    products = json.loads(DATA.read_text(encoding="utf-8")).get("products", [])
    featured = sum(product.get("public_tier") == "featured" for product in products)
    lab = sum(product.get("public_tier") == "lab" for product in products)
    return featured, lab


def main() -> int:
    featured, lab = load_counts()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "index.html").write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Independent software studio building careful tools for work and everyday life.">
  <title>Priyansh Chordia — Independent Software Studio</title>
  <style>
    :root {
      --paper: #f3eddf;
      --paper-deep: #e8dcc7;
      --ink: #17342f;
      --muted: #5e6d63;
      --line: rgba(23, 52, 47, .18);
      --coral: #d85e43;
      --marigold: #e6a935;
      --card: rgba(255, 252, 244, .68);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 82% 8%, rgba(230,169,53,.25), transparent 30rem),
        radial-gradient(circle at 8% 68%, rgba(216,94,67,.13), transparent 27rem),
        repeating-linear-gradient(105deg, transparent 0 22px, rgba(23,52,47,.018) 22px 23px),
        var(--paper);
      font-family: "Avenir Next", "Gill Sans", sans-serif;
      min-height: 100vh;
    }
    a { color: inherit; }
    .shell { width: min(1180px, calc(100% - 40px)); margin: 0 auto; }
    header { display: flex; align-items: center; justify-content: space-between; padding: 28px 0; border-bottom: 1px solid var(--line); }
    .mark { font: 700 13px/1 "Avenir Next", sans-serif; letter-spacing: .17em; text-transform: uppercase; text-decoration: none; }
    nav { display: flex; gap: 24px; font-size: 14px; }
    nav a { text-decoration: none; }
    main { padding: clamp(72px, 11vw, 150px) 0 48px; }
    .eyebrow { margin: 0 0 22px; color: var(--coral); font-weight: 700; letter-spacing: .16em; text-transform: uppercase; font-size: 12px; }
    h1 { max-width: 940px; margin: 0; font: 500 clamp(58px, 10vw, 132px)/.9 "Iowan Old Style", Baskerville, Palatino, serif; letter-spacing: -.055em; text-wrap: balance; }
    h1 em { color: var(--coral); font-weight: 500; }
    .intro { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(230px, .6fr); gap: 48px; align-items: end; margin-top: 54px; }
    .intro p { max-width: 660px; margin: 0; color: var(--muted); font: 400 clamp(18px, 2.2vw, 27px)/1.45 "Iowan Old Style", Baskerville, serif; }
    .stamp { justify-self: end; width: 210px; aspect-ratio: 1; display: grid; place-items: center; border: 1px solid var(--line); border-radius: 50%; transform: rotate(5deg); text-align: center; background: rgba(255,252,244,.28); }
    .stamp strong { display: block; font: 500 42px/1 "Iowan Old Style", serif; }
    .stamp span { color: var(--muted); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; }
    .coming { margin-top: clamp(90px, 14vw, 180px); padding: clamp(32px, 5vw, 68px); border: 1px solid var(--line); border-radius: 2px 42px 2px 42px; background: var(--card); box-shadow: 0 30px 80px rgba(55, 43, 27, .08); position: relative; overflow: hidden; }
    .coming::after { content: ""; position: absolute; width: 220px; height: 220px; right: -80px; bottom: -110px; border-radius: 50%; background: var(--marigold); opacity: .28; }
    .coming small { color: var(--coral); font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .coming h2 { max-width: 760px; margin: 18px 0 12px; font: 500 clamp(34px, 5vw, 66px)/1 "Iowan Old Style", Baskerville, serif; letter-spacing: -.035em; }
    .coming p { max-width: 640px; margin: 0; color: var(--muted); line-height: 1.65; }
    footer { display: flex; justify-content: space-between; gap: 20px; margin-top: 72px; padding: 26px 0 34px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; }
    .reveal { opacity: 0; transform: translateY(22px); animation: arrive .8s cubic-bezier(.2,.75,.2,1) forwards; }
    .reveal:nth-child(2) { animation-delay: .12s; }
    .reveal:nth-child(3) { animation-delay: .24s; }
    @keyframes arrive { to { opacity: 1; transform: none; } }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } .reveal { opacity: 1; transform: none; animation: none; } }
    @media (max-width: 720px) {
      .shell { width: min(100% - 26px, 1180px); }
      header { padding: 20px 0; }
      nav { gap: 14px; }
      .intro { grid-template-columns: 1fr; }
      .stamp { justify-self: start; width: 150px; }
      .stamp strong { font-size: 32px; }
      footer { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <a class="mark" href="/">Priyansh Chordia</a>
      <nav aria-label="Primary"><a href="#work">Work</a><a href="#approach">Approach</a></nav>
    </header>
    <main>
      <p class="eyebrow reveal">Independent software studio</p>
      <h1 class="reveal">Careful software for <em>clearer work</em> and quieter lives.</h1>
      <div class="intro reveal" id="approach">
        <p>I build focused products where privacy, evidence, and restraint are part of the experience — from document operations to thoughtful everyday tools.</p>
        <div class="stamp" aria-label="Portfolio preparation status"><div><strong>"""
        + html.escape(str(featured))
        + """</strong><span>selected projects<br>in preparation</span></div></div>
      </div>
      <section class="coming" id="work">
        <small>Portfolio consolidation</small>
        <h2>One home for the work.</h2>
        <p>The selected product stories are being prepared from a single verified portfolio registry. The next release will add individual project pages and a separate Lab for work still being proven.</p>
      </section>
    </main>
    <footer><span>Built deliberately, published selectively.</span><span>"""
        + html.escape(str(lab))
        + """ projects currently in the Lab</span></footer>
  </div>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"generated {OUT / 'index.html'} ({featured} selected, {lab} lab)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
