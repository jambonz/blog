---
title: "Initial impressions of Gradium TTS"
date: "2026-08-13"
description: "Latency and voice-quality notes from testing Gradium's streaming TTS on jambonz."
author: "Kevin Jombe"
tags: ["gradium", "tts", "latency", "streaming"]

---

![Gradium recording widget screenshot](./Gradium-Widget.png)

We recently added Gradium as a TTS vendor on jambonz and I spent an afternoon
testing it. Gradium advertises "highly expressive streaming, precise
word-level timestamps, custom pronunciation dictionaries, and enterprise-grade
scalable concurrency." I wanted to see how the streaming and latency claims
hold up on a real call.

## The setup

Two inbound applications on jambonz.cloud, both using the same Gradium voice
(voice id `bwRhQrJel4IuvxLF`, default model, `en`):

- An echo app built with `say` + `gather` in a loop, transcribing with
  Deepgram Flux and reading the transcript back.
- An `agent`-based app: Deepgram nova-3-general for STT, GPT-4o for the LLM,
  and Gradium for synthesis; barge-in enabled, no tools configured.

## Latency

Echo app — first byte timings from a sample session:

- Fastest: 356 ms
- Median: 392 ms
- Slowest: 665 ms

Five of six measurements landed between 356 ms and 432 ms. The 665 ms outlier
occurred on the last prompt and didn't correlate with text length. Application
hook RTT was flat at ~277–280 ms, so the variance appears to be on the TTS
side, not the app server.

Agent verb — streaming makes a real difference. First byte dropped to ~220 ms
under the same conditions (ElevenLabs Flash v2.5 was ~274 ms). Session
averages across that call were roughly: 676 ms STT, 667 ms LLM, 220 ms TTS.

The practical takeaway: using the `agent` verb and streaming TTS saves ~170
ms versus a non-streaming `say` path. At these latencies, 170 ms can be the
difference between a natural turn and a noticeable pause.

## Voice quality

Gradium exhibits a wide depth of emotion, realistic cadences and even subtle
breathing sounds. In my tests the agent often felt very natural — close to
passing a casual Turing-like check for short interactions.

## Conclusions

Gradium's streaming TTS is fast enough for production conversational use. At
~220 ms to first byte through `agent` it is competitive with the fastest
vendors on the platform and worked cleanly with GPT-4o in my tests. The
non-streaming `say` path is slower but still fine for IVR and notifications,
especially when combined with jambonz's TTS caching.

If you'd like to try this yourself on jambonz.cloud, add a small echo or
agent app and point it at Gradium. Below are sample assets you can drop into
this post's folder:

- `Gradium-Widget.png` — screenshot or short video of the recording widget
- `sample-echo.mp3` — recording from the echo app
- `sample-agent.mp3` — recording from the agent session

Embedding the jambonz.cloud recording widget here is useful for readers who
want to reproduce the test — if you'd like, I can capture a short video of
the widget and include it in this folder.

---

If you want me to add recordings, drop the `.mp3` and image/video files into
this folder and I'll commit them to the PR.
