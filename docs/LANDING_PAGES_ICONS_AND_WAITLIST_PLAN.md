# Five-app landing pages, icons, and waitlist plan

Status: `implementation_in_progress`  
Created: 2026-08-03  
Canonical implementation repository: this repository

## Objective

Replace the current skeletal product pages with three selectable, accessible
landing-page directions for each of Mala, Anjali, Svara, Roam, and Hindsight;
integrate app-specific HubSpot Free CRM waitlists; and preserve free GitHub
Pages hosting.

The local Claude Design intake package is:

`/Users/pchordia/Documents/claude-design-handoff-five-apps-2026-08-03.zip`

It contains five current icon references, five real Mala screenshots, selected
product documentation, an asset manifest, screenshot gaps, implementation
constraints, and a prompt addendum. Claude Design is asked for **15 complete
clickable concepts**: three unique full designs and three corresponding icon
candidates for each of five apps. Generated concepts are not approved assets.

## Current truth

- GitHub Pages is canonical and free.
- Mala, Anjali, Svara, Roam, and Hindsight are in the public product catalogue.
- All five product pages use the shared Landing System handoff with app-specific
  tokens, motifs, content, and screenshot slots.
- Hindsight's landing page is public; its privacy/support routes remain withheld.
- App privacy/support copy is candidate legal copy and remains `noindex` until
  approval and effective dates are recorded.
- HubSpot is selected conceptually, but no portal/form identifiers or verified
  production forms are recorded here.
- No website-level waitlist privacy page or consent implementation exists.

## Non-negotiable architecture

- Keep the Python generator and generated `site/` output contract.
- Keep GitHub Pages and the custom domain.
- Do not scaffold React or a runtime backend.
- Store public page content and asset metadata in reviewed repository-owned
  source files; do not query private app repositories or CRM data at runtime.
- Keep facts and waitlist access usable without optional enhanced JavaScript.
- Do not hand-edit generated output.
- New icons remain candidates until separately approved by each app project.

## Task index

| ID | Task | Status | Depends on | Completion evidence |
|---|---|---|---|---|
| WEB-LP-001 | Ingest Claude concept-foundation package and verify its actual contents | complete | Claude Design delivery | Confirmed 15 written directions/15 icon descriptions; finished prototypes were not supplied |
| WEB-LP-002 | Preserve all three directions per app for owner comparison | complete | WEB-LP-001 | Three selectable directions per app; 15 total |
| WEB-LP-003 | Extend public content schema for rich landing-page fields and asset manifests | complete | agreed field contract | `data/landing_pages.json`, validation, and tests |
| WEB-LP-004 | Add Hindsight to the explicit public allowlist | complete | owner changed public scope | Five-product registry/sync allowlist; no sixth project exposed |
| WEB-LP-005 | Add Hindsight candidate privacy/support data and routes | blocked | exact Build 1 privacy review, support contact | Generated routes, noindex state, validation tests |
| WEB-LP-006 | Implement reusable semantic landing-page primitives | complete | WEB-LP-002, WEB-LP-003 | Shared generator markup, style module, and selector script |
| WEB-LP-007 | Implement five pages with the shared responsive landing system | complete | WEB-LP-006 | Generated pages, app-specific tokens, motifs, feature grids, screenshot slots |
| WEB-LP-008 | Create HubSpot portfolio/contact property and four/five form contract | blocked | owner HubSpot account | Property/form inventory with no secrets in Git |
| WEB-LP-009 | Publish website waitlist privacy disclosure and consent language | blocked | controller, purpose, retention/deletion decisions | Approved portfolio privacy page and consent copy |
| WEB-LP-010 | Integrate one app-specific waitlist form per page | blocked | WEB-LP-008, WEB-LP-009 | Default/error/duplicate/success/fallback behavior |
| WEB-LP-011 | Add metadata, portfolio Open Graph asset, canonical links, and structured data | complete | selected assets/copy | Portfolio social card, canonical links, and structured data are active |
| WEB-LP-012 | Run automated security/privacy/output checks | complete | WEB-LP-007 | Generator tests, route validation, JS checks, generated output |
| WEB-LP-013 | Run browser, responsive, reduced-motion, selector, and form QA | in progress | WEB-LP-012, test HubSpot forms | All 15 selectors and desktop/mobile layouts pass; production form states remain blocked |
| WEB-LP-014 | Deploy reviewed commit and verify exact public routes | blocked | WEB-LP-013, explicit owner approval | CI URL, commit SHA, live 200/404/link/form evidence |

## Rich public content contract

At minimum, support: tagline, beta status, hero copy, problem, audience,
benefits, how-it-works steps, privacy summary, limitations, screenshot manifest,
alt text, waitlist CTA, FAQ, app-resource links, selected concept ID, icon/asset
provenance, and last review date. Reject private contacts, internal notes,
unapproved metrics, testimonials, secrets, and arbitrary HTML in public data.

## HubSpot contract

Use one portfolio account. Prefer explicit per-app boolean interest properties
so joining multiple lists does not overwrite earlier interest. Track beta status
separately (`waitlisted`, `invited`, `testing`, `completed`, `paused`). Public
forms require email and app-specific consent; first name and device/testing
interest are optional. Store only public form IDs/configuration safe for a
browser. Never commit private CRM exports, tester lists, tokens, or credentials.

Do not install site-wide behavioral tracking by default. If proposed later,
perform a separate cookie/consent/privacy decision.

## Verification

Automated checks must cover schema failure, exact five-product visibility,
route reachability, canonical/social metadata, structured data, local links,
asset collisions, placeholder/private-field scans, form fallback markup, and
generated-output freshness. Manual checks must include keyboard, screen reader,
320px through desktop, 200% zoom, reduced motion, no-JavaScript factual access,
form consent and errors, logged-out live URLs, and support/privacy links.

## Publication boundary

Do not describe the CSS motifs or screenshot slots as approved App Store icons or app captures. Publication
of the landing pages requires truthful app-project claims and exact live
evidence. HubSpot forms and App Store legal routes remain separate gates; until
HubSpot is configured, the pages disclose and use an email fallback. Hindsight
may publish its private-beta landing page, but its legal routes remain withheld
until WEB-LP-005 is authorized and verified.

## Parked follow-up

| ID | Idea | Status | Before implementation |
|---|---|---|---|
| WEB-FUTURE-001 | Create a dedicated subpage for an ABBYY implementation specialist offering/profile | parked | Confirm audience, purpose, route, copy, relationship to the five-app portfolio, and whether ABBYY naming or assets require attribution/approval |
