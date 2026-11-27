---
title: "I gave my chief-of-staff bot one line of instructions"
slug: "five-word-soul-file"
date: "2026-11-10"
summary: "Five words, 28 bytes. Everything I add costs tokens every conversation."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*Five words, 28 bytes. Everything I add costs tokens every conversation.*

I build automation and AI agent systems. The first bot I built for my company is a chief of staff, called SuperBot. Every bot has a soul file: a short text it reads at the start of every conversation that says who it is and what to care about. After its first identity file was emptied, SuperBot's held a single line, exactly as I asked:

> always listen to your owner

Five words. Twenty-eight bytes, counting the newline. I had told my AI assistant: "Other than that nothing."

![the whole file](/blog-media/five-word-soul-file/five-word-soul.gif)

I chose it on purpose. The bot reads that file at the start of every single conversation, so every word I add is paid for in tokens every time, whether the bot is writing a plan or answering a sum. A short file is cheap to run and easy to review: any change is a one-line difference I can read in a second.

So the rule I follow is: identity goes in the file, jobs go in the prompt. A one-off job, like "make the other bots", is told to the bot for that conversation and never written into the file. I said that to my assistant in nearly those words: "We're not putting that in the Superbot soul file. We're just going to tell it that it needs to do this."

The file did grow, because I kept adding rules. It is now 905 bytes: a two-line introduction and eight numbered rules. Rule one is still the original line, with "Do as he says" added after it. The business motto, "take from open source", sits inside the build rule. Rule seven is the one about learning:

> Always learn. Always find ways to become better and more efficient, and continue to evolve.

Each addition is a numbered decision in my log with my exact words next to it, so I can say when a line arrived and who asked for it. The file went from 28 bytes to 905 in about a day. Every one of those 877 bytes is paid for in tokens at the start of every conversation, which is why I keep reading it.

The first check after that was a sum: my assistant asked the bot one, and the hosted model answered it with no fallback to the local model.

