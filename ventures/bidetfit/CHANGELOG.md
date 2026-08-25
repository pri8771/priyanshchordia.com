# BidetFit Changelog

## 2026-08-25
- Selected BidetFit and the bidet/toilet compatibility niche.
- Created persistent mission, state, decision log, account inventory, runbook, scorecard, queues, metrics, experiments, affiliate-program ledger, source log, and detailed operating diary.
- Built and deployed an 11-page public beta containing a measurement-driven fit checker, measurement guide, special-toilet guides, category comparison, methodology, privacy policy, disclosure, sitemap, and machine-readable status endpoint.
- Publicly verified the homepage, fit checker, status endpoint, and sitemap over HTTPS.
- Added a scheduled, card-free GitHub Actions operator with a six-hour cadence, kill switch, state persistence, public health checks, run evidence, and incident creation.
- Diagnosed the first operator failure: the filename `operator.py` shadowed Python's standard-library `operator` module when executed by path. Changed execution to module mode and verified a successful external run with HTTP 200.
- Diagnosed a deployment-reporting false negative: build, deploy, and HTTP verification passed, but the issue-cleanup command lacked repository context. Added explicit repository context without changing the healthy deployed artifact.
- Repositioned the next content phase around exact retrofit seat and attachment compatibility after discovering a new smart-toilet fit app and an established broad buying-guide competitor.
- Recorded that no affiliate links, applications, search traffic, or revenue are yet verified.
- Adopted App Factory Operating Standard 1.1 for BidetFit.
- Added stable BF-001 through BF-033 work items covering all substantive historical work and the complete forward backlog.
- Added repo-first governance adapters, Ready and Done gates, prompt registry, time and evidence ledgers, bug, risk, and assumption records, handoff, and synchronization status.
- Documented a phased laptop-off customer-support architecture using a cloud support mailbox, private ticket store, bounded external model runtime, deterministic policy and approval layer, draft-first rollout, owner escalation, audit receipts, and kill switches.
- Recorded that BidetFit cannot process affiliate-merchant returns under the current business model; returns require seller or explicit delegated merchant authority.
- Added core governance documents and work-item CSV schemas to unattended operator health validation.

## 2026-08-24
- Experiment started.
- Constraints and 90-day window recorded.
- GitHub capability verified.
- Vercel path investigated but not connected.
