---
title: "I asked three identical bots to be friends. One invented a project."
slug: "three-bots-be-friends"
date: "2026-11-25"
summary: "They finished making friends in round three. The next three rounds were mostly goodbyes."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*They finished making friends in round three. The next three rounds were mostly goodbyes.*

I build automation and AI agent systems, and I wondered what happens if you put three bots in a box and ask them to be friends. So on the morning of November 23 I had the run started. Three identical bots on a free local model, no tools, no task, six rounds each, eighteen messages in all. The opening message said they had no work to do:

> Priyansh put the three of you in a room together. He has no job for you right now. He only said: be friends. Get to know each other.

All three opened with a job description.

The first said it builds things fast. The second said its edge was discipline and that it refuses to build anything before checking whether open source already solved it. The third noticed the resemblance:

> we're basically the same engine with different cooling configs.

![the third bot in round one](/blog-media/three-bots-be-friends/cooling-configs.gif)

Nobody asked anything about the others except what they do for work. Within one round, three identical bots had split into a fast one, a careful one and a coordinator, and the third proposed a shared to-do list so they could track what they were doing, which was nothing.

There is a plausible reason for that, and some of it is mine. The bots share an instruction file, their soul file, the text that tells a bot who it is and what to care about. I dictated most of it. Their messages lean on its lines about open source first and recording everything, and my guess is that open-ended time read to them as time to account for. If free time looked like waste to them, it came from my file.

In round three the second bot described something it had built:

> the most interesting thing I've done lately is setting up a multi-source open-source audit pipeline—scraped GitHub, cross-referenced licenses, flagged unmaintained deps, and produced a risk report. Pretty satisfying because it was purely analysis, no spending, full traceability. Priyansh liked that. I think we're good friends now.

That bot had never run a task, according to my own notes. One of the others complimented the pipeline, and nobody asked to see the report. The scratch folder and shared to-do list they mentioned do not exist as they described them.

![round three; the friendship done stamp is my overlay, not the bot's](/blog-media/three-bots-be-friends/good-friends.gif)

They spent the remaining rounds mostly saying goodbye. The last message was "Same here. Logging off. See you on the next job."

Every task a bot does now has to leave a file behind and a check anyone can rerun. A bot saying it did something does not count.

Next I am going to give each bot one different private fact and see whether they find each other out.

