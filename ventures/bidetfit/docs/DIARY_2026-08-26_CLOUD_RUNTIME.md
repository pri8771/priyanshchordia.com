# BidetFit Diary Addendum — 24×7-as-needed Cloud Runtime

**Date:** Wednesday, August 26, 2026  
**Work item:** BF-034 / Jira PCH-127  
**Prompt:** PRM-BF-007  
**Status:** Architecture and governance records complete; implementation and owner gates open

## Owner request

The owner asked how to create a place where the BidetFit operator could run continuously as needed while the laptop is off, including code updates, analytics analysis, and more complete autonomy.

## Current-state diagnosis

The existing GitHub Actions operator is a real external unattended process, but it is intentionally deterministic. It wakes every six hours, validates state and governance, verifies the public site, records evidence, and opens incidents. It does not maintain private durable event state, receive authenticated Jira/Gmail webhooks, call a model, analyze traffic strategically, or write substantive code.

A permanently running VM was rejected as the default architecture because the workload is intermittent and an idle server would add patching, credential, recovery, and cost burden without improving the business loop. The desired capability is continuously available event-driven execution rather than continuously occupied compute.

## Research and constraint discovered

Google Cloud Run can scale to zero and its container filesystem is disposable, so durable mission, task, approval, and execution state must live in an external database. A valid Google Cloud Billing account is still required even when expected usage remains within free tiers. That requirement conflicts with the original no-card rule and therefore remains an explicit owner gate rather than being silently bypassed.

A provider model API is also distinct from a consumer ChatGPT subscription. Free model tiers can have quota and data-use limitations. Any free model path is restricted to public or properly redacted data; customer messages and confidential information require an approved private-data tier.

## Decision

Adopt a two-path rollout:

1. Strict-zero pilot using GitHub Actions, analytics APIs, Jira polling or validated dispatch, and a free model tier only for public/redacted tasks.
2. Robust event-driven Google Cloud runtime after explicit billing authorization, using Cloud Run, Cloud Run Jobs, Firestore, Pub/Sub or Cloud Tasks, Cloud Scheduler, Secret Manager, monitoring, a private GitHub App, Jira events, and an approved model API.

The strict-zero path remains a fallback and independent watchdog after the robust runtime is available.

## Control model

- Model output is a proposal, not authority.
- Jira, email, web content, and model output are untrusted data.
- Every event has an idempotency key and every task has a lease.
- Code changes occur on branches and pull requests.
- Tests, preview, policy, and verification gates precede production.
- External actions are independently authorized.
- Global and capability-specific kill switches are mandatory.
- Secrets and raw PII never enter public GitHub, Jira, Notion, or logs.

## First vertical slice

A trusted Jira task moved to `Ready for Agent` will create exactly one task. The worker will read canonical BidetFit state from GitHub, fetch the public status endpoint, write a sanitized execution receipt back to Jira, reject replay, and honor a global kill switch. It will not edit code, use a model, send email, or deploy.

## Records created

- Jira PCH-127 / BF-034.
- Notion BF-034 project child page.
- `docs/work_items/BF-034.md`.
- `docs/CLOUD_AGENT_RUNTIME.md`.
- D-018 in `DECISIONS.md`.
- PRM-BF-007 and prompt-log entry.
- Updated task and tracker ledgers.

## Owner actions ahead

- Decide whether to preserve strict no-card operation or explicitly authorize Google Cloud billing linkage with no actual spend authorization.
- Create or approve the dedicated Google Cloud project and 2FA/recovery.
- Install the private GitHub App.
- Authorize Jira and analytics access.
- Select and authorize a model API and data policy.
- Later authorize the BidetFit support mailbox and Gmail scopes.

## Next implementation order

1. Merge the BF-034 planning and governance records.
2. Build the strict-zero no-op Jira-to-runner-to-receipt path.
3. Create infrastructure-as-code for the robust path without credentials.
4. Bundle the exact owner setup screens and permissions.
5. Deploy and test after the owner gate.
6. Add analytics, code update, model, and email capabilities one bounded tier at a time.
