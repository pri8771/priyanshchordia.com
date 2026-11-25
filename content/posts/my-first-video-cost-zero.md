---
title: "My first AI-made video looks like a script made it"
slug: "my-first-video-cost-zero"
date: "2026-11-16"
summary: "A slow zoom, a robot voice and a written verdict before anyone posts it."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

A slow zoom, a robot voice and a written verdict before anyone posts it.

My first AI-made video is about three bots who spent the last three rounds mostly saying goodbye. The video itself is 30 seconds. I put a disclosure on every frame, and the plan calls for a written quality verdict before anyone posts the result. My team wrote the verdict that day. The short version was watchable, not good.

What made it into the video was a real result from the experiment. What made it onto the screen was text on a gradient. There are six text cards, and while the robot voice speaks, the text gets slowly closer. That is the extent of the camera work. There was no footage.

![A text card slowly enlarges against a gradient, with the AI disclosure visible.](/blog-media/my-first-video-cost-zero/slow-zoom.gif)

The whole pipeline is a text file of scenes in and an MP4 out. The script reads the scenes from a JSON file. The built-in macOS `say` command supplies the voice and Pillow, a Python image library, draws one PNG per scene. Then ffmpeg applies `zoompan` for the slow zoom and `concat` to join the scenes. Changing the video means changing the JSON. A bot can run it without a GPU and with just that one script to call.

The file checks out. It is 30.6 seconds long, 1080 by 1920, with H.264 video and AAC audio. It took about 20 seconds to render, end to end, with no paid tool. The file check can tell me all of that about the finished clip except whether somebody would keep watching. That part went in the written verdict.

The disclosure is part of the picture. Pick any frame from the finished video and the line is there. It covers the script, the voice and the images. I also checked YouTube’s official pages that day. YouTube requires its altered-content setting for realistic synthetic content. Its guidance also says mass-produced templated content is ineligible for ad revenue. Another platform’s help pages would not load, so its entry stayed unconfirmed.

As for whether somebody would keep watching, the phrase in the team’s verdict that day was “would not hold a stranger for a swipe” (`PIPELINE.md`). There is no music. The words on screen are the scene cards, so there are words to read but no captions timed to the words being spoken. Apart from the zoom, nothing moves.

The plan names Piper or Kokoro for a better voice. Either needs a model download. It also calls for real visuals or stock footage, music and word-timed captions. Those are still on the list. What I could already change was the subject. Video 002 was a can cooler product clip, drafted in minutes from the same script format. It runs 23.3 seconds.

