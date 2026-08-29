# BidetFit Operating Diary

This diary is the detailed chronological record for the 90-day affiliate experiment. It records completed work, failed attempts, evidence, assumptions, decisions, measured results, and the next adjustment. Automated health evidence is also written to `RUNS.csv` and `logs/runs.jsonl`.

---

## Day 1 — Monday, August 24, 2026

### Mission activation
The owner sent `START`, activating a 90-day experiment running from August 24 through November 21, 2026. The owner authorized legitimate free accounts, use of authorized non-Primandir infrastructure, a new brand chosen by the operator, and owner completion of unavoidable identity, tax, agreement, payout, CAPTCHA, or two-factor steps. Initial spending is $0. Collected cash may be reinvested under the 50%-per-rolling-24-hour cap.

### Constraints recorded
- Primandir is excluded completely.
- The `unsubscriber.me` identity may be used.
- Personal facts may not be invented. Real owner information is used only when genuinely required.
- No illegal, deceptive, spammy, or platform-prohibited tactics.
- Pending commissions are not spendable cash and do not count as revenue.

### Capability and infrastructure audit
GitHub access was verified for the authenticated account `pri8771`. The account contains public and private repositories and supports file, branch, pull-request, issue, and workflow operations through the connected GitHub capability.

A Vercel integration was identified as a possible deployment path, but it was not installed or connected. No claim of Vercel deployment was made. The initial attempt therefore did not produce a public affiliate site.

### Completed and verified
- Experiment dates and financial rules were fixed.
- GitHub access was verified.
- Existing assets were inventoried at a high level.
- The Primandir exclusion was preserved.

### Attempted but failed or incomplete
- A Vercel deployment connection was offered but not installed.
- No dedicated affiliate repository was created because the available connected action did not expose repository creation.
- No niche was selected.
- No site was published.
- No scheduled external operator had run.

### Measured result at end of Day 1
- Public affiliate pages: 0
- Search impressions: 0
- Search clicks: 0
- Affiliate clicks: 0
- Affiliate applications: 0
- Approved programs: 0
- Verified commissions: $0
- Cash received: $0
- Autonomous external runs: 0

### Lesson
The first day spent too much time auditing possibilities without shipping a bounded public asset. The adjustment for Day 2 was to use already-working, card-free GitHub Pages infrastructure, choose one narrow problem with an original tool advantage, and launch before pursuing merchant approval.

---

## Day 2 — Tuesday, August 25, 2026

### Repository and hosting investigation
A deeper repository audit found that `priyanshchordia.com` is already deployed through GitHub Pages from `main`, with a custom domain and an hourly deployment workflow. The workflow builds the existing portfolio, validates it, mounts a separate CommerceLint release, deploys the combined static artifact, performs public HTTP verification, and writes a machine-readable deployment receipt.

The audit also discovered that **CommerceLint is a separate autonomous zero-budget business** housed in `pri8771/autonomous_apps`. CommerceLint is an ecommerce audit/service experiment, not this affiliate publishing experiment. Its code, revenue model, state, and metrics must not be presented as BidetFit results. The only infrastructure shared is the zero-cost public host and deployment pipeline.

The existing portfolio validator checks every generated page for canonical URLs, metadata, document structure, local links, reachability, and sitemap consistency. Therefore, copying unvalidated files directly into `site/` would be unsafe. BidetFit is mounted after the portfolio build using an isolated source directory and its own validator, mirroring the proven subsite pattern.

### Niche research
Several commercially oriented niches were compared:

1. Bidet/toilet compatibility.
2. Laptop dock and external-display compatibility.
3. HVAC replacement-filter matching.
4. Robot-vacuum replacement parts.
5. Home-office ergonomics.
6. Travel power and plug compatibility.

The strongest alternative was laptop dock/display compatibility. It offers a valuable configuration checker, but typical PC and electronics commission rates are relatively low, specifications change quickly, and a promising merchant program explicitly excludes Pennsylvania-based affiliates. That makes it less attractive for this owner and this 90-day window.

