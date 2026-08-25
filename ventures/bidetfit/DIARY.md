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

The existing portfolio validator checks every generated page for canonical URLs, metadata, document structure, local links, reachability, and sitemap consistency. Therefore, copying unvalidated files directly into `site/` would be unsafe. BidetFit will be mounted after the portfolio build using an isolated source directory and its own validator, mirroring the proven subsite pattern.

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

### Brand decision
The provisional brand is **BidetFit** with the line: **“Measure once. Buy the bidet that fits.”** An initial web search found no obvious same-category brand conflict, but this is not a legal trademark clearance. The project can operate under a subdirectory without buying a domain, and the brand can be changed if stronger evidence appears.

### Product decision
The first useful asset is a conservative browser-based fit checker. It asks for:
- One-piece, two-piece, wall-hung, or unknown toilet type.
- Round, elongated, unusual, or unknown bowl shape.
- Bowl length from mounting-bolt centerline to front edge.
- Mounting-bolt spacing.
- Clearance from the bolt centerline to the tank or rear curve.
- French-curve geometry.
- Skirted or concealed plumbing.
- Nearby electrical outlet.
- Desired bidet category.

The result is not a product guarantee. It reports likely fit, caution, or high fit risk; explains the reasons; and tells the reader what exact manufacturer dimensions still need confirmation.

### Monetization research
Initial program candidates were recorded, but no application or tracking link has been published:
- ManyBidets through Awin: published terms list 5% sitewide, 10% on select products, a 30-day cookie, and monthly payouts.
- Premium Bidet: published partner page lists 8%, 10%, and 15% tiers, 30-day last-click tracking, and monthly payouts.
- iCleaningo: published affiliate page lists a direct electric-bidet program; exact terms are queued for final application-time verification.
- Amazon Associates: a lower-rate fallback for eligible home products; category placement and attribution must be checked before use.
- Betterway was researched but is primarily a bamboo paper merchant, so it is a possible adjacent newsletter offer rather than a core bidet merchant.

### Adjustment made
The project is no longer waiting for a new repository, a paid domain, or Vercel. It will launch as an isolated subsite on the already-working GitHub Pages custom domain. Merchant applications will follow the useful beta rather than precede it, improving the credibility of applications and preventing placeholder affiliate content.

### Automation design
A scheduled GitHub Actions operator is being installed with a six-hour cadence. Each run will:
1. Read `STATE.json` and honor the kill switch.
2. Validate required memory files and CSV schemas.
3. Validate the source site and sitemap.
4. Check the public status endpoint when deployed.
5. Record evidence in `RUNS.csv` and `logs/runs.jsonl`.
6. Update the persistent state.
7. Commit only evidence/state changes.
8. Open or refresh a GitHub issue if the workflow fails.

This external deterministic loop can run while the chat is closed. It does not fabricate editorial judgment or silently call a paid language-model API. Research, new prose, and strategic pivots still require an active authorized model session unless a separate model runtime is later connected.

### Completed and verified so far on Day 2
- Existing free GitHub Pages host identified.
- Existing hourly deployment/recovery pattern inspected.
- CommerceLint separated from the affiliate experiment.
- Six niches scored.
- Bidet/toilet compatibility selected.
- BidetFit brand and MVP defined.
- Affiliate candidates and published terms recorded.
- Persistent project memory and detailed diary created.
- External scheduled operator configured in source.

### Still in progress
- Public deployment and route verification.
- First successful scheduled operator run.
- Affiliate applications.
- Search-engine submission and analytics baseline.

### Current measured result
- Public affiliate pages: 0 until deployment receipt passes
- Search impressions: 0
- Search clicks: 0
- Affiliate clicks: 0
- Applications submitted: 0
- Programs approved: 0
- Verified commissions: $0
- Cash received: $0

### Next adjustment trigger
If the fit checker receives impressions but weak engagement, simplify the measurement flow and lead with toilet-shape identification. If pages receive commercial clicks but no merchant approval, add eligible fallback merchants without weakening the niche. If search discovery remains zero after indexing and publication of the initial cluster, distribute the measurement guide through legitimate homeowner, plumbing, renter, and accessibility communities without spam.
