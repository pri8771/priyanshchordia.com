---
title: "Artifact-First Development: What If Software Could Be Built Like Lego?"
slug: "artifact-first-development"
date: "2026-09-20"
summary: "The dependency does not have to be another team's implementation. Sometimes it can be an explicit contract for the artifact they must produce."
series: "Own Your AI Stack"
status: "published"
internal_status: "working-draft"
---

I keep coming back to a simple question:

**What if a software project were treated less like a sequence of tasks and more like a graph of artifacts that have to fit together?**

A lot of project plans quietly assume this:

```text
A → B → C → D
```

B waits for A. C waits for B. Adding more developers does not help if everyone is blocked on the same chain.

That becomes especially weird once the workers are AI agents.

If I can start ten implementation workers in a few minutes, worker supply is no longer the obvious bottleneck.

Dependencies are.

So the question I have been experimenting with is:

**Can some implementation dependencies be moved earlier into artifact contracts, so the actual implementations can happen in parallel?**

## The Lego version

Suppose Artifact A parses a customer from a purchase order.

Artifact B validates that customer.

The validator does not necessarily need the parser to exist.

It needs to know what the parser is obligated to produce.

For example:

```json
{
  "customer_id": "string",
  "name": "string",
  "country": "ISO-3166-1 alpha-2",
  "confidence": 0.0
}
```

Once that contract is stable, the validator can be built against fixtures.

```python
def validate_customer(customer):
    assert customer["customer_id"]
    assert len(customer["country"]) == 2
    assert 0 <= customer["confidence"] <= 1
    return customer
```

At the same time, another worker can build the parser against the same contract.

Neither implementation is fake.

The consumer uses a fixture until the real producer exists. The producer has a concrete output obligation. Integration becomes a test of whether the two pieces actually honor the same connection surface.

That is the Lego analogy.

The important thing is not how each piece was manufactured.

It is whether the studs line up.

## This is not a claim that contracts are new

The pieces of this idea already exist in software engineering.

