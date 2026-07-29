# App Store URL release checklist

These routes are generated from `data/apps.json`. They are stable App Store
Connect destinations. The implementation-derived copy was audited on
2026-07-29, but it remains candidate legal copy, is marked `noindex`, and is
omitted from the sitemap until `legal_approved` is explicitly set to `true`
with a per-app `policy_effective_date`.

| App | Bundle ID | Privacy URL | Support URL | Apple App ID |
| --- | --- | --- | --- | --- |
| AuraFit | `com.pchordia.aurafit` | `https://priyanshchordia.com/apps/aurafit/privacy/` | `https://priyanshchordia.com/apps/aurafit/support/` | Not verified |
| Anjali | `app.anjali.Anjali` | `https://priyanshchordia.com/apps/anjali/privacy/` | `https://priyanshchordia.com/apps/anjali/support/` | Not verified |
| Tessera | `com.priyanshchordia.tessera` | `https://priyanshchordia.com/apps/tessera/privacy/` | `https://priyanshchordia.com/apps/tessera/support/` | Not verified |
| Svara | `com.primandir.svara` | `https://priyanshchordia.com/apps/svara/privacy/` | `https://priyanshchordia.com/apps/svara/support/` | Not verified |
| Roam | `com.localfirst.roam` | `https://priyanshchordia.com/apps/roam/privacy/` | `https://priyanshchordia.com/apps/roam/support/` | Not verified |
| Pocket Party Court | `com.pocketpartycourt.app` | `https://priyanshchordia.com/apps/pocket-party-court/privacy/` | `https://priyanshchordia.com/apps/pocket-party-court/support/` | Not verified |
| Hindsight | `com.hindsight.pchordia.app` | `https://priyanshchordia.com/apps/hindsight/privacy/` | `https://priyanshchordia.com/apps/hindsight/support/` | Not verified |

## Current review state

| App | Implementation review | Remaining publication gate |
| --- | --- | --- |
| AuraFit | Candidate copy corrected to match the current deterministic on-device analysis, system photo picker, and runtime StoreKit behavior | Owner/legal approval |
| Anjali | Factual review complete | Owner/legal approval |
| Tessera | Factual review complete | Repository-designated legal-controller approval |
| Svara | Factual review complete | Owner/legal approval |
| Roam | Factual review complete | Owner/legal approval |
| Pocket Party Court | Factual review complete | Owner/legal approval |
| Hindsight | Factual review complete | Owner/legal approval |

The shared support mailbox has DNS-level mail routing, but its end-to-end
operation is not yet verified. The required workflow is: send a uniquely titled
message from an authenticated external mailbox to
`support@priyanshchordia.com`, confirm receipt in the owned destination mailbox,
reply, confirm the reply arrives back at the sender, and record the person who
monitors the address. The Gmail connector required reauthentication during the
2026-07-29 audit, so this test was not performed and no test email was sent.

## Before App Store submission

For each app:

1. Compare the privacy copy with the exact archived release binary, enabled
   capabilities, privacy manifest, App Store privacy answers, StoreKit products,
   permissions, exports, notifications, diagnostics, and deletion behavior.
2. Confirm the copy with the owner/legal reviewer appropriate for the release.
3. Set `legal_approved` to `true` and set `policy_effective_date` to the actual
   approval/effective date in `YYYY-MM-DD` form.
4. Send a real message to `support@priyanshchordia.com`, receive it in the owned
   mailbox, reply, and record who monitors it. DNS-level mail routing alone does
   not prove the recipient exists.
5. Regenerate and run the full validation sequence in `README.md`.
6. Commit, push, wait for GitHub Pages deployment, and verify each route in a
   logged-out browser over HTTPS.
7. After Apple creates a public listing, copy the numeric Apple App ID into
   `app_store_id`. The generator will then emit the canonical
   `https://apps.apple.com/app/id<id>` link; do not use same-name listings from
   other developers.

Digital Temple is intentionally excluded from route generation until its
optional Firebase account, sync, analytics, crash-reporting, retention, and
deletion behavior receives a separate review.
