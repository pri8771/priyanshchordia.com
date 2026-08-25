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
