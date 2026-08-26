# BidetFit Decision Log

## D-001 — Use existing GitHub Pages infrastructure
**Date:** 2026-08-25  
**Decision:** Host BidetFit as an isolated subsite at `priyanshchordia.com/bidetfit/` using the existing card-free GitHub Pages pipeline.  
**Why:** It is already deployed, supports HTTPS and scheduled verification, costs $0, and avoids waiting for a new account or domain.  
**Tradeoff:** The first version lives on an owner domain rather than a standalone branded domain. Revisit only after measurable traction or collected revenue.

## D-002 — Keep CommerceLint separate
**Date:** 2026-08-25  
**Decision:** CommerceLint is a separate service business and is not part of the affiliate experiment.  
**Why:** It has a different mission, revenue model, state, and public product. Mixing results would make reporting misleading.  
**Implementation:** BidetFit uses a separate source path, workflow, state, diary, metrics, and public route.

## D-003 — Select bidet/toilet compatibility
**Date:** 2026-08-25  
**Decision:** Select bidet and toilet compatibility over dock/display compatibility, HVAC filters, robot-vacuum parts, home-office ergonomics, and travel adapters.  
**Evidence:** The niche combines strong purchase intent, measurable fit constraints, several direct affiliate programs, meaningful product values, relatively stable dimensions, and an opportunity to add an original decision tool without claiming product testing.  
**Primary risk:** Compatibility varies by exact product and toilet model, so the checker must be conservative and never state a guaranteed fit.

## D-004 — Use BidetFit as the provisional brand
**Date:** 2026-08-25  
**Decision:** Operate under `BidetFit`.  
**Why:** Descriptive, memorable, and aligned with the problem.  
**Caveat:** Initial collision search is not legal trademark clearance. The subdirectory strategy keeps a brand change inexpensive.

## D-005 — Launch utility before affiliate applications
**Date:** 2026-08-25  
**Decision:** Publish a genuinely useful beta before asking merchants to approve the site.  
**Why:** It improves application credibility, prevents a thin affiliate site, and creates a destination even while approvals are pending.

## D-006 — No active merchant links before approval
**Date:** 2026-08-25  
**Decision:** Product and merchant links remain editorial or absent until the exact program is approved and terms are recorded.  
**Why:** Avoid noncompliant tracking, broken attribution, misleading commercial claims, and premature optimization.

## D-007 — Split deterministic automation from model judgment
**Date:** 2026-08-25  
**Decision:** GitHub Actions performs health checks, state reads, schema checks, public verification, evidence logging, retries, and alerts. New research and substantive editorial decisions require an authorized model session unless a separate free model runtime is deliberately connected later.  
**Why:** This is honest autonomy: unattended tasks run externally, while judgment is not falsely described as continuous consciousness.

## D-008 — Narrow the moat after competitor discovery
**Date:** 2026-08-25  
**Decision:** Do not compete as another generic “best bidets” publisher or as a smart-toilet bathroom-readiness app. Prioritize retrofit bidet seats and attachments, French-curve and skirted-toilet edge cases, accessible-plumbing constraints, and an exact toilet-model by bidet-model evidence database.  
**Evidence:** A newly surfaced App Store product already performs verified smart-toilet fit math, while BestBidets already publishes broad practical buying guides and compatibility content.  
**Adjustment:** Move the model-level compatibility database, toilet-model identification guide, and photo/measurement sheet ahead of generic recommendation pages. Keep BidetFit's result conservative and source-linked.

## D-009 — Adopt App Factory Operating Standard 1.1
**Date:** 2026-08-25  
**Status:** Adopted  
**Owner:** Priyansh; implemented by ChatGPT  
**Decision:** Every substantive BidetFit task, bug, decision, discussion, risk, change request, release gate, prompt, and handoff uses the same stable-ID, evidence, timing, Jira, Notion, and GitHub rules as the App Factory.  
**Why:** Chat-only history cannot support durable autonomy, review, delegation, or truthful Done claims.  
**Consequences:** Historical tasks are backfilled without inventing exact hours. Future work must be Ready before execution and satisfy the Definition of Done.  
**Affected work:** BF-012 and all future work items.  
**Revisit trigger:** A later central standard version is explicitly approved and migrated.

## D-010 — Repository canonical; Jira lifecycle; Notion command center
**Date:** 2026-08-25  
**Status:** Adopted  
**Decision:** Versioned repository documentation and execution evidence are canonical. Jira is the executable lifecycle, dependency, approval, worklog, and discussion system. Notion is the project command center and planning/knowledge mirror. Chat is non-canonical until captured.  
**Why:** This mirrors the active App Factory doctrine and provides both inspectable evidence and usable owner interfaces.  
**Conflict rule:** Correct the repository first, open a sync or conflict work item, and then update Jira and Notion. Never silently overwrite history.

## D-011 — Use Jira project PCH as the BidetFit execution container
**Date:** 2026-08-25  
**Status:** Adopted  
**Decision:** Create a dedicated BidetFit epic and backlog in the existing Jira `PCH` project, whose current purpose is website work.  
**Why:** BidetFit is deployed on `priyanshchordia.com`, the connected Jira capability does not expose project creation, and a dedicated epic preserves project boundaries without waiting for manual Jira administration.  
**Tradeoff:** BidetFit shares a Jira project container. Stable `BF-` IDs, labels, epic linkage, repository paths, and Notion project links preserve isolation.  
**Revisit trigger:** A dedicated BidetFit Jira project is manually created or the portfolio adopts a different universal control plane.

