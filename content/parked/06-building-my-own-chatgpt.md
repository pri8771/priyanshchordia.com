---
title: "Building My Own ChatGPT: One Interface, Many Models, My Own Inference"
slug: "building-my-own-chatgpt"
date: "2026-09-20"
summary: "Once models are providers instead of destinations, the interesting product becomes the router, memory, tools, and interface around them."
series: "Own Your AI Stack"
status: "draft"
---

If I already have multiple AI providers and a local inference server, why should I start every task by deciding which chatbot website to open?

That is the motivation for the next layer: my own chat interface.

Not my own foundation model.

My own control surface.

## The UI is the easy part

At a high level:

```text
                 personal chat UI
                        │
                  request router
                        │
         ┌──────────────┼──────────────┐
         │              │              │
      local         hosted/free      premium
    inference         capacity        models
         │              │              │
         └──────────────┼──────────────┘
                        │
                 tools + projects
```

The interesting parts are routing, durable context, tool access, and observability.

A text box is not the hard part.

## One important constraint: subscriptions are not automatically APIs

This is easy to get wrong.

Paying for a consumer ChatGPT, Claude, or other subscription does not automatically mean a custom application can programmatically spend that subscription as API credit.

My app has to use supported APIs, connectors, local endpoints, or explicit worker integrations.

That makes provider abstraction important.

The application should not assume every "AI I can use" has the same transport.

## Normalize the request before choosing the provider

I want the conversation layer to produce a provider-neutral request:

```json
{
  "project": "swarmai",
  "intent": "implementation",
  "risk": "medium",
  "messages": [
    {
      "role": "user",
      "content": "Implement the next authorized task."
    }
  ],
  "tools": ["github"],
  "budget": {
    "prefer_local": true,
    "allow_premium": true
  }
}
```

Then the router chooses a provider.

A simplified API could look like:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    provider = router.choose(
        intent=request.intent,
        risk=request.risk,
        budget=request.budget,
    )

    response = await provider.chat(
        messages=request.messages,
        tools=request.tools,
    )

    return {
        "provider": provider.name,
        "response": response,
    }
```

The UI does not need to care which model answered.

## Project memory should not become another giant chat transcript

The repo-centric idea still applies.

If a conversation is attached to a software project, the interface should be able to load the project's current state rather than replay every message I have ever exchanged with it.

Something like:

```python
context = project_context.load(
    files=[
        "AGENTS.md",
        "docs/PROJECT_MEMORY.md",
        "docs/coordination/STATE.json",
    ]
)
```

That creates a nice symmetry.

My interactive chat and my background workers can use the same project context.

## Models become infrastructure

At that point I stop thinking:

"Which chatbot is my main chatbot?"

I start thinking:

"Which provider should service this request?"

That opens the door to policies such as:

- local model for cheap classification;
- hosted free capacity for general work;
- strong reasoning model for architecture;
- different provider for independent review;
- specialized coding worker for repository edits.

The interface becomes mine. The models remain replaceable.

## The end state I want

I want to be able to type:

```text
Finish the next verified SwarmAI milestone.
```

The system should know which project I mean, inspect current state, decide whether the request belongs in chat or in a background worker, allocate inference, and show me evidence when the work is complete.

That is much closer to an operating layer for AI work than a clone of a chatbot.

This post becomes much more interesting once the local inference server is live, because then I can publish the real routing traces and cost breakdown instead of architecture diagrams alone.
