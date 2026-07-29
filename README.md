# priyanshchordia.com

A dependency-free, generated portfolio for independent software. The public
site is live at [priyanshchordia.com](https://priyanshchordia.com) and deploys
to GitHub Pages from `main`.

## Sources of truth

- `data/registry.public.json` — sanitized public product catalogue.
- `data/apps.json` — explicit publication state, support contact, App Store ID,
  and app-specific privacy copy.
- `content/posts/*.md` — journal entries with front matter.
- `scripts/themes/*.css` — shared base, 11 selectable designs, and the finishing
  layer for accessibility and narrow-screen behavior.
- `scripts/experiences/*.js` — four interactive homepage experiences.
- `scripts/generate_site.py` — static generator.

`mission-control/registry.json` is private operational truth. GitHub Pages never
reads it, and it must not be copied into this repository. The sync script exports
only public product identity, summary, lifecycle stage, portfolio lane, and tier;
it omits paths, priorities, gate evidence, health signals, and internal notes.

## Validate and generate

```sh
python3 -m unittest discover -s tests -v
python3 scripts/generate_site.py
python3 scripts/check_site.py
node --check site/experiences.js
python3 -m http.server --directory site 8000
```

To refresh the public product snapshot first:

```sh
python3 scripts/sync_registry.py ../mission-control/registry.json
```

The generated `site/` directory is committed. Do not hand-edit it: regenerate
after changing source data, themes, experiences, or the generator. CI repeats the
tests, generation, route/markup validation, JavaScript syntax check, and verifies
that the committed output is current before deployment.

## App Store URL contract

Published apps receive two stable App Store Connect destinations:

```text
https://priyanshchordia.com/apps/<slug>/privacy/
https://priyanshchordia.com/apps/<slug>/support/
```

Route generation and legal approval are separate. An enabled route must map to a
public product and have a real support email plus app-specific privacy copy. Copy
without explicit owner/legal approval is served `noindex` and omitted from the
sitemap. Approval also requires a per-app `policy_effective_date` in ISO
`YYYY-MM-DD` form. No generic legal policy is generated. `app_store_id` remains
`null` until a numeric Apple App ID is verified; only then does the site emit an
`apps.apple.com/app/id…` download link.

The public directory is
[priyanshchordia.com/apps/](https://priyanshchordia.com/apps/).
The per-app release gates and bundle-ID map are documented in
`docs/app-store-release-checklist.md`.

## Deployment

`.github/workflows/pages.yml` regenerates and validates the site on every push to
`main`, then publishes the exact `site/` artifact to GitHub Pages. The custom
domain and HTTPS are already configured.
