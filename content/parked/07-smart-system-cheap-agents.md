---
title: "AI Agents Don't Need to Be Brilliant. The System Around Them Does."
slug: "smart-system-cheap-agents"
date: "2026-09-20"
summary: "Cheap agents become more useful when the environment supplies contracts, tests, retries, independent review, and escalation."
series: "Own Your AI Stack"
status: "draft"
---

There is an expensive assumption hiding inside a lot of agent designs:

Every worker should be as smart as possible.

That makes sense if the worker is operating alone.

It makes less sense if the system can constrain the problem, validate the output, retry failures, and escalate only when needed.

My current hypothesis is that a good agent system should spend intelligence selectively.

## Put certainty outside the model when you can

Suppose I ask a model whether a parser is correct.

That is probabilistic.

Suppose I run 300 parser tests.

That is much less ambiguous.

So the worker loop should prefer deterministic evidence where available:

```python
candidate = worker.implement(task)

result = tests.run(candidate)

if result.passed:
    review = independent_reviewer.check(candidate)

    if review.accepted:
        accept(candidate)
    else:
        retry(candidate, review.feedback)
else:
    retry(candidate, result.failures)
```

The worker does not have to remember every acceptance criterion if the test harness already encodes it.

## Use expensive intelligence at the edges

A routing policy might deliberately escalate:

```python
def solve(task):
    result = small_model.try_task(task)

    if result.confidence >= 0.90 and tests.pass_for(result):
        return result

    result = medium_model.retry(task, previous=result)

    if tests.pass_for(result):
        return result

    return strong_model.solve(
        task,
        failure_history=result.history,
    )
```

The exact confidence number is illustrative. Model self-confidence is not a reliable truth signal by itself.

The important idea is the escalation ladder.

Cheap attempts are allowed only because something else verifies them.

## Multiple weak agents do not automatically become a strong system

This is the failure mode I most want to avoid with SwarmAI.

If I ask ten unreliable workers the same vague question and average the answers, I may simply get ten versions of the same mistake.

Parallelism needs diversity and verification.

Useful parallel patterns include:

- different implementations against one contract;
- independent research from different providers;
- adversarial review;
- generated test cases checked by a deterministic runner;
- competing plans scored against explicit requirements.

"More agents" is not the goal.

"More verified progress per unit of inference" is the goal.

## The environment can make the task easier

A worker given this:

```text
Fix the order parser.
```

has to infer almost everything.

A worker given this:

```yaml
goal: "Parse multi-line order items"
contract: docs/ORDER_ITEM_V2.md
fixtures:
  - fixtures/uk-001.txt
  - fixtures/es-014.txt
tests:
  - tests/test_multiline_items.py
do_not_change:
  - public API schema
acceptance:
  - all existing tests pass
  - new fixtures pass
  - independent review passes
```

is solving a much smaller problem.

That is the core idea.

Make the environment carry as much certainty as possible.

## This is why all the earlier pieces fit together

Repo-centric context gives workers shared memory.

Remote-worker hosts give me capacity.

Artifact-first development reduces blocking dependencies.

SwarmAI coordinates the worker pool.

Local inference makes cheap attempts more practical.

The personal chat/router gives me one control surface.

Tests, contracts, and review make the whole thing less dependent on one brilliant model.

The stack is becoming:

```text
human intent
    ↓
project context
    ↓
artifact / task contract
    ↓
worker routing
    ↓
candidate output
    ↓
deterministic tests
    ↓
independent review
    ↓
accept / retry / escalate
```

That is the system I am trying to build.

The interesting question is not whether a small model can beat a frontier model in isolation.

It is whether a deliberately engineered system can use lots of cheaper intelligence without letting error rates explode.
