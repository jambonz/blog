---
title: "jambonz 11.1.16: turn-taking models, more vendors, and Agent Studio handoffs"
date: 2026-11-22
description: "jambonz 11.1.16 previews jambonz's own turn detection and interrupt models, adds ai-coustics, Phonic, KugelAudio and ElevenLabs Scribe v3 Live, and brings Situations, agent-to-agent handoff and live call events to Agent Studio."
author: "Dave Horton"
tags: ["release", "voice-ai", "agent", "agent-studio", "turn-taking"]
draft: true
faq:
  - question: "What is jambonz turn detection?"
    answer: "It is jambonz's own end-of-turn model, which runs in the jambonz media server as an alternative to Krisp. Set turnDetection to \"jambonz\" on the agent verb. It is a preview in 11.1.16, so the model and its defaults may change in later releases."
  - question: "What is the difference between a Situation and a handoff in Agent Studio?"
    answer: "A Situation changes an agent's instructions and tools during a call while the same agent keeps talking. A handoff passes the call to a different Studio agent, which is the right choice when you need a different engine, voice, speech vendor or language model, or an agent that another team builds."
  - question: "Can my own server follow an Agent Studio call as it happens?"
    answer: "Yes. An agent can post chosen call events to your server, such as what the caller says, the agent's replies, tool results and Situations starting and ending. Your server can reply with actions, or push actions into a live call through the Studio API. These need a cascaded voice pipeline agent on jambonz 11.1.13 or later."
  - question: "Does upgrading to 11.1.16 change the database schema?"
    answer: "No. There are no database schema changes since 11.1.12."
---

jambonz 11.1.16 is out, covering everything from 11.1.13 through 11.1.16. The release is about voice agents in two ways:

- **In jambonz:** our own turn detection and interrupt models (in preview), four new speech and voice AI vendors, and more events telling your application what the agent is doing.
- **In Agent Studio:** Situations, which change an agent's instructions and tools mid-call when something comes up, and handoffs, which pass a caller from one agent to another on the same call. Every Situation change and handoff appears on the call timeline, and the same call events can be sent to your own server as they happen.

## jambonz turn detection and interrupt prediction (preview)