## D-012 — Keep customer data out of public systems
**Date:** 2026-08-25  
**Status:** Adopted  
**Decision:** Raw customer email, personal data, order data, identity evidence, exact private measurements, and credentials must never be stored in the public repository, public logs, or Jira.  
**Why:** Support messages can contain private and sensitive information; Jira and the repository should hold sanitized summaries, policies, code, redacted fixtures, and evidence references only.  
**Implementation:** Customer operations require a private encrypted ticket and event store plus retention and deletion controls before launch.

## D-013 — Draft-first support before any auto-send
**Date:** 2026-08-25  
**Status:** Adopted architecture; release requires owner approval  
**Decision:** The first customer-support release creates drafts only. Named low-risk categories may auto-send only after a measured pilot, independent QA, exact prompt and template approval, canary limits, and automatic shutdown on guardrail breach.  
**Why:** Real support evidence should be collected before the system makes unsupervised external commitments.  
**Prohibited initial auto-send:** account actions, orders, returns or refunds, privacy or legal determinations, complaints, security incidents, and safety-critical advice.

## D-014 — Affiliate referrals do not grant return authority
**Date:** 2026-08-25  
**Status:** Adopted  
**Decision:** BidetFit does not process a merchant’s return, replacement, cancellation, or refund under the current affiliate model. It may provide general guidance or route the buyer to the seller.  
**Why:** The merchant is the transaction owner; affiliate referral does not create seller-of-record or API authority.  
**Future gate:** Returns require BidetFit to become the seller or receive explicit delegated merchant authority, then implement identity, policy, idempotency, audit, and scoped financial approval.

## D-015 — Use a zero-budget cloud mailbox poller for the first pilot
**Date:** 2026-08-25  
**Status:** Adopted architecture; implementation blocked on mailbox authorization  
**Decision:** Begin with a cloud-hosted Google Apps Script trigger that polls an authorized Gmail support label every few minutes and emits idempotent private ticket events.  
**Why:** It runs while the laptop is off, has no permanent VM requirement, and minimizes infrastructure and cost for low initial volume.  
**Tradeoff:** Polling adds latency and quota dependence. A Gmail API watch and event service may replace it when response-time or volume evidence justifies the change.

## D-016 — Open-ended unattended work requires a separate model runtime
**Date:** 2026-08-25  
**Status:** Adopted  
**Decision:** The six-hour GitHub operator remains deterministic. Customer classification, draft generation, open-ended research, and strategic diagnosis require a separately authorized API-accessible model or agent runtime.  
**Why:** This ChatGPT conversation cannot wake itself, and a ChatGPT subscription must not be assumed to provide API runtime or credits.  
**Gate:** Provider, model, cost or free tier, data handling, prompts, secrets, and failure behavior must be approved and logged before use.

## D-017 — Deterministic policy enforcement gates every external action
**Date:** 2026-08-25  
**Status:** Adopted architecture; high-risk delegation requires owner approval  
**Decision:** AI output is a proposal, not authority. A deterministic service classifies action risk, verifies identity and policy, checks environment and financial scope, enforces idempotency, validates a scoped approval token, writes an immutable receipt, and honors kill switches before any email, account, order, return, refund, deletion, or destructive action.  
**Why:** Prompt constraints alone cannot safely authorize external side effects.  
**Default:** Unclassified, ambiguous, unsupported, or high-risk actions deny or escalate.

## D-018 — Use an event-driven cloud agent rather than an always-on VM
**Date:** 2026-08-26  
**Status:** Adopted architecture; robust deployment blocked on owner billing authorization  
**Decision:** Build autonomy around event-driven disposable workers with durable external state. Use the existing GitHub Actions environment for the strict-zero-budget pilot, and prepare a Google Cloud foundation using Cloud Run, Cloud Run Jobs, Firestore, Pub/Sub or Cloud Tasks, Cloud Scheduler, Secret Manager, monitoring, a private GitHub App, Jira events, and a separately approved model API. Do not operate an idle permanent VM.  
**Why:** The workload is intermittent. Event-driven compute is continuously available without consuming compute while idle, is easier to patch and recover, and supports signed webhooks, retries, private state, least-privilege identities, and independent execution receipts. Cloud Run instances are disposable, so all mission, task, approval, and execution state must live outside the container.  
**Cost decision:** Pilot with minimum instances 0, maximum instances 1, concurrency 1, bounded jobs, provider quotas, spend controls, and kill switches. Google Cloud requires a valid billing account even for free-tier usage, so linking billing is an explicit owner exception to the original no-card rule and does not authorize paid usage.  
**Model decision:** A ChatGPT subscription is not an API runtime. Use a separately authorized model API. A provider free tier may be used only for public or properly redacted material and only after its data-use terms are accepted; raw customer or confidential data requires an approved private-data tier.  
**Code authority:** The runtime may create branches, commits, pull requests, tests, reports, and Jira receipts. It may not bypass branch protection, read secrets, directly push to production, accept agreements, or perform customer, merchant, legal, privacy, or financial actions outside an approved deterministic policy.  
**Affected work:** BF-013, BF-017, BF-021, BF-023, BF-029, BF-030, BF-031, and BF-034.  
**Revisit trigger:** Measured traffic or workload makes scale-to-zero latency unacceptable, or an equally secure zero-cost runtime becomes available.
