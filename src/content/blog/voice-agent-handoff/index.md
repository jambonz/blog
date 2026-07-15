---
title: "Voice Agent Handoff Made Simple in jambonz"
date: 2026-07-15
description: "Blind transfer, warm transfer with a private briefing, and a conferenced three-way handoff — all built into the jambonz voice agent, with no custom transfer code."
author: "Dave Horton"
tags: ["voice-ai", "handoff", "jambonz-v11", "agent", "transfer"]
draft: true
faq:
  - question: "What is the difference between blind (cold) transfer and warm transfer in voice AI?"
    answer: "A blind transfer connects the caller straight to the destination with no briefing — fastest, best for simple routing. A warm transfer puts the caller on hold while the voice agent reaches the human first and briefs them privately, so the human has context before the caller is connected."
  - question: "What is a conferenced handoff?"
    answer: "A conferenced (three-way) handoff brings the human onto the call while the caller stays on the line, so the caller hears the introduction happen. It continues as a three-way conversation until the voice agent drops off. In jambonz this is a warm transfer with callerPresent set to true."
  - question: "Do I need to write custom code for voice agent handoff in jambonz?"
    answer: "No. All three handoff types are declared on the agent verb's handoff property. jambonz injects a transfer_to_human tool the model can call and runs the entire transfer choreography — dialing, screening, briefing, bridging, and fallback — for you. There is no transfer workflow to build."
  - question: "Does the LLM choose which type of transfer to use?"
    answer: "No — you configure the handoff type (blind, warm, or conferenced) on the agent. The LLM only decides when to hand off, by calling the injected transfer_to_human tool once it understands the caller's need."
  - question: "What happens if the human doesn't answer or declines the transfer?"
    answer: "Each outcome (no answer, busy, declined, or failure) has a configurable disposition: return the caller to the voice agent, send them to voicemail, or hang up. By default the caller is returned to the agent, which resumes the conversation."
---

Every production voice agent eventually needs to bring in a human. In jambonz
v11, the three ways to do that — **blind transfer**, **warm transfer**, and a
**conferenced three-way handoff** — are configured directly on the voice agent.
There's no transfer workflow to build.

## Why Handoff Usually Means Writing a Workflow

On most voice AI platforms, "transfer to a human" is not a feature — it's a
project. A warm transfer in particular means orchestrating it yourself: create a
consultation room, place an outbound call to the specialist, move participants
between rooms, tear it all down when someone hangs up. LiveKit, for example,
exposes this as a `WarmTransferTask` built from `CreateSIPParticipant` and
`MoveParticipant` primitives — powerful, but it's plumbing you own, test, and
maintain.

jambonz collapses that into a single declarative `handoff` block on the `agent`
verb. You describe the outcome you want; jambonz injects a `transfer_to_human`
tool for the model and runs the entire choreography — dialing, screening,
briefing, bridging, and fallback — when the model calls it.

One clarification worth making up front: **you** configure *which* kind of
handoff happens; the **LLM** decides *when* to trigger it, by calling the
injected tool once it understands what the caller needs.

## The Three Handoff Types in jambonz v11

All three are the same `agent` verb with a different `handoff` block. The full,
runnable versions of each — built on [`@jambonz/sdk`][sdk] (≥ 0.8.3) — live in
the [transfer-apps examples][examples].

### 1. Blind transfer

The caller is connected directly to the human, with no briefing step. Fastest
option; best for simple routing where context handoff doesn't matter. Here's the
whole agent, so you can see where `handoff` fits:

```ts
session
  .agent({
    stt: { vendor: 'deepgram', language: 'en-US' },
    tts: { vendor: 'cartesia', voice: ttsVoice },
    llm: {
      vendor: 'openai',
      model: 'gpt-4.1-mini',
      llmOptions: { systemPrompt },
    },
    turnDetection: 'stt',
    handoff: {
      mode: 'blind',
      blindMethod: 'dial',                       // 'refer' (SIP REFER) or 'dial' (bridged call)
      target: [{ type: 'phone', number: target }],
      callerId,
      disposition: { onNoAnswer: 'return', onBusy: 'return', onFailure: 'return' },
      actionHook: '/transfer-done',
    },
    eventHook: '/agent-event',
    actionHook: '/agent-done',
  })
  .send();
```

### 2. Warm transfer (private briefing)

The caller is parked on hold while the voice agent calls the human and briefs
them privately. The human is screened with a `confirm` gate — they press a digit
to accept — and only then is the caller connected. Just the `handoff` block (the
rest of the agent is identical):

```ts
handoff: {
  mode: 'warm',
  callerPresent: false,                          // caller is parked; doesn't hear the brief
  target: [{ type: 'phone', number: target }],
  callerId: '+15085550101',                      // an owned DID, or the carrier rejects the leg
  brief: {
    template:
      'In one sentence, tell the specialist why the caller is calling, then say ' +
      'exactly: "Press one to connect, or hang up to decline."',
  },
  confirm: { prompt: 'Press one to connect.', digit: '1' },
  onHoldHook: '/on-hold',                        // what the parked caller hears during the brief
  disposition: { onNoAnswer: 'return', onBusy: 'return', onDecline: 'return', onFailure: 'return' },
  actionHook: '/transfer-done',
},
```

### 3. Conferenced (three-way) handoff

The voice agent brings the human onto the call while the caller stays on the
line, so the caller hears the introduction happen. The call continues as a
three-way conversation until the agent drops off. The only difference from a warm
transfer is a single property — `callerPresent: true`:

```ts
handoff: {
  mode: 'warm',
  callerPresent: true,                           // caller joins the three-way and hears the brief
  target: [{ type: 'phone', number: target }],
  callerId,                                      // an owned DID, or the carrier rejects the leg
  brief: 'auto',                                 // let the LLM write the introduction
  disposition: { onNoAnswer: 'return', onBusy: 'return', onDecline: 'return', onFailure: 'return' },
  actionHook: '/transfer-done',
},
```

No conference verb, no REST `createCall`, no second WebSocket endpoint — jambonz
joins the caller into the three-way and lets the agent introduce them.

## How jambonz Compares to Other Voice AI Platforms

| Feature | jambonz | Other voice AI platforms |
|---|---|---|
| Blind (cold) transfer | Built in | Built in, or via SIP REFER |
| Warm transfer | Built in | Usually via transfer APIs |
| Conferenced handoff | Built in | Often requires custom implementation |
| Setup | Voice agent configuration | Platform config or custom code |

*Capabilities vary by platform.* The conferenced handoff is the one that stands
out: bringing a human into a live three-way with the caller — while the agent
introduces them and then steps away — is rarely a built-in on other platforms.
In jambonz it's one property.

## Getting Started with jambonz

Handoff is available now in jambonz v11. See the [voice agent
documentation][docs] for how to configure blind, warm, and conferenced transfer
on your agent, and the [transfer-apps examples][examples] for complete,
deployable apps for all three.

[sdk]: https://www.npmjs.com/package/@jambonz/sdk
[examples]: https://github.com/jambonz/v10-examples/tree/main/examples/transfer-apps
[docs]: https://docs.jambonz.org
