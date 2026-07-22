# priyanshchordia.com

Static public portfolio generated from the sanitized public view of the private
Mission Control registry.

## Data boundary

`mission-control/registry.json` is private operational truth. It is never read by
GitHub Pages and must never be copied here verbatim. `scripts/sync_registry.py`
exports only public product identity, summary, lifecycle stage, portfolio lane,
and public tier into `data/registry.public.json`; hidden products and all local
paths, priorities, gate evidence, health signals, and internal notes are omitted.

## Generate locally

```sh
python3 scripts/sync_registry.py ../mission-control/registry.json
python3 scripts/generate_site.py
python3 -m http.server --directory site 8000
```

GitHub Pages regenerates `site/` from the committed public snapshot on every push
to `main`. Custom-domain DNS is intentionally deferred to the final human-gate
handoff.
