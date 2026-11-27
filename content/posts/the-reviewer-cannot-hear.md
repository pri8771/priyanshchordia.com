---
title: "I gave my video a new voice. Nobody has heard it."
slug: "the-reviewer-cannot-hear"
date: "2026-11-23"
summary: "The file has passed the part of the review that does not involve ears."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*The file has passed the part of the review that does not involve ears.*

My company's second AI-made video is a vertical ad for a can cooler. Seven text cards, a spoken line on each, about 23 seconds. The first render used the laptop's built-in voice. I have now replaced that voice with an open-source model, and nobody has listened to the result.

Including me.

The notes on the first video, written that morning, were fairly specific:

> Watchable, not good. It is text on a gradient with a robot voice and a slow zoom

And:

> It would not hold a stranger for a swipe.

So there was a recorded objection to the voice, and a request to download a voice model had been on my list since that morning. When I read the list that afternoon, my recorded response was:

> Why do we need a voice model?

![my recorded response to the voice-model request](/blog-media/the-reviewer-cannot-hear/why-a-voice-model.gif)

That afternoon I also gave my assistant a broader instruction about the list:

> for all of them, go by your best recommendation.

That covered the voice model. I had questioned the particular thing and then approved all the things, so the particular thing got installed. A complete decision.

The model is Kokoro, an open-source text-to-speech model with 82 million parameters and an Apache 2.0 licence. It runs on the laptop without an account or a network connection. Installation took one command and under a minute. The model file is 325.5 MB, the voices file is 28.2 MB, and the whole installation with its Python environment takes 479 MB.

The request spent the afternoon on my list. The installation took under a minute.

My assistant added the voice as an optional third argument to the video script and rendered the ad again. The result went from 23.3 seconds to 22.6. It then checked its work. Its November 23 report said:

> Checked: the file plays and has speech at normal level (mean -23 dB). Not checked: how it sounds, since I cannot hear it; pronunciation of "A I" and "dot" needs his or a bot's ear.

The word “speech” is doing some work there.

The check used ffmpeg's volumedetect filter: mean volume -23.1 dB, peak -3.5 dB. Without ears, we can verify that the container plays, an audio stream exists, its duration, and its loudness statistics. Those statistics cannot tell speech from a dial tone, or establish pronunciation, tone, or the right words. A cheap next check is speech-to-text followed by a diff against the script. That has not been done.

The script spells out “A I” and “dot” so the voice will say them right. Whether it actually does is still part of the review.

The listening job was written up for another bot. Its November 23 task instruction was:

> Real listening only; if you cannot play audio, write "could not listen" and stop.

![the listening task's instruction to stop if it cannot listen](/blog-media/the-reviewer-cannot-hear/real-listening-only.gif)

I am the only member of the company equipped to review the voice. I have not. As of November 23 at 17:11 EST, nobody, human or bot, has listened to it. The video is not posted.