Bidet/toilet compatibility won because the purchase blocker is unusually concrete: buyers frequently do not know whether a seat, attachment, valve, toilet shape, power arrangement, or clearance will work. Manufacturer fit guides expose measurable dimensions, allowing original value without pretending to physically test products. Multiple relevant merchants advertise direct commission rates between 5% and 15%, with 30-day attribution common. Product order values can also be materially higher than ordinary household consumables.

### Brand and product decision
The provisional brand is **BidetFit** with the line: **“Measure once. Buy the bidet that fits.”** The first useful asset is a conservative browser-based fit checker. It asks for toilet type, bowl shape, rear clearance, bolt spacing, bowl length, French-curve geometry, skirted or concealed plumbing, outlet availability, and desired bidet category. The result reports likely fit, caution, or high fit risk and explains what exact manufacturer evidence still needs confirmation. It is not a product guarantee.

### Monetization research
Initial program candidates were recorded, but no application or tracking link was published:
- ManyBidets through Awin: published terms list 5% sitewide, 10% on select products, and a 30-day cookie.
- Premium Bidet: published partner page lists 8%, 10%, and 15% tiers and 30-day last-click tracking.
- iCleaningo: a direct electric-bidet program whose full terms need final application-time verification.
- Amazon Associates: a lower-rate breadth fallback whose exact product-category rate and current rules must be checked.
- Betterway: an adjacent bathroom-consumables offer rather than a core fit merchant.

### Public beta built
BidetFit was implemented as an isolated static subsite with 11 HTML pages:
1. Homepage.
2. Interactive fit checker.
3. How-to-measure guide.
4. French-curve compatibility guide.
5. Skirted-toilet installation guide.
6. Round-versus-elongated guide.
7. Electric-versus-non-electric comparison.
8. No-outlet options guide.
9. Editorial methodology.
10. Affiliate disclosure.
11. Privacy policy.

The source also includes a sitemap, robots file, social image, machine-readable status endpoint, accessible navigation, structured data, and a custom validator. No affiliate links, analytics scripts, email capture, or invented product-testing claims were included at launch.

### Deployment evidence
The BidetFit overlay workflow rebuilt and validated the portfolio, mounted CommerceLint separately, mounted and validated BidetFit, deployed the combined GitHub Pages artifact, and performed public HTTPS checks on the homepage, fit checker, status endpoint, and sitemap. All four public checks passed, including an HTTP 200 status and expected content markers.

The overall deployment run initially appeared red only because a post-verification incident-cleanup command ran outside a checked-out repository and lacked explicit repository context. The website build, deployment, and public verification had already passed. The cleanup command was corrected by supplying the repository context, and the false-negative condition was documented rather than misreported as a site failure.

### Automation failure and repair
The first operator attempts failed before state validation. The root cause was technical and reproducible: invoking `ventures/bidetfit/scripts/operator.py` by path placed its directory first on Python's import path, causing the file named `operator.py` to shadow Python's standard-library `operator` module. Python then failed while importing `enum`.

The execution command was changed to module mode: `python3 -m ventures.bidetfit.scripts.operator`. The commit step was also hardened to preserve run evidence even after failures, and incident resolution was added after recovery.

The repaired external run `32868199605` completed successfully at `2026-08-25T15:49:47Z`. It loaded persistent state, validated required files and CSV schemas, validated the public source, fetched the public status endpoint, received HTTP 200, marked the site live, marked automation healthy, and committed the evidence to `STATE.json`, `RUNS.csv`, `logs/runs.jsonl`, and this diary.

### Competitive discovery after launch
A fresh search surfaced two important competitors:
- **Bidets: Smart Toilet Fit**, a newly listed app that checks smart-toilet installation requirements from manufacturer documentation and reports exact margins, failures, and unknowns.
- **BestBidets**, an established broad practical buying-guide site that already organizes content around fit, outlet availability, installation, and product categories.

This changes the strategy but does not invalidate the niche. It proves exact fit is a real user problem while reducing the value of generic “best bidet” publishing. BidetFit will differentiate around retrofit bidet seats and attachments, French-curve and skirted-toilet edge cases, accessible-plumbing constraints, and an exact toilet-model by bidet-model evidence database. The database, toilet-model identification guide, and printable measurement/photo sheet were moved ahead of generic recommendation pages.

