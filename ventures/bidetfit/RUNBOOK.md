# BidetFit Runbook

## Operating loop
Every eligible run must:
1. Read `MISSION.md`, `STATE.json`, `DECISIONS.md`, and the latest diary entry.
2. Stop safely if `KILL_SWITCH` exists or experiment status is `paused`/`stopped`.
3. Validate required project files and CSV headers.
4. Check local public-source integrity.
5. Check the public status endpoint and critical routes when the site is live or launching.
6. Refresh available metrics without inventing missing values.
7. Choose the highest-impact action that is permitted and executable.
8. Execute it, verify it, and record evidence.
9. Update `STATE.json`, `RUNS.csv`, `CHANGELOG.md` when appropriate, and the daily diary for substantive work.
10. Schedule or leave the next eligible action in persistent state.

## Scheduled operator
Workflow: `.github/workflows/bidetfit-operator.yml`  
Cadence: every six hours, plus manual dispatch and relevant source/workflow changes.  
The operator uses only Python's standard library and GitHub's included runner services. It performs deterministic state, schema, source, and public-health work while the chat is closed. It does not invent editorial judgment or silently call a paid model.

### Health and measurement freshness — BF-013 / PCH-104, BF-029 / PCH-120

`STATE.json.updated_at` has scope `operator_health_only`. A successful run may
advance health timestamps; it does not advance `metrics_observation.last_observed_at`
or turn unavailable traffic, sales or commission values into zero.

The public build produces status schema 2 from the recorded state and unchanged
`METRICS.csv`. `health` contains the last recorded verification/run times, not a
claim that deployment just checked the site. `metrics_observation.last_recorded_date`
identifies the newest dated historical CSV row; it is distinct from an actual
observation timestamp. The uninstrumented beta reports `status: unmeasured`, a null
observation timestamp, null traffic and null verified commission. The old launch-day
CSV rows remain intact. A future collector needs a reviewed observation contract
before these fields can report measured values; adding a CSV row alone does not
establish coverage. Public snapshots refresh on the existing deployment path.

Verification: `python3 -m unittest discover -s tests -v` includes stale/absent
measurement coverage and a mocked successful health run. These checks make no
provider requests and do not claim public deployment or business outcomes.

## Deployment
Workflow: `.github/workflows/bidetfit-pages-overlay.yml`  
The deployment rebuilds the public portfolio, mounts CommerceLint as a separate business, mounts and validates BidetFit, deploys the combined artifact, and verifies the BidetFit homepage, checker, status endpoint, and sitemap over public HTTPS.

## Diary protocol
- Record one detailed section for every local operating day, including failed attempts, evidence, assumptions, decisions, metrics, and the next adjustment.
- Record substantive model-driven work directly in `DIARY.md`.
- The external operator appends the first automated evidence entry for each UTC day.
- Preserve every run, including same-day repeats, in `RUNS.csv` and `logs/runs.jsonl`.
- Never rewrite a failure into a success; append the repair and verification evidence.

## Kill switch
Create `ventures/bidetfit/KILL_SWITCH` or set `experiment.status` to `paused` or `stopped`. The operator must log the paused state and perform no network or mutation work beyond that evidence record.

## Recovery
1. Inspect the most recent row in `RUNS.csv` and JSON object in `logs/runs.jsonl`.
2. Inspect the GitHub workflow run and any `[BidetFit] Operator incident` issue.
3. Reproduce source validation with `python3 -m ventures.bidetfit.scripts.operator --local-only`.
4. Repair the smallest failing component.
5. Dispatch the workflow manually or make a relevant source change.
6. Verify the public `status.json`, homepage, checker, and sitemap before closing the incident.

## Publishing gate
A page may publish only when it has:
- A clear audience and search intent.
- A unique value statement.
- Original analysis or utility.
- Source attribution for factual product/fit claims.
- One canonical URL, one H1, accessible navigation, and no broken local links.
- A current review date.
- Affiliate disclosure where commercial links appear.
- No claim of personal testing unless documented.

## Affiliate-link gate
Before activating a link, record merchant, network, current commission structure, attribution window, payment threshold, geography, prohibited traffic, content restrictions, link rules, application state, approval evidence, destination URL, and verification date. Confirm the link resolves and is allowed on the intended page.

## Financial gate
No spend occurs before cash is actually received. During a rolling 24-hour period, aggregate reinvestment spend may not exceed 50% of collected cash available at the start of that period without explicit owner approval.
