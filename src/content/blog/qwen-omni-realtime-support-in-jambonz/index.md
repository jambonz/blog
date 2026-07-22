---
title: "jambonz Adds Speech-to-Speech Support for Alibaba's Qwen Omni-Realtime"
date: 2026-07-20
description: "Connect phone calls to Qwen-Audio-3.0-Realtime with a single verb: full-duplex voice AI with semantic turn detection, streaming transcripts, and sub-second response latency."
author: "Dave Horton"
tags: ["voice-ai", "qwen", "s2s", "speech-to-speech", "alibaba", "llm"]
faq:
  - question: "What is Qwen Omni-Realtime?"
    answer: "Qwen Omni-Realtime is [Alibaba Cloud's](https://www.alibabacloud.com/) family of full-duplex speech-to-speech models (the models behind the Qwen-Audio-3.0-Realtime launch). A single model listens and speaks simultaneously over a persistent WebSocket connection, handling speech recognition, reasoning, and speech generation natively without a separate STT/LLM/TTS pipeline."
  - question: "Which Qwen models does jambonz support?"
    answer: "jambonz supports the [Omni-Realtime conversation models](https://www.alibabacloud.com/help/en/model-studio/realtime), including qwen3.5-omni-plus-realtime (strongest reasoning) and qwen3.5-omni-flash-realtime (fastest responses). You choose the model in the verb's model property."
  - question: "How do I authenticate to Qwen from jambonz?"
    answer: "Provide your Alibaba Cloud Model Studio (DashScope) API key in the verb's auth.apiKey property. An optional auth.host selects the endpoint: the default is the international endpoint (dashscope-intl.aliyuncs.com); you can specify a workspace-scoped host or the China (Beijing) endpoint instead. Note that DashScope keys are region-bound. The key and endpoint must belong to the same region."
  - question: "How does turn detection work with Qwen on jambonz?"
    answer: "Qwen offers two server-side modes, configured in session_update.turn_detection: server_vad (acoustic only) and semantic_vad, which considers whether the caller's utterance sounds complete before ending their turn. We recommend starting with semantic_vad and a silence_duration_ms of 800."
  - question: "Can the voice agent speak first when the call connects?"
    answer: "Yes. Include a response_create in llmOptions and jambonz triggers an immediate model response once the session is configured, so the agent greets the caller. Omit it and the agent waits for the caller to speak first."
  - question: "What latency can I expect?"
    answer: "In our testing against the Singapore endpoint, the first audio of the model's reply arrived roughly 400 milliseconds after the caller stopped speaking — comfortably within the range of natural conversational turn-taking."
---

We're happy to announce that [jambonz](https://jambonz.org/) now supports Alibaba's
**Qwen Omni-Realtime** models (the models behind the recent Qwen-Audio-3.0-Realtime
launch) as a first-class speech-to-speech vendor. If you run [jambonz v11](https://jambonz.org/blog/jambonz-v11-release) or later with the mediajam media engine, you can connect any phone call to a full-duplex Qwen voice agent with a single verb.

## Why Qwen Omni-Realtime Matters for Voice Agents

Qwen Omni-Realtime is a *native* speech-to-speech model: one model listens, reasons,
and speaks over a single persistent connection, rather than chaining STT → LLM → TTS.
That architecture shows up where it counts on a phone call:

- **Latency.** In our live testing against the Singapore endpoint, the model's first
  audio arrived about **400 ms after the caller stopped speaking**, squarely in
  natural-conversation territory.
- **Semantic turn detection.** Beyond plain voice-activity detection, Qwen's
  `semantic_vad` weighs whether the caller's utterance actually *sounds finished*
  before taking the turn.
- **Streaming transcripts both ways.** Caller speech is transcribed incrementally
  *while they speak*, and the assistant's speech arrives with a synchronized text
  transcript, so your application always has text to log, analyze, or act on.
- **Scale of language support**, function calling, and a catalog of 55 voices.

## How to Add Qwen Omni-Realtime to a jambonz Call

If you've used the [OpenAI Realtime API with jambonz](https://docs.jambonz.org/tutorials/voice-ai-examples/open-ai-realtime-api), this will feel instantly
familiar. Qwen's wire protocol is an OpenAI-Realtime dialect, and jambonz exposes it
the same way. Here's a minimal application using the [@jambonz/sdk](https://www.npmjs.com/package/@jambonz/sdk)
WebSocket interface:

```js
session
  .answer()
  .qwen_s2s({
    model: 'qwen3.5-omni-flash-realtime',
    auth: {
      apiKey: process.env.DASHSCOPE_API_KEY,
    },
    llmOptions: {
      session_update: {
        modalities: ['text', 'audio'],
        voice: 'Ethan',
        instructions: 'You are a friendly and helpful voice assistant. ' +
          'Keep your responses concise and conversational.',
        turn_detection: {
          type: 'semantic_vad',
          threshold: 0.5,
          silence_duration_ms: 800,
        },
      },
      // the agent speaks first; omit this to wait for the caller
      response_create: {
        instructions: 'Greet the caller warmly and ask how you can help.',
      },
    },
    actionHook: '/s2s-complete',
  })
  .send();
```

A few practical notes from our testing:

- **Endpoints and regions.** The default endpoint is Alibaba's international one
  (`dashscope-intl.aliyuncs.com`). You can set `auth.host` to a workspace-scoped
  endpoint (`ws-<workspaceId>.<region>.maas.aliyuncs.com`, which Alibaba recommends
  for performance) or to the China (Beijing) endpoint. **DashScope API keys are
  region-bound**, so key and endpoint must match.
- **Turn detection tuning.** `silence_duration_ms` controls how long a pause ends the
  caller's turn. Lower values respond faster but will jump into mid-sentence pauses;
  we found 800 ms (the vendor default) a good starting point with `semantic_vad`.
- **Greeting behavior.** The model stays silent until the caller speaks unless you
  provide a `response_create`, a deliberate choice so both agent-first and
  caller-first call flows are easy.

## Where to Learn More About Qwen Omni-Realtime

- The [Qwen Omni Realtime tutorial](https://docs.jambonz.org/tutorials/voice-ai-examples/qwen-omni-realtime) walks
  through the full setup, including function calling and events.
- A complete working example lives in
  [jambonz/v10-examples](https://github.com/jambonz/v10-examples/tree/main/examples/s2s/qwen).
- Qwen support ships in @jambonz/schema 0.4.1, @jambonz/sdk 0.10.0, and jambonz
  v11's feature-server and mediajam.

As always, come find us in the [jambonz community](https://community.jambonz.org/) with
questions. We'd love to hear what you build with it.
