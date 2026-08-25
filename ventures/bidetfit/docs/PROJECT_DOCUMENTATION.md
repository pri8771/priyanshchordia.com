# BidetFit Project Documentation

**Project:** BidetFit  
**Owner:** Priyansh Chordia  
**Execution operator:** ChatGPT plus approved external workers  
**Scope version:** `BF-1.1-governed-autonomy`  
**Experiment:** 2026-08-24 through 2026-11-21  
**Canonical website:** https://priyanshchordia.com/bidetfit/  
**Repository:** `pri8771/priyanshchordia.com`, path `ventures/bidetfit`  
**Status:** Live public beta; deterministic unattended operations active; analytics, monetization, and customer operations not yet active  
**Last updated:** 2026-08-25

## Executive summary

BidetFit is a zero-budget affiliate publishing experiment focused on reducing bidet/toilet compatibility uncertainty. It provides a conservative browser-based fit checker and supporting measurement guides. The site is live, but it has no customer accounts, active affiliate links, verified traffic, sales, or revenue yet.

GitHub Pages serves the static site. GitHub Actions runs a six-hour deterministic operator that reads persistent state, validates required project records, checks public health, writes evidence, and opens incidents. This does not constitute a continuously thinking AI agent. Open-ended research, support replies, and strategic changes require an external model runtime or an active authorized AI session.

## Problem

A buyer can know that they want a bidet while still being unable to answer whether a seat, attachment, sprayer, plumbing adapter, or electric configuration will work with their exact toilet and bathroom. Common blockers include French-curve geometry, skirted or concealed plumbing, rear clearance, bolt spacing, bowl length, wall-hung construction, and power availability.

## Audience

- First-time bidet buyers.
- Owners of one-piece, French-curve, skirted, wall-hung, compact, or unusual toilets.
- Renters seeking reversible options.
- Buyers without a nearby electrical outlet.
- People comparing electric seats, non-electric attachments, and handheld sprayers.

## Product

The current product consists of:

- A measurement-driven fit checker.
- A how-to-measure guide.
- Guides for French-curve and skirted toilets.
- Round-versus-elongated interpretation.
- Electric-versus-non-electric comparison.
- No-outlet options.
- Editorial methodology, privacy, disclosure, sitemap, robots, and machine-readable status.

The checker reports broad category risk. It never guarantees that a specific product fits. Exact product and toilet drawings, installation requirements, and merchant return policies still control.

## Differentiation

The roadmap is intentionally narrower than a generic “best bidets” publication:

1. Retrofit seats and attachments.
2. Difficult toilet geometry and plumbing access.
3. Exact toilet-model × bidet-model evidence records.
4. Source-linked confidence and unresolved unknowns.
5. Measurement and photo artifacts that can be sent to manufacturers, merchants, plumbers, or landlords.

## Business model

The current model is affiliate referral revenue. BidetFit is not the seller of record and does not own the merchant transaction. It therefore cannot currently cancel, return, replace, or refund products purchased from an affiliate merchant. It may explain general fit considerations or route a visitor to the merchant. Actual post-purchase action requires seller status or explicit delegated merchant API authority.

Primary success metric: verified attributable affiliate commission during the experiment window. Pending, approved, reversed, and cash-received amounts remain separate.

## Current architecture

```text
Browser
  └─ GitHub Pages static site
       ├─ HTML/CSS/JavaScript fit checker
       ├─ public guides and disclosures
       └─ status.json

GitHub repository
  ├─ canonical docs and state
  ├─ public source
  ├─ validators
  └─ workflows

GitHub Actions
  ├─ build/deploy/verify
  └─ six-hour deterministic operator
       ├─ read state and kill switch
       ├─ validate files and schemas
       ├─ verify public status endpoint
       ├─ write run evidence
       └─ open/resolve incidents
```

## Target autonomous customer-operations architecture

```text
support mailbox
  → cloud intake trigger
  → private event queue and ticket store
  → deterministic classification and policy precheck
  → bounded external model runtime
  → approved knowledge retrieval
  → proposed response/action
  → authorization and approval service
  → draft, send, or owner escalation
  → immutable receipt and analytics
```

Raw customer messages and personal data must remain in private storage. Jira receives sanitized task summaries and evidence references, not raw email content. GitHub contains code, policies, redacted fixtures, and execution receipts without customer secrets.

## Governance

- Repository docs are canonical.
- Jira is the active work lifecycle and owner command queue.
- Notion is the project command center and planning/knowledge mirror.
- Every substantive task has a stable `BF-` work-item ID.
- Every decision, risk, question, bug, release gate, and prompt is recorded.
- Historical actual hours remain “Unknown / Needs Backfill” unless evidence supports a number.
- No work is Done without acceptance evidence and required synchronization.
- High-risk communications, identity, privacy, contracts, payments, returns, refunds, and destructive actions require deterministic authorization and scoped owner approval.

## Current verified state

- Public site: live.
- Public HTML pages: 11.
- Critical public routes verified: homepage, checker, status, sitemap.
- Deterministic external operator: healthy.
- Search Console: not configured.
- Behavioral analytics: not configured.
- Affiliate applications: 0.
- Approved programs: 0.
- Active affiliate links: 0.
- Verified sales: 0.
- Approved commission: $0.
- Cash received: $0.
- Customer accounts: none.
- Support mailbox: not provisioned.
- Return/refund authority: none.

## Immediate milestones

1. Complete App Factory governance backfill and Jira/Notion synchronization.
2. Establish Search Console and privacy-conscious event analytics.
3. Reverify and submit affiliate applications.
4. Build the exact compatibility data schema and initial records.
5. Provision the support inbox and draft-only customer-operations pilot.
6. Expand to low-risk auto-send only after measured quality and human approval.

## Non-goals for the current release

- Guaranteed fit.
- Product-testing claims.
- Customer accounts or payment processing.
- Direct sale, inventory, fulfillment, returns, or refunds.
- Unrestricted autonomous email.
- Storing personal data in the public repository or Jira.
- Spending before collected cash or beyond the authorized reinvestment cap.
