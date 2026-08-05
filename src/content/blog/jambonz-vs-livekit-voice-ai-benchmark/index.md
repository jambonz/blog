---
title: "jambonz Outperforms LiveKit 10x in Voice AI Concurrency"
date: 2026-08-06
description: "A reproducible voice AI scalability benchmark measures how many concurrent voice AI calls jambonz and LiveKit sustain on identical hardware."
author: "Dave Horton"
tags: ["benchmarks", "livekit", "voice-ai", "scalability", "self-hosting"]
whitepaper:
  title: "jambonz Outperforms LiveKit 10x in Voice AI Concurrency"
  file: "/whitepapers/jambonz-vs-livekit-voice-ai-benchmark.pdf"
  description: "All eleven configurations tested, latency analysis, cost derivation, and every limitation we found in our own methodology."
faq:
  - question: "How many concurrent voice AI sessions can jambonz and LiveKit handle?"
    answer: "On one 8-vCPU instance, jambonz sustained 250 concurrent voice-agent sessions and LiveKit sustained 25 — about 31 sessions per vCPU against 3, a tenfold difference, measured against the same quality bar of under 0.5% failed calls and turn latency within 25% of baseline."
  - question: "Why does LiveKit use more CPU per call than jambonz?"
    answer: "LiveKit forks a dedicated process for every call, while jambonz runs one shared media server process that carries every call on the box. Per-process sampling shows roughly 0.11 CPU cores per session for LiveKit against about 0.014 for jambonz — an eight-fold difference in the cost of carrying one call."
  - question: "Does turn detection explain the difference?"
    answer: "No. We removed turn detection as a variable by routing both platforms through the same off-box turn events. jambonz's ceiling more than doubled once its native detector was removed; LiveKit's ceiling didn't move."
  - question: "Is LiveKit a poor choice for voice AI?"
    answer: "No. LiveKit does things jambonz doesn't, including video, multi-party rooms, and browser and mobile SDKs, none of which were tested here. Below roughly 100 concurrent sessions the compute gap won't matter much."
---

If you're running [voice AI agents on your own infrastructure](https://jambonz.org/self-hosting), the question that matters is simple: **How many concurrent calls can one server handle before it falls over?**

So we built an open-source load-testing harness to find out. We ran the same conversation against jambonz and LiveKit, on identical hardware, and watched what happened.

## How Many Concurrent Voice AI Sessions Can jambonz and LiveKit Handle?

On one 8-vCPU instance, jambonz sustained 250 concurrent voice-agent sessions. LiveKit sustained 25. That's about 31 sessions per vCPU against 3, a **tenfold difference**, measured against the same quality bar: under 0.5% failed calls and turn latency within 25% of baseline.

We tested LiveKit **seven different ways**, including [its own documented reference topology](https://docs.livekit.io/intro/overview/) with dedicated agent servers, and its efficiency never left a narrow range of 2.2 to 3.1 sessions per vCPU. More hardware scaled its capacity. It didn't change its efficiency.

## Why Does LiveKit Use More CPU Per Call Than jambonz?

The two platforms handle a call differently at the architecture level. LiveKit forks a dedicated process for every call. jambonz runs one shared media server process that carries every call on the box.

Per-process CPU sampling shows LiveKit spending about 0.11 CPU cores per session inside that per-call process, against about 0.014 cores per session in jambonz's shared process. That's roughly an **eight-fold difference** in the cost of carrying one call, and it's the mechanism behind the capacity numbers above.

## Does Turn Detection Explain the Difference Between LiveKit and jambonz?

No. We removed turn detection as a variable by routing both platforms through the same off-box turn events, so neither ran local turn-detection inference.

jambonz's ceiling **more than doubled** once its native detector was removed. LiveKit's ceiling didn't move. That tells you the per-call process model, not the turn detector, is what's setting LiveKit's limit.

## Is LiveKit a Poor Choice for Voice AI?

No, and this benchmark doesn't claim that. LiveKit does things jambonz doesn't, including video, multi-party rooms, browser and mobile SDKs. None of that was tested here, so none of it should be dismissed because of a capacity number.

Below roughly 100 concurrent sessions, LiveKit is a sound choice. This compute gap won't matter much. Above that, though, and especially into the hundreds or thousands, the architecture starts deciding your server bill and your ops burden.

## Was LiveKit Configured Fairly?

We treated tuning LiveKit as part of the work rather than an afterthought. We found and fixed a config issue that had capped it at 14 sessions, [posted our setup to LiveKit's community forum](https://community.livekit.io/t/looking-for-tuning-recommendations-for-single-server-self-hosted-lk-for-sip-inbound/1709), and applied every recommendation we got back. LiveKit's deployment docs size an agent server at 10 to 25 concurrent jobs for the hardware we used.

Our numbers land right where [their own documentation](https://docs.livekit.io/deploy/custom/deployments/) says they should.

## Read Our Full Benchmark

The full paper covers all eleven configurations tested, latency analysis, cost derivation, and every limitation we found in our own methodology. The load generator, vendor mocks, and raw data are public.
