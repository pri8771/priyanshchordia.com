---
title: "My phone was the only thing that knew what it was doing"
slug: "my-phone-noticed"
date: "2026-11-21"
summary: "Three tries, zero messages delivered, and a security check I did not write."
series: "Running a company on AI agents"
status: "draft"
---

> **DRAFT.** Not yet published. This page is a working copy for review and is not indexed by search engines.

*Three tries, zero messages delivered, and a security check I did not write.*

At about 2:26 PM EST on November 23, I asked for a new blank bot running on a local model. His name is Mr. Luthor. I chat with my bots through a phone app, which connects to a server address saved in it. This one was supposed to be a new bot I could message.

By about 3:03 PM, I had a progress report:

> its there, but cannot load messages

The log was more specific. The phone had signed in and requested a new chat connection six times in ten seconds. No conversation was ever created.

Quite a blank bot.

At about 3:54 PM, I reported:

> And I still can't message Mr. luthor there.

My AI assistant found that the phone had never reached the new bot's server. Every sign-in from the phone had gone to the old server, including the last one at 3:52 PM. I had been checking whether the new bot worked through a connection that had never reached him.

The assistant pointed the address my phone already knew at the new server and moved the old dashboard to a different port. The address was familiar. What answered it was now different. Its note on the fix included this:

> Not checked: the phone itself.

The phone was available to contribute a finding.

At about 4:03 PM, I read its error into dictation:

> It's still not working. Do I need a new link? The Hermes host at this address reports a different identity than the one you are connected to. Check the address in the Hermes connection. I sent a chat and said hi. Not sure what happened. It glitched.

![my three reports, 3:03, 3:54 and 4:03 PM, then the phone's error](/blog-media/my-phone-noticed/different-identity.gif)

It had, in fact, checked.

This is trust on first use, the same idea as SSH's known_hosts warning. The client remembers the identity it first saw at an address and refuses when a different one answers. From the phone's side, a different server answering at a trusted address is exactly what an attack looks like. The app was right. The repair is to give the new thing a new address, not make the warning disappear.

I had called this a glitch. That security check was the best-engineered part of my set-up, and I did not write it. The only component that behaved correctly all afternoon was the one refusing to work.

The next fix gave Mr. Luthor his own address, to be added in the app as a new server. The hand-over note written minutes later said:

> never point his old address at it again.

It also supplied the current result:

![the two notes: Not checked: the phone itself. and The phone has not yet signed in there.](/blog-media/my-phone-noticed/not-checked.gif)

As of this draft: three tries, zero messages delivered to Mr. Luthor from my phone.

