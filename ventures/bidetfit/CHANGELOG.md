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
- Created Jira epic `PCH-90` and one Jira work item for every `BF-001` through `BF-033` record.
- Created the BidetFit Notion command-center project, 33 task mirrors, 12 canonical document indexes, and decision mirrors for `D-009` through `D-017`.
- Added `TRACKER_LINKS.csv` and `TRACKER_INDEX.md` with permanent GitHub, Jira, and Notion references, synchronization caveats, sample verification, and conflict procedure.
- Extended the unattended operator to require and validate tracker-link files before reporting project health.
- Merged tracker synchronization in GitHub PR #7 at `4ca038e91779613bff86f9254ffa1ee1c52b50de`.
- Verified the merged governance and tracker system through unattended operator run `32916545607`; the validation, durable state commit, and incident-resolution steps all passed.
- Transitioned Jira `PCH-103` and the Notion `BF-012` task to Done only after the post-merge cloud proof.
- Closed the canonical App Factory governance backfill and recorded `governance.backfill_status` as `synced`.

## 2026-08-24
- Experiment started.
- Constraints and 90-day window recorded.
- GitHub capability verified.
- Vercel path investigated but not connected.
