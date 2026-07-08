---
title: "jambonz v11: New Media Server Doubles Capacity"
date: 2026-07-06
description: "jambonz v11 replaces FreeSWITCH with a custom media server, more than doubling capacity and improving voice AI platform performance."
author: "Dave Horton"
tags: ["jambonz-v11", "voice-ai", "media-server", "freeswitch", "scalability"]
faq:
  - question: "Why did jambonz remove FreeSWITCH?"
    answer: "FreeSWITCH is a general-purpose media server that jambonz only used a fraction of, and the unused overhead limited how far a single cluster could scale. Removing it let us build something scoped to exactly what jambonz needs."
  - question: "How much faster is jambonz v11?"
    answer: "It's about capacity, not raw speed. In a like-for-like test on identical 4-vCPU hardware, the new media server sustained more than twice the concurrent sessions FreeSWITCH did (around 750 versus 290 on a stripped-down playout app) using about half the CPU per call and a fraction of the memory. Real-world capacity depends on what each call actually does, but on the same hardware a cluster handles close to double the traffic before you add servers."
  - question: "Does jambonz v11 still support self-hosted deployments?"
    answer: "Yes. Self-hosted voice AI scalability was the main motivation for this release. jambonz runs a large share of its traffic on infrastructure customers manage themselves, and this is where the capacity gains matter most."
  - question: "Will the OSS version of jambonz adopt the new media server?"
    answer: "No, the newer/faster media server will be available only to commercial customers. The open source (0.x) software stream will continue to rely on the legacy Freeswitch implementation."
---

jambonz version 11 is our biggest release yet. It introduces new vendor choices for LLM, STT, and TTS, simplified voice agent handoff tools, support for arm64, and the latest turn-taking models from Krisp. Underneath it sits a rewritten media server that roughly doubles how much a jambonz cluster can carry.

We've always built [jambonz](https://www.jambonz.org/) around scalability. For most of the platform's life, FreeSWITCH was the limiting factor. In v11, we replaced it.

## Why We Removed FreeSWITCH

FreeSWITCH is a general-purpose media server, and a solid one. Developed for a broad range of use cases, it's a bit like a swiss army knife replete with a voluminous set of features.  For our purposes, though, many of those features were unused and some of them limited the scalability of the jambonz platform.

So, for years, when a single jambonz cluster hit its ceiling, the answer was to add more feature servers rather than raise the ceiling itself.

## A Purpose-Built Media Server for jambonz

We wrote our own media server, scoped only to what jambonz needs:

- Written in Go for performance and improved memory management
- Stream-lined command interface that is purpose-built to speed jambonz call setup and handle more calls/sec
- Minimal configuration: no dialplans or complex configurations 
- Much smaller memory footprint and much easier to build
- Built-in cli for observability and management

Building our own media server around exactly what jambonz needs was the logical next step for us to improve the scalability and feature set of jambonz.  

In version 11 we've done it.

## How Much Did Capacity Improve in jambonz v11?

To measure the media server in isolation, we ran the old and new servers head-to-head on the **same 4-vCPU hardware**, driving each with the **identical application** and ramping concurrent calls until the box gave out.

| | FreeSWITCH | New media server |
| --- | --- | --- |
| Concurrent sessions before trouble | ~290 | ~750 |
| Behaviour at the limit | Collapses — calls start dropping | Plateaus — never drops calls in progress |
| CPU per call (at 250, both healthy) | ~1.4 cores | ~0.7 core (about half) |
| Memory | 494 MB base + ~5–10 MB/session | 39 MB base + ~1 MB/session |
| Docker image (compressed) | ~735 MB | ~131 MB (approx. 6 times smaller) |

On identical work, the new server carried more than twice the concurrent session (closer to 2.5×) at roughly half the CPU per call and a fraction of the memory. Just as important is *how* each behaves at the ceiling: the old server hit a wall and began timing out calls, while the new one simply stops accepting new calls and keeps the ones it has running cleanly. The container image shrank too, from about 735 MB to 131 MB (roughly 6 times smaller) which means faster pulls, quicker cold starts, and less to move around when you're autoscaling.

**A word on what these numbers mean.** This was a deliberately minimal application (answer the call, play a short cached prompt, hang up) over G.711, with no speech recognition, no LLM, and no turn-taking. We built it that way on purpose, to isolate the media engine and compare the two servers on exactly the same work. A production voice-AI agent does far more per call (live transcription, streaming synthesis, turn detection, often recording) so its absolute per-box capacity lands well below these figures. How many sessions a box holds depends heavily on the application; treat ~750 as the ceiling for the lightest possible workload, not a promise for a full agent. (On jambonz.cloud we comfortably run 500-600 concurrent calls on a 4cpu arm64 c7g.xlarge instance type feature server).

What *does* carry across workloads is the shape of the comparison (about half the CPU per call, a fraction of the memory, and graceful degradation instead of collapse) and those hold whether a call is doing a little or a lot. That's why we describe the gain as *roughly doubling* what a cluster can carry: it's the conservative, workload-independent read of a bigger measured difference.

For self-hosted customers, that turns into one of two things:

- Fewer instances running the same call volume
- The same instances carrying more calls at the same latency

**Either way, that's a smaller infrastructure bill for the same amount of traffic.**

jambonz runs across six continents and handles millions of minutes a month, most of it on hardware customers manage themselves. When a box handles twice the calls, customers need half as many boxes to hit the same volume. That's real money on a self-hosted deployment.

## Everything Else in This Release

There's more in v11 beyond the media server rewrite:

- **New turn-taking models from** [**Krisp**](https://krisp.ai/), which improve how the platform tells a caller finishing a thought from a caller just pausing
- **Timeout handling for speech-to-speech models**, closing a gap some of you came to jambonz specifically to avoid
- [**Arm64**](https://en.wikipedia.org/wiki/AArch64) **support**, alongside amd64, worth a look if you're comparing instance costs for a [self-hosted deployment](https://docs.jambonz.org/self-hosting/overview)

We'll be covering session observability, voice agent handoff, and call center coach mode in follow-up posts later this month.

## What v11 Means for Self-Hosted Voice AI

As deployments grow, capacity becomes just as important as features. v11 raises the number of calls a single box can handle before additional hardware is required, making it easier to scale without expanding infrastructure too soon.

## Availability

**jambonz v11 is available now on [jambonz.cloud](https://jambonz.cloud/).** Support for self-hosted deployments follows shortly.