Until now the [agent](https://docs.jambonz.org/verbs/verbs/agent) verb used Krisp for acoustic turn detection. With 11.1.16 you can also run jambonz's own end-of-turn model, which runs directly in our media server:

```json
"turnDetection": "jambonz"
```

To tune it, use `{"mode": "jambonz", "threshold": 0.9}`. The threshold starts at 0.9 and drops over 1.6 seconds of silence, so a caller who simply stops talking isn't left waiting.

There's a matching interrupt model too:

```json
"bargeIn": { "strategy": "interruptPrediction", "vendor": "jambonz" }
```

Both are previews. The models and their defaults may change in later releases, so try them, tell us how they do on your traffic, and don't count on today's numbers yet.

## More vendors

- **ai-coustics** for noise isolation and VAD, with native 8 kHz and 16 kHz models. Use it with `noiseIsolation` on the agent and config verbs. Self-hosted systems need an ai-coustics license key.
- **[Phonic](https://docs.jambonz.org/guides/features/tts-vendor-settings/phonic)** for text-to-speech (in `say`) and speech-to-speech in the `llm` verb.
- **KugelAudio Fluid** for speech-to-speech in the `llm` verb, with `global`, `eu` and `us` regions.
- **ElevenLabs Scribe v3 Live** for speech-to-text. With the agent verb it uses Scribe's turn prediction to end the caller's turn, about 0.8 seconds sooner than VAD on a complete question.

## More visibility into what your agent is doing

The agent eventHook now gets events that used to show up only in feature-server logs:

- **`agent_update`** tells you whether each `agent:update` was applied and, if it was rejected, why.
- **Turn-taking events**: `overlapping_speech`, `user_interruption` (with its cause), `interrupt_prediction_ignored`, `no_response_timeout` and `llm_error`.
- **`turn_end` for turns the agent started itself**, such as the greeting or a reply you asked it to generate. These carry `agent_initiated: true`.

## Agent Studio: Situations, handoffs, and a clearer view of every call

### Situations

A call rarely follows one script. A caller says they've lost their job, disputes a charge, or asks to be called back. Each of these needs its own instructions, and sometimes its own tools, but only once it comes up.

A **[Situation](https://docs.jambonz.org/agent-studio/situations/overview)** is one of those moments, described once on the agent. While it's active, its instructions are added to the prompt, and tools can be offered or hidden. When it's resolved, those changes come off again, and the agent is told what to stop doing so it doesn't keep following the old instructions.

Situations start in one of two ways:

- **The agent decides.** Use this for things the model can recognise from the conversation, like hardship or a callback request. The model sees a one-line "when it applies" description and starts the Situation when it fits.
- **Only your server.** Use this when something must be true before the agent can act. A collections agent's `verify_identity` tool checks the caller and then starts a `negotiation` Situation. Until it does, the model can't see the negotiation instructions or call `record_agreement`. Studio enforces this itself; it doesn't rely on the model to behave.

Situations can wait on each other ("only once `negotiation` has started"), and up to three can be active at once. Your server can also steer a call directly. It can reply to [call events](https://docs.jambonz.org/agent-studio/situations/call-events) with [actions](https://docs.jambonz.org/agent-studio/situations/actions), or [push actions into a live call](https://docs.jambonz.org/agent-studio/situations/push) through the API, for example when a payment lands mid-call. Those actions can start a Situation, add context, change the instructions, or make the agent speak.

Situations, call events and pushed actions need a cascaded voice pipeline agent on jambonz 11.1.13 or later. For a longer walk through, see [Situations: voice agents that change their instructions mid-call](/blog/situations-in-agent-studio/).

### Handing calls to other agents

An agent can now [hand a call to another Studio agent](https://docs.jambonz.org/agent-studio/building/handoff) while the caller stays on the same call. A front desk can pass billing questions to a billing agent, and an English agent can hand off to a Spanish one with a different voice. The receiving agent doesn't greet the caller again: it carries on from what the caller last said, given either a summary, the last few turns, or just the values handed over.

Each destination becomes a tool for the model (`send_to_billing`). The values the receiving agent needs are that tool's parameters, so the model fills in the account number in the same call that decides to hand off. Values can be marked required or sensitive; sensitive values never appear in logs or call records. Callers can be sent back to the first agent too. Studio prevents loops and caps a call at four handoffs.

Use a Situation when only the instructions or tools need to change. Use a handoff when you need a different engine, voice, speech vendor or model, or an agent another team owns.

### Seeing what happened

The call timeline in **[Calls](https://docs.jambonz.org/agent-studio/calls)** and in the test-call view now shows:

- each Situation starting, resolving or being dropped, and who started it;
- handoffs, with the names of the values passed (never the values themselves) and the time until the next agent's first reply;
- refused changes, with the reason;
- any agent update that jambonz didn't apply.

The same events can be [posted live to your own server](https://docs.jambonz.org/agent-studio/situations/call-events), along with call start and end, what the caller says, the agent's replies, interruptions and tool results, so your systems can follow the conversation as it happens.

## One change to note

An `llm` verb with `vendor: openai` and no `model` now defaults to `gpt-realtime-2.1`, because OpenAI retires `gpt-realtime` on January 20, 2027. If you've pinned a model, nothing changes for you.

## Upgrading

There are no database schema changes since 11.1.12. Self-hosted AWS users can deploy now with the CloudFormation templates and public AMIs, available in 30 regions for amd64 and arm64. The [full changelog](https://docs.jambonz.org/changelog) lists every fix in this release, including two API authorization issues, a gather inter-digit timeout bug and a database upgrade from 10.0.x that never finished.
