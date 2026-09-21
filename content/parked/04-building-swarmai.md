---
title: "Building SwarmAI: What Happens When 50 AI Workers Share One Project?"
slug: "building-swarmai"
date: "2026-09-20"
summary: "SwarmAI is my attempt to coordinate large numbers of temporary AI workers around shared state, artifact contracts, tests, evidence, and multiple inference providers."
series: "Own Your AI Stack"
status: "published"
internal_status: "working-draft"
---

Most agent frameworks start with a team.

A researcher. A developer. A reviewer. Maybe a manager.

I started with a different question:

**What if I had fifty useful workers available for a problem?**

Not fifty personalities.

Fifty pieces of temporary capacity.

Some may be strong reasoning models. Some may be small local models. Some may be coding agents. Some may exist for one task and disappear.

How do I make that useful instead of chaotic?

That question became SwarmAI.

This is a build-in-public description of what I am building, not a claim that I currently have a production-ready fifty-agent swarm running unattended.

## The unit should be work, not personality

I do not want to begin by inventing fifty permanent job titles.

I want the task to describe what it needs.

```yaml
task:
  id: parser-042
  goal: "Handle multi-line purchase-order items"
  risk: medium

requires:
  capabilities:
    - python
    - parsing
    - tests

inputs:
  - artifact: ocr-order-v2
  - file: docs/PARSER_CONTRACT.md

outputs:
  - implementation
  - tests
  - evidence

review:
  independent_provider: true
  max_retries: 2
```

The runtime can decide what worker is qualified and available.

Claude today. Cursor tomorrow. A local Qwen model for a small bounded task. A different provider for review. Multiple workers for competing approaches when that is actually useful.

The task is durable.

The worker is replaceable.

## A swarm needs constraints more than it needs more agents

Spawning agents is easy.

Preventing fifty agents from creating fifty incompatible versions of reality is the real problem.

The control layer needs boring things:

- explicit ownership;
- task leases;
- artifact contracts;
- shared repository state;
- conflict detection;
- cancellation;
- retry budgets;
- cost limits;
- provider admission rules;
- deterministic checks;
- independent review;
- evidence that binds to an exact source revision.

Conceptually:

```python
def run_task(task):
    worker = scheduler.assign(task)

    candidate = worker.execute(task)

    checks = verifier.run(candidate)
    if not checks.passed:
        return retry_or_escalate(task, checks)

    reviewer = scheduler.assign_reviewer(
        task,
        exclude_provider=worker.provider,
    )

    verdict = reviewer.review(candidate, checks)

    if verdict.accepted:
        return accept_artifact(candidate, checks, verdict)

    return retry_or_escalate(task, verdict)
```

The LLM is only one component in that loop.

That is a recurring theme in this series: I want certainty to live outside the model whenever possible.

## Why not just make one giant permanent crew?

Persistent roles are useful when the role itself has durable context.

But many software tasks do not need a permanent identity.

A project may need:

```text
2 architecture workers
        ↓
12 implementation workers
        ↓
4 independent reviewers
        ↓
1 expensive escalation
```

Then five minutes later it may need only one worker.

That suggests a scheduler and a worker pool rather than a fixed org chart.

My mental model is:

```text
human goal
    ↓
planning / decomposition
    ↓
artifact graph
    ↓
ready task queue
    ↓
qualified worker pool
    ↓
tests + evidence + review
    ↓
accepted artifacts
```

The swarm is elastic around the work.

## The repository remains the common ground

SwarmAI does not replace the repo-centric approach from the first article.

It depends on it.

If the controller dies, I want a replacement controller to reconstruct the important state from durable artifacts.

If a worker disappears, I want its lease to expire without losing the project.

If a provider becomes unavailable, I want another provider to pick up bounded work without requiring me to re-explain the project.

That means the system cannot keep its only copy of truth inside an orchestration process.

## The most useful test so far was a failure

This is where the project stopped being an architecture diagram for me.

I ran a real end-to-end mission against a real repository using actual local inference.

The worker inspected the real repo. The model call was real. The reviewer was real.

The mission still failed.

The model produced implementation text, but the system failed to turn that output into a material worktree change. The independent review rejected the result.

That failure is more useful than a green demo that quietly substitutes fixtures.

It exposed a missing artifact transition:

```text
model proposes implementation
            ↓
    materialize change
            ↓
      inspect diff
            ↓
     run regression
            ↓
    independent review
```

