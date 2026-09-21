---
title: "Building My Own Inference Server Because Free Tiers Aren't a Strategy"
slug: "building-my-own-inference-server"
date: "2026-09-20"
summary: "The next step after interchangeable model workers is owning a local OpenAI-compatible pool of inference for cheap background work."
series: "Own Your AI Stack"
status: "draft"
---

Once you start thinking of models as workers, you hit a very predictable problem.

Workers consume inference.

A lot of it.

I can move between ChatGPT, Claude, Cursor, Gemini, and other providers, but a large worker pool turns every provider limit into scheduling logic.

So I am building the next layer: my own inference server.

This article is a build log. I will replace the placeholders with measured throughput, power, concurrency, and model-quality results once the server is actually running.

## The goal is not to beat frontier models

I have no expectation that an old server with local GPUs will replace the strongest hosted models.

That is the wrong comparison.

The useful question is:

What percentage of my workload does not require a frontier model?

Examples:

- classify a task;
- summarize a log;
- extract structured fields;
- write a first-pass test;
- compare two small artifacts;
- convert a requirement into a checklist;
- run repetitive review passes.

If a local model can handle those jobs, premium inference becomes an escalation path instead of the default.

## Make the local server look boring

The best interface is one every existing tool already understands.

I want the local server to expose an OpenAI-compatible API shape:

```bash
curl http://inference.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-coder",
    "messages": [
      {"role": "user", "content": "Write tests for this parser contract."}
    ]
  }'
```

Whether the backend is vLLM, Ollama, llama.cpp, or something else should be a deployment decision.

The rest of my stack should see "an inference provider."

## Routing matters more than one model

A simple provider table can look like:

```yaml
providers:
  local-small:
    endpoint: http://inference.local/v1
    cost_class: owned
    strengths: [classification, extraction, simple-code]

  free-cloud:
    endpoint: provider-specific
    cost_class: promotional
    strengths: [general, research]

  premium-reasoning:
    endpoint: provider-specific
    cost_class: paid
    strengths: [architecture, ambiguity, escalation]
```

Then a scheduler can route based on task risk.

```python
def route(task):
    if task.risk == "low" and local.can(task):
        return local

    if free_cloud.available() and free_cloud.can(task):
        return free_cloud

    return premium
```

That is the economic reason I care about local inference.

Not because it is universally better.

Because it can absorb the boring work.

## The hardware I already own matters

I have a Dell PowerEdge R730 that is already part of my always-on environment.

That makes the experiment more interesting than a clean-room cloud benchmark.

The real build needs to answer:

- which GPUs are practical in the chassis;
- what models fit comfortably;
- how many concurrent workers can run;
- whether context/KV-cache pressure moves the bottleneck;
- how the server behaves under sustained load;
- how much power the whole system actually consumes;
- whether the quality is sufficient for the tasks I route locally.

I will publish those numbers instead of guessing them.

## "Free inference" needs an asterisk

If I already own the machine, local inference can have very low marginal software cost.

It is not literally free.

There is hardware, electricity, maintenance, cooling, and my time.

That distinction matters.

The comparison I care about is marginal cost per useful verified task, not marketing price per token.

## What I want to open-source

If this becomes stable, the reusable piece is not my exact server.

It is the routing layer and deployment contract:

```text
worker → model router → provider
                      ├─ local
                      ├─ free/promotional
                      └─ premium
```

A clean open-source version could let anyone register an OpenAI-compatible local endpoint next to hosted providers and define their own routing rules.

First I need real measurements.