API-first and contract-first development define interfaces before implementations. Tools such as [Pact](https://docs.pact.io/) let consumers and providers test integration contracts independently. Build systems such as [Bazel](https://bazel.build/versions/9.0.0/about/intro) explicitly model artifacts, actions, and dependency graphs so work can be reused and scheduled correctly.

I am not trying to rename all of that.

The part I am interested in is the **project-management unit**.

Instead of saying:

> Version 1.4 is 80% done because 16 of 20 tasks are closed.

I want to be able to say:

> Version 1.4 exists when this exact set of accepted artifacts exists.

That turns a version into an artifact set instead of a task percentage.

## What counts as an artifact?

An artifact can be code, but it does not have to be.

For an AI-heavy software project, I might track:

- an API contract;
- a JSON schema;
- a database migration;
- a threat model;
- a benchmark definition;
- a fixture set;
- a test harness;
- a deployment manifest;
- a runbook;
- a UI component;
- a verified model-qualification result;
- a real end-to-end evidence package.

The important property is that it has a **defined state transition**.

A useful artifact record might look like:

```yaml
artifact:
  id: normalized-customer-v1
  state: drafting
  owner: parser-worker

inputs:
  - purchase-order-ocr-v1

outputs:
  schema: schemas/normalized-customer-v1.json

acceptance:
  tests:
    - tests/test_customer_schema.py
    - tests/test_country_codes.py
  examples:
    - fixtures/customer-uk.json
    - fixtures/customer-de.json

consumers:
  - ship-to-matcher
  - order-validator
```

The state is not "someone is working on it."

It might be:

```text
missing
  ↓
contracted
  ↓
implemented
  ↓
verified
  ↓
accepted
```

That is much easier for both people and agents to reason about.

## Why I think this matters more with AI workers

Human software teams cannot scale worker count infinitely. Hiring, onboarding, communication, and coordination are expensive.

AI changes that constraint.

I can start several coding sessions much faster than I can add several engineers to a team.

That exposes a different problem:

```text
20 available workers
        ↓
12 blocked by dependencies
        ↓
5 editing the same files
        ↓
2 duplicating work
        ↓
1 useful merge
```

More agents do not automatically create more throughput.

If I want real parallelism, I have to deliberately create **independent work surfaces**.

Artifact contracts are one way to do that.

## The producer can be missing and the consumer can still be real

Here is the simplest useful pattern.

First, define the contract:

```json
{
  "$id": "normalized-order-v2",
  "type": "object",
  "required": ["order_id", "currency", "items"],
  "properties": {
    "order_id": {"type": "string"},
    "currency": {"type": "string", "minLength": 3, "maxLength": 3},
    "items": {"type": "array"}
  }
}
```

Then commit a fixture:

```json
{
  "order_id": "PO-1042",
  "currency": "GBP",
  "items": [
    {"sku": "ABC-1", "qty": 4}
  ]
}
```

Now the downstream worker can build something real:

```python
from pathlib import Path
import json

order = json.loads(
    Path("fixtures/normalized-order-v2.json").read_text()
)

result = validate_and_route(order)

assert result.currency == "GBP"
assert result.route == "uk-order-flow"
```

Later the real parser replaces the fixture.

If the real parser satisfies the contract, the downstream code should not need to care.

If it does care, that is useful information: the contract was incomplete.

## Acceptance artifacts matter as much as implementation artifacts

This is the part I think traditional task boards under-emphasize.

A code file existing is not the same thing as the artifact being accepted.

For a meaningful artifact, I want the evidence to travel with it.

```yaml
acceptance:
  source_revision: "git-sha"
  required_checks:
    - unit-tests
    - contract-tests
    - security-review
  evidence:
    - artifacts/test-report.json
    - artifacts/review.md
  accepted_by:
    - lead-review
```

That makes "done" reconstructable.

An agent cannot simply say "tests passed" and move on. The exact artifact version and the evidence that applies to that version have to line up.

## Where the idea came from

One of the things that pushed me toward this mental model was Apple's [DiffuCoder research](https://machinelearning.apple.com/research/diffucoder).

DiffuCoder is a diffusion-style code model. Apple's paper describes denoising over an entire sequence, with global planning and iterative refinement rather than requiring conventional strictly left-to-right generation.

That paper is **not** a project-management paper, and I do not want to pretend it proves artifact-first development.

The spark for me was more abstract:

**What changes when order is no longer assumed to be strictly sequential?**

If code generation itself can explore a less rigid generation order, what parts of software delivery are sequential only because our process assumes they have to be?

That led me back to interfaces, fixtures, contracts, build graphs, and eventually this artifact-first framing.

## The important caveat: some dependencies are real

You cannot schema your way out of every dependency.

Two components may share:

- a transaction boundary;
- a latency budget;
- a state machine;
- a locking strategy;
- a migration order;
- a hardware constraint;
- a security boundary.

Those integrations still need real integration work.

The mistake would be to confuse "we wrote an interface" with "the system is decoupled."

Artifact-first development is not zero-dependency development.

It is a way to ask:

**Which dependencies can be transformed from "wait for implementation" into "agree on a verifiable contract"?**

Even a partial answer creates more parallelism.

## The project becomes a graph, not a flat backlog

The end state I want is a machine-readable artifact graph:

```text
OCR contract ───────┐
                    ├──→ normalized order ──→ validation report
catalog contract ───┘           │
                                ├──→ ship-to decision
                                │
                                └──→ audit evidence
```

Then a scheduler can ask:

- which artifacts are missing;
- which contracts are stable;
- which artifacts are independently buildable now;
- which workers would collide on the same files;
- which consumers can start from fixtures;
- which artifact states block a milestone.

That is a much more useful question than "what ticket is next?"

## I am now using this idea in SwarmAI itself

This is no longer only a thought experiment for me.

In SwarmAI, I have started treating artifacts as the canonical project state and deriving implementation packets from artifact gaps. Architecture documents, contracts, evidence protocols, implementation slices, and verification results can advance independently when their contracts do not conflict.

That does not eliminate integration.

It gives the integration work a more explicit shape.

For now, I am deliberately stopping this first public series here. The next stage of the experiment gets into orchestration, larger worker pools, and infrastructure, but I want more measured evidence before I write about those pieces as finished systems.

## What I may open-source

If the pattern continues to work, I want to publish a tiny artifact-management layer:

```text
artifacts/
├── registry.schema.json
├── registry.json
├── examples/
│   ├── api-contract.yaml
│   ├── benchmark.yaml
│   └── acceptance-evidence.yaml
└── tools/
    ├── ready.py
    ├── validate.py
    └── graph.py
```

Not another giant project-management platform.

Just enough structure to let people test the idea:

**define the pieces first, define how they connect, then let workers build as many pieces in parallel as the contracts safely allow.**
