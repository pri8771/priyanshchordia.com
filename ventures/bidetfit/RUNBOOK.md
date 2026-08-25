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
Cadence: every six hours, plus manual dispatch and source/workflow changes.  
The operator uses only Python’s standard library and GitHub’s included runner services.

## Kill switch
Create `ventures/bidetfit/KILL_SWITCH` or set `experiment.status` to `paused` or `stopped`. The operator must log the paused state and perform no network or mutation work beyond that evidence record.

## Recovery
1. Inspect the most recent row in `RUNS.csv` and JSON object in `logs/runs.jsonl`.
2. Inspect the GitHub workflow run and any `[BidetFit] Operator incident` issue.
3. Reproduce source validation with `python3 ventures/bidetfit/scripts/operator.py --local-only`.
4. Repair the smallest failing component.
5. Dispatch the workflow manually.
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