### What Day 2 taught us
1. Ship a useful bounded product before adding accounts and monetization complexity.
2. Existing verified infrastructure is more valuable than waiting for an ideal standalone domain.
3. Fit uncertainty is a sharper commercial problem than another list of products.
4. The concept has competition; the moat must be exact evidence and difficult edge cases, not a broad quiz.
5. External deterministic autonomy is feasible and verified, but model-level strategic judgment still needs an authorized model runtime.
6. Red workflow badges must be diagnosed at the step level; a reporting failure is not the same as a deployment failure.

### End-of-day verified scorecard
- Public HTML pages: 11
- Public critical routes independently verified: 4
- Known indexed pages: 0; Search Console is not configured yet
- Search impressions: 0
- Search clicks: 0
- Organic sessions: 0 measured
- Affiliate applications: 0
- Approved programs: 0
- Active affiliate links: 0
- Affiliate clicks: 0
- Verified sales: 0
- Pending commission: $0
- Approved commission: $0
- Cash received: $0
- Successful external operator runs: 1

### Adjustment and next actions
1. Establish Search Console and indexing before interpreting “zero traffic.”
2. Reverify exact program terms and submit a bundled set of merchant applications; request owner action only for agreements, identity, tax, payout, CAPTCHA, or two-factor steps.
3. Build the model-level evidence schema and first 25 exact compatibility records.
4. Publish the toilet-model-number guide and printable measurement/photo sheet.
5. Add privacy-conscious analytics only after updating the privacy disclosure and keeping Primandir identifiers excluded.
6. After the next green overlay deployment, fold BidetFit into the primary Pages workflow to eliminate the short sequential redeployment window.
7. Measure impressions, checker starts, completions, qualified merchant clicks, and verified commission separately.

### Decision triggers
- If exact-pair pages earn impressions faster than broad guides, allocate most editorial capacity to the database.
- If the checker earns starts but weak completion, reduce the first screen to toilet type, shape, and three measurements, then progressively ask plumbing and power questions.
- If merchant approval is delayed, continue database publishing and use non-affiliate manufacturer destinations rather than adding unapproved tracking.
- If search discovery remains zero after sitemap submission and indexing time, distribute the measurement sheet through relevant homeowner, renter, plumbing, accessibility, and bidet communities without spam.

---

## Automated evidence — 2026-08-25

<!-- operator:2026-08-25 -->
- First external operator evidence for this UTC day: **success**.
- Public site state observed: **live**.
- Evidence detail: required files, CSV schemas, and public-source files passed; public status endpoint verified with HTTP 200.
- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.
---

## Automated evidence — 2026-08-26

<!-- operator:2026-08-26 -->
- First scheduled operator evidence for this UTC day: **success**.
- Public site state observed: **live**.
- Evidence detail: required mission, governance, tracker, work-item, CSV, and public-source files passed; public status endpoint verified
- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.
---

## Automated evidence — 2026-08-27

<!-- operator:2026-08-27 -->
- First scheduled operator evidence for this UTC day: **success**.
- Public site state observed: **live**.
- Evidence detail: required mission, governance, tracker, work-item, CSV, and public-source files passed; public status endpoint verified
- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.
---

## Automated evidence — 2026-08-28

<!-- operator:2026-08-28 -->
- First scheduled operator evidence for this UTC day: **success**.
- Public site state observed: **live**.
- Evidence detail: required mission, governance, tracker, work-item, CSV, and public-source files passed; public status endpoint verified
- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.
---

## Automated evidence — 2026-08-29

<!-- operator:2026-08-29 -->
- First scheduled operator evidence for this UTC day: **success**.
- Public site state observed: **live**.
- Evidence detail: required mission, governance, tracker, work-item, CSV, and public-source files passed; public status endpoint verified
- Additional same-day runs are retained in `RUNS.csv` and `logs/runs.jsonl`.

