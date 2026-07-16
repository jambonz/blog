---
title: "Voice Agent Handoff Made Simple in jambonz"
date: 2026-07-16
description: "jambonz v11 adds built-in blind, warm, and conferenced handoff for voice agents — declarative, no custom transfer workflow to build."
author: "Dave Horton"
tags: ["voice-ai", "handoff", "jambonz-v11", "agent", "transfer"]
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
  - question: "What does the transfer verb do in jambonz?"
    answer: "The transfer verb provides a general, simple and declarative means for performing a call transfer to another party from within any jambonz application.  When using the agent or s2s verbs the transfer function is baked into the 'handoff' property, in all other cases you can use the transfer verb."
---

Every production voice agent eventually needs to bring in a human, and there are three possible ways to do that: 
- **Blind transfer** — the caller is connected directly to the human with no briefing.
- **Warm transfer** — the caller is put on hold while the human is briefed privately, then connected.
- **Three-way warm transfer** — the human is brought into the call while the caller stays on the line, so the caller hears the introduction.

jambonz has always had best-in-class support for telephony and all three methods have been supported for a long time.
However, prior to v11, orchestrating a handoff required building a custom transfer workflow, and it could get a bit complicated.

So in v11, we've introduced a simple declarative approach to defining the handoff approach you want for your voice agent.

<iframe width="560" height="315" src="https://www.youtube.com/embed/5cdNry2D8rg?si=CkZMON-O0Mbda9MU" title="Demonstrating ease of use of agent handoff in jambonz version 11" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Why Handoff Usually Means Writing a Workflow

On most voice AI platforms, "transfer to a human" is not a feature — it's a
project. A warm transfer in particular means orchestrating it yourself: create a
consultation room, place an outbound call to the specialist, move participants
between rooms, tear it all down when someone hangs up. LiveKit, for example,
exposes this as a `WarmTransferTask` built from `CreateSIPParticipant` and
`MoveParticipant` primitives — powerful, but it's plumbing you own, test, and
maintain.

jambonz collapses that into a single declarative `handoff` block on the `agent`
verb (if you are building a cascaded voice pipeline) or the `s2s` verb if you are building a 
speech-to-speech voice agent. 

You describe the outcome you want; jambonz injects a `transfer_to_human`
tool for the model and runs the entire choreography — dialing, screening,
briefing, bridging, and fallback — when the model calls it.

The division of responsibilities is clear: 
- **you** declare *which* kind of handoff happens; 
- the **LLM** decides *when* to trigger it, by calling the
injected tool once it understands what the caller needs; and
- **jambonz** handles the mechanics of the transfer — dialing, briefing, bridging, and fallback.

## The Three Handoff Types in jambonz v11

All three are the same `agent`(or `s2s`) verb with a different `handoff` block. The full,
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
    turnDetection: 'krisp',
    handoff: {
      mode: 'blind',
      blindMethod: 'refer',                       // 'refer' (SIP REFER) or 'dial' (bridged call)
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
session
  .agent({
    stt: { vendor: 'deepgram', language: 'en-US' },
    tts: { vendor: 'cartesia', voice: ttsVoice },
    llm: {
      vendor: 'openai',
      model: 'gpt-4.1-mini',
      llmOptions: { systemPrompt },
    },
    turnDetection: 'krisp',
    handoff: {
      mode: 'warm',
      callerPresent: false,        // caller is parked; doesn't hear the brief
      target: [{ type: 'phone', number: target }],
      callerId: '+15085550101',    // optional: caller ID on outbound call to human agent
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
    eventHook: '/agent-event',
    actionHook: '/agent-done',
  })
  .send();
```

### 3. Conferenced (three-way) handoff

The voice agent brings the human onto the call while the caller stays on the
line, so the caller hears the introduction happen. The call continues as a
three-way conversation until the agent drops off. The only difference from a warm
transfer is a single property — `callerPresent: true`:

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
    turnDetection: 'krisp',
    handoff: {
      mode: 'warm',
      callerPresent: true,  // caller joins the three-way and hears the brief
      target: [{ type: 'phone', number: target }],
      callerId,                                      
      brief: 'auto',        // let the LLM create the introduction
      disposition: { onNoAnswer: 'return', onBusy: 'return', onDecline: 'return', onFailure: 'return' },
      actionHook: '/transfer-done',
    },
    eventHook: '/agent-event',
    actionHook: '/agent-done',
  })
  .send();
```

No conference verb, no REST api call to create a second call leg, no second WebSocket endpoint — jambonz
joins the caller into the three-way and lets the voice agent introduce them before dropping out of the conference.

> For details on each of the handoff properties [please review our docs](https://docs.jambonz.org/verbs/verbs/agent#transfer-to-human-handoff).

## Call transfer when not building a voice agent

Call transfer is also available for apps that do not implement a voice agent.  Perhaps you are building a 
simple CPaaS-type callflow using `say`, `gather` etc and you want to do a call transfer?  No problem, in that
case you can simply use the standalone [transfer](https://docs.jambonz.org/verbs/verbs/transfer) verb.  The 
same options described above for the agent handoff are available in the `transfer` verb.

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
documentation](https://docs.jambonz.org/verbs/verbs/agent) for how to configure blind, warm, and conferenced transfer
on your agent, and the [transfer-apps examples](https://github.com/jambonz/v10-examples/tree/main/examples/transfer-apps) for complete,
deployable apps for all three.

[sdk]: https://docs.jambonz.org/sdks/node-sdk
[examples]: https://github.com/jambonz/v10-examples/tree/main/examples/transfer-apps
[docs]: https://docs.jambonz.org