I had proved the top and bottom of the flow, but not the middle.

So the failure stayed a failure and became the next repair packet.

That is the behavior I want from SwarmAI: **no known-answer substitution, no fake success flag, no pretending a model response is the same thing as completed work.**

## Local inference is already part of the experiment

I have also run a smaller real routing proof with local Ollama models.

The proof used actual `gemma3:4b` and `qwen3.5:4b` model calls through the governed broker. I deliberately disabled one route to verify that the system selected a permitted alternative, then exhausted the allowed quota to verify that another request was denied instead of silently falling through to paid capacity.

The important result was not that a 4B model became magical.

It was that the broker could distinguish:

```text
configured
authenticated
healthy
allowed
within quota
qualified for this task
```

Those are different states.

A model appearing in a provider catalog does not mean I should route production work to it.

## "Free" is a policy, not a provider name

This matters because one of my requirements is zero surprise spend.

If a provider has a free tier, SwarmAI should not infer from a marketing page that a given account, model, and request is free right now.

The route has to be explicitly admitted.

Conceptually:

```python
def admit_route(account, model, task):
    assert account.authenticated
    assert model.health == "healthy"
    assert model.price_is_known
    assert model.current_cost == 0
    assert account.quota_remaining > 0
    assert model.qualified_for(task.kind)

    return True
```

If any of that is unknown, the safest route is "not admitted."

That makes the system less impressive in a demo and much more useful in real life.

## Artifact-first project management changed SwarmAI itself

As the project grew, I stopped treating the task list as canonical state.

The artifact registry became more important.

A version is not accepted because enough tickets are closed.

It is accepted when the required artifact set is in the right state with evidence bound to the right source.

That lets architecture, implementation, evaluation design, security work, and operational evidence progress in parallel without pretending they are interchangeable.

It also gives the swarm something machine-readable to reason about.

A worker can ask:

- what artifact am I advancing;
- what state transition is allowed;
- what evidence is required;
- what other artifacts block acceptance;
- what can I work on without colliding with another worker?

That is a much better substrate for a large worker pool than a vague backlog.

## Eventually SwarmAI should help build SwarmAI

One milestone I care about is self-hosted development.

Not uncontrolled self-modification.

A bounded loop:

```text
SwarmAI issue
    ↓
artifact gap identified
    ↓
SwarmAI creates bounded worker packets
    ↓
workers implement on isolated branches
    ↓
tests + independent review
    ↓
human-controlled integration gate
```

If SwarmAI cannot safely consume its own task, artifact, evidence, and review abstractions, that is a sign the abstractions are not good enough.

## Product versus my personal deployment

I am deliberately keeping these separate.

My personal deployment can know that I have a Mac, a Windows machine, an R730, particular subscriptions, and particular preferences.

The reusable product should not require any of that.

The product boundary I want is:

```text
SwarmAI core
├── artifact registry
├── scheduler
├── governed model broker
├── worker protocol
├── verification / review loop
└── durable evidence

optional integrations
├── GitHub
├── local inference
├── cloud providers
├── MCP / tool providers
└── deployment targets
```

My environment should be one configuration of SwarmAI, not SwarmAI itself.

## The metric I care about is not agent count

I can make a screenshot with 100 agents.

That does not tell me anything.

The metric I actually care about is closer to:

**verified artifact progress per unit of time, inference, and human attention.**

If doubling the worker count doubles merge conflicts and reviewer load, the swarm got worse.

If a local small model can solve a bounded task with deterministic verification, that may be more valuable than routing every request to a frontier model.

If an expensive model can resolve an ambiguity that would otherwise cause ten retries, that is also a win.

The scheduler needs to care about the whole system.

## Is SwarmAI open source?

Not yet.

The current repository is still under active development and I do not want to publish a bootstrap that encourages people to trust capabilities I have not verified.

But I do want the reusable core to become a real product rather than remain a private pile of scripts.

If enough people want to follow or test it, the first public release should include:

- the artifact registry format;
- worker/task contracts;
- the provider abstraction;
- zero-spend routing controls;
- local inference support;
- evidence/review gates;
- a self-hosted starter deployment.

That leads to the next layer of the stack: [why I am building my own inference server instead of treating provider limits as a permanent fact of life](/blogs/building-my-own-inference-server/).
