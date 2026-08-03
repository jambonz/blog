---
title: "jambonz Adds Speech-to-Speech Support for xAI's Grok Voice Think Fast 2.0"
date: 2026-08-03
description: "Connect phone calls to xAI's Grok Voice Think Fast 2.0 with a single verb: a native speech-to-speech model that reasons while it speaks, with a reasoning-effort dial you can turn down when latency matters more than deliberation."
author: "Dave Horton"
tags: ["voice-ai", "grok", "xai", "s2s", "speech-to-speech", "llm"]
faq:
  - question: "What is Grok Voice Think Fast 2.0?"
    answer: "Grok Voice Think Fast 2.0 is xAI's native speech-to-speech model, served over a persistent WebSocket at api.x.ai. One model listens, reasons, and speaks, rather than chaining a separate speech-to-text engine, LLM, and text-to-speech engine. xAI reports that 2.0 improves on the 1.0 generation in reasoning, transcription accuracy, and conversational feel, and that it reasons in parallel with speaking so tool calls fire earlier in a turn."
  - question: "Which model name should I use in the jambonz llm verb?"
    answer: "Set model to grok-voice-think-fast-2.0 explicitly rather than relying on the grok-voice-latest alias. Pinning the exact model name means your application's behavior does not change underneath you the next time xAI repoints the alias at a new generation."
  - question: "How is Grok Voice different from OpenAI Realtime on jambonz?"
    answer: "xAI speaks the same OpenAI Realtime GA wire dialect, so llmOptions carries the same session_update and response_create payloads and your existing OpenAI Realtime application is most of the way there. Four differences matter in practice: session_update is required for xAI because audio is gated until the first session.updated arrives; turn_detection sits at the top level of session_update rather than under audio.input; a completed tool call arrives on response.function_call_arguments.done rather than response.output_item.done; and caller transcripts arrive on conversation.item.input_audio_transcription.updated, which is cumulative rather than incremental."
  - question: "What is reasoning.effort and when should I change it?"
    answer: "reasoning.effort is an xAI-specific setting in session_update with two values, high (the default) and none. It is the clearest dial we have seen on any speech-to-speech vendor for trading deliberation against latency: leave it at high for calls where the agent has to reason over tool results or policy, and set it to none for high-volume flows where the fastest possible reply matters more. There is no equivalent knob on OpenAI Realtime, Gemini Live, or Deepgram Voice Agent."
  - question: "Do I need to configure audio formats or codecs?"
    answer: "No, and you should not try. Audio on the wire to xAI is pcm16 at 24 kHz, and jambonz forces that format and rate regardless of what your session_update declares. Anything you set in session_update.audio.input.format or session_update.audio.output.format is overridden, so leave it out."
  - question: "Can the agent use tools, MCP servers, and call transfer?"
    answer: "Yes. Tool and function calling follows the same shape as OpenAI's, declared in session_update.tools and routed to your toolHook. MCP tools, the runtime-injected handoff tool, and the runtime-injected hangup tool all work the same way with xAI as with every other speech-to-speech vendor jambonz supports."
  - question: "Which voices are available?"
    answer: "The built-in voices are eve (the default), ara, rex, sal, and leo, selected via session_update.audio.output.voice. Custom voice IDs from xAI's Custom Voices API also work."
---

We're happy to announce that [jambonz](https://jambonz.org/) supports xAI's
**Grok Voice Think Fast 2.0** as a first-class speech-to-speech vendor. If you run
[jambonz v11](https://jambonz.org/blog/jambonz-v11-release) or later with the mediajam
media engine, you can connect any phone call to a Grok voice agent with a single verb.

## Why Grok Voice Think Fast 2.0 Matters for Voice Agents

[Grok Voice](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech) is a
*native* speech-to-speech model: one model listens, reasons, and speaks over a single
persistent connection. xAI's pitch for the 2.0 generation is that it reasons *while* it
talks — so a tool call can fire before the agent has finished its first sentence, instead
of after a visible pause — along with better transcription accuracy and a more natural
conversational feel than the 1.0 models.

The part we find most interesting for telephony is a setting the other vendors don't
expose: **`reasoning.effort`**, which takes `high` (the default) or `none`. That is an
explicit dial for the tradeoff every voice-agent developer ends up making by hand —
deliberation versus latency — and it can be set per session, so a support flow that
reasons over tool output and a high-volume "where's my order" flow can use the same model
with different characters.

## How to Add Grok Voice to a jambonz Call

If you've used the [OpenAI Realtime API with jambonz](https://docs.jambonz.org/tutorials/voice-ai-examples/open-ai-realtime-api),
this will feel instantly familiar — xAI speaks an OpenAI-Realtime dialect, and jambonz
exposes it the same way. Here's a minimal application using the
[@jambonz/sdk](https://www.npmjs.com/package/@jambonz/sdk) WebSocket interface:

```js
session
  .s2s({
    vendor: 'xai',
    // pinned deliberately, rather than relying on the grok-voice-latest alias
    model: 'grok-voice-think-fast-2.0',
    auth: {
      apiKey: process.env.XAI_API_KEY,
    },
    llmOptions: {
      session_update: {
        instructions: 'You are a friendly and helpful voice assistant. ' +
          'Keep your responses concise and conversational.',
        turn_detection: { type: 'server_vad' },
        audio: {
          output: { voice: 'eve' },
        },
        // xAI-specific: 'high' reasons before speaking, 'none' minimizes latency
        reasoning: { effort: 'high' },
      },
      // the agent speaks first
      response_create: {
        instructions: 'Greet the caller warmly and ask how you can help.',
      },
    },
    actionHook: '/s2s-complete',
  })
  .send();
```

A few practical notes:

- **Pin the model.** Name `grok-voice-think-fast-2.0` explicitly rather than leaning on
  the `grok-voice-latest` alias — that keeps your agent's behavior from shifting the next
  time xAI repoints the alias at a new generation.
- **`session_update` is required.** Unlike OpenAI, xAI gates audio until it has received
  your first `session.update` and replied with `session.updated`, so there is no
  "connect and start talking" path.
- **`turn_detection` is top-level.** OpenAI GA nests it under
  `session_update.audio.input.turn_detection`; xAI expects it directly on
  `session_update`. Omit it (or set it to `null`) to take over turn-taking yourself with
  `input_audio_buffer.commit` / `input_audio_buffer.clear`.
- **Don't set audio formats.** The wire format to xAI is pcm16 at 24 kHz and jambonz
  forces it, so anything you declare in `session_update.audio.*.format` is overridden.

## Where to Learn More

- The [xAI Grok Voice tutorial](https://docs.jambonz.org/tutorials/voice-ai-examples/x-ai-grok-voice-think-fast-2-0)
  walks through the full setup, including tool calling and events.
- A complete working example lives in
  [jambonz/v10-examples](https://github.com/jambonz/v10-examples/tree/main/examples/s2s/xai).
- The [`llm` verb reference](https://docs.jambonz.org/verbs/verbs/llm#xai-voice-agent)
  documents every xAI option, including voices, input transcription, and tool-call routing.
- xAI Voice Agent support ships in jambonz v11's feature-server and mediajam.

As always, come find us in the [jambonz community](https://community.jambonz.org/) with
questions. We'd love to hear what you build with it.
