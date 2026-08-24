#!/usr/bin/env python3
"""Inject a tracked MachineCart launch surface into the generated portfolio."""

from __future__ import annotations

from pathlib import Path


def inject_portfolio_promotion(site_root: Path) -> None:
    """Add one promotion without changing the six-app source catalog."""

    homepage = site_root / "index.html"
    content = homepage.read_text(encoding="utf-8")
    marker = 'id="machinecart-live"'
    if marker in content:
        return

    journal_marker = '<section id="journal">'
    if content.count(journal_marker) != 1:
        raise ValueError(
            f"Expected one portfolio journal section, found {content.count(journal_marker)}"
        )

    promotion = """<section id="machinecart-live" data-machinecart-promotion="2026-08-24">
<div class="section-head"><span class="label">02 / Live experiment</span><h2>Machine-readable commerce.</h2></div>
<div class="products"><a class="product" href="machinecart/?utm_source=portfolio&amp;utm_medium=internal&amp;utm_campaign=machinecart_launch">
<span class="num">LIVE</span><h3>MachineCart</h3>
<p>Scan an ecommerce product page for structured-data, offer, variant, policy, and machine-understanding gaps.</p>
<span class="meta">web commerce / free scanner</span></a></div>
</section>
"""
    content = content.replace(journal_marker, promotion + journal_marker, 1)
    content = content.replace(
        '<span class="label">02 / Journal</span>',
        '<span class="label">03 / Journal</span>',
        1,
    )

    nav_marker = '<a href="journal/">Journal</a>'
    nav_link = (
        '<a href="machinecart/?utm_source=portfolio_nav&amp;utm_medium=internal&amp;'
        'utm_campaign=machinecart_launch">MachineCart</a>'
    )
    if nav_link not in content:
        if content.count(nav_marker) != 1:
            raise ValueError(
                f"Expected one portfolio journal nav link, found {content.count(nav_marker)}"
            )
        content = content.replace(nav_marker, nav_link + nav_marker, 1)

    homepage.write_text(content, encoding="utf-8")

    rendered = homepage.read_text(encoding="utf-8")
    required = (
        marker,
        'href="machinecart/?utm_source=portfolio',
        '>MachineCart</a>',
        '03 / Journal',
    )
    missing = [value for value in required if value not in rendered]
    if missing:
        raise ValueError(f"Portfolio MachineCart promotion failed validation: {missing}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("site_root", type=Path)
    args = parser.parse_args()
    inject_portfolio_promotion(args.site_root.resolve())
    print("MachineCart portfolio promotion injected and validated.")
