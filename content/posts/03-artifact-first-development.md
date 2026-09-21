---
title: "Artifact-First Development: What If Software Could Be Built Like Lego?"
slug: "artifact-first-development"
date: "2026-09-20"
summary: "The dependency does not have to be another team's implementation. Sometimes it can be an explicit contract for the artifact they must produce."
series: "Own Your AI Stack"
status: "draft"
---

I keep coming back to a simple question:

What if a software project were treated less like a sequence of tasks and more like a collection of artifacts that have to fit together?

Traditional planning often becomes:

```text
A → B → C → D
```

B waits for A. C waits for B. Add more developers or AI agents and they spend more time waiting.

But sometimes B does not actually need A to be finished.

B needs to know exactly what A will produce.

That is a different dependency.

## Move the dependency from implementation to contract

Suppose Artifact A is a customer parser and Artifact B is a validator.

The validator does not need the parser's code.

It needs the parser's output contract:

```json
{
  "customer_id": "string",
  "name": "string",
  "country": "ISO-3166-1 alpha-2",
  "confidence": 0.0
}
```

Now the validator can be built against a fixture before the parser exists.

```python
def validate_customer(customer):
    assert customer["customer_id"]
    assert len(customer["country"]) == 2
    assert 0 <= customer["confidence"] <= 1
    return customer
```

The parser team now has a clear obligation: produce that artifact.

The validator team has a clear assumption: consume that artifact.

Those pieces can move in parallel.

## The artifact should carry its own acceptance contract

I like the idea of defining each meaningful output with something close to this:

```yaml
artifact:
  id: normalized-customer-v1
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

Now "done" means more than "someone wrote the code."

The artifact has a shape, examples, tests, and consumers.

## This is not zero-dependency development

There is a dangerous oversimplification here.

You cannot make every software dependency disappear.

If two components share a database transaction, timing behavior, state machine, or performance constraint, an interface definition does not make the integration free.

Artifact-first development is not magic parallelism.

It is an attempt to identify dependencies that can be moved earlier into explicit contracts.

That is still valuable, especially when workers are cheap.

## The idea clicked for me while reading about diffusion code models

One of the things that nudged this mental model was Apple's work on diffusion-style code generation.

Apple's [DiffuCoder research](https://machinelearning.apple.com/research/diffucoder) describes masked diffusion models whose denoising process operates over an entire sequence and can use global planning and iterative refinement rather than being restricted to conventional left-to-right generation.

That paper is not a project-management methodology, and I do not want to pretend it proves this idea.

The interesting spark for me was simpler:

What changes when order is no longer assumed to be strictly sequential?

Software projects have the same question at a different layer.

## A producer can be missing and the consumer can still be real

A consumer can start with a fixture:

```python
from pathlib import Path
import json

customer = json.loads(
    Path("fixtures/normalized-customer-v1.json").read_text()
)

result = match_ship_to(customer)

assert result.ship_to_id == "100042"
```

Later, replace the fixture with the real producer.

If the producer satisfies the same contract, the consumer should not care.

That is the Lego analogy: the connection surface matters more than how the piece was manufactured.

## This becomes more interesting with AI workers

Human teams cannot infinitely parallelize because coordination is expensive.

AI changes the worker-supply side of the equation. I can start many sessions much more cheaply than I can hire many engineers.

That makes a different bottleneck visible:

**dependencies become expensive.**

If I have twenty available workers but twelve of them are waiting for another task to finish, the worker count is meaningless.

So my project-management question becomes:

How much of the dependency graph can I replace with stable contracts, fixtures, schemas, tests, and acceptance artifacts?

## The project itself becomes a graph of artifacts

Eventually I want a machine-readable view like:

```text
OCR artifact ───────┐
                    ├─→ normalized order ─→ validation report
customer catalog ───┘           │
                                └─→ ship-to decision
```

A worker should be able to ask:

- which artifacts exist;
- which are missing;
- which contracts are stable;
- which consumers can start now;
- which integrations need real evidence.

That is much more useful than a flat backlog when dozens of workers are available.

I am experimenting with this inside my own projects now. If the pattern survives real integration work, I want to publish the schemas, task format, and artifact graph conventions as a reusable template.
