---
title: "jambonz Adds Speech-to-Speech Support for Azure Voice Live"
date: 2026-09-21
description: "Connect phone calls to Microsoft's Voice Live API with one verb, in native speech-to-speech or cascaded text mode."
tags: ["voice-ai", "azure", "s2s", "speech-to-speech", "microsoft", "llm"]
draft: true
faq:
  - question: "What is the Azure Voice Live API?"
    answer: "Voice Live is Microsoft's managed speech-to-speech service for voice agents. It exposes a single WebSocket that bundles speech recognition, a generative model, and text to speech, so you don't orchestrate those pieces yourself. It uses the Azure OpenAI Realtime event vocabulary but adds Azure-only capabilities such as semantic turn detection, server-side noise suppression and echo cancellation, and the full Azure TTS voice catalog."
  - question: "Is this the same as jambonz's existing microsoft vendor?"
    answer: "No. The microsoft vendor targets the older Azure OpenAI Realtime deployment endpoint and shares its payload shapes with vendor openai. Voice Live is a separate service with its own flat session shape and its own features, so it ships as its own vendor, voicelive. A session_update written for openai_s2s will not work unchanged."
  - question: "Which models can I use with Voice Live on jambonz?"
    answer: "Two families, and the choice changes the architecture. A native speech-to-speech model such as gpt-realtime-2.1 generates audio itself. A text model such as gpt-4.1, gpt-4o or gpt-5 runs cascaded: Azure speech to text transcribes the caller, the text model answers, and an Azure voice speaks the reply. Availability varies by region, so check what your resource actually offers."
  - question: "What kind of Azure resource do I need?"
    answer: "A Microsoft Foundry resource, created with kind AIServices. Its endpoint looks like https://your-resource.services.ai.azure.com/ and that hostname is what jambonz connects to. A plain Speech resource will not work: its only endpoint is the shared regional gateway, which Voice Live rejects with a 401."
  - question: "How do I authenticate to Voice Live from jambonz?"
    answer: "Put your resource key in the verb's auth.apiKey and jambonz sends it as the api-key query parameter. Alternatively, mint a Microsoft Entra ID token for the https://ai.azure.com/.default scope and pass it as auth.accessToken; jambonz sends that as an Authorization Bearer header. Entra tokens are short-lived, so mint one per call."
  - question: "Does jambonz support the Voice Live avatar?"
    answer: "No. Voice Live's text to speech avatar requires a separate WebRTC SDP exchange with the service to carry video, which has no place in a SIP phone call. Everything else (voices, semantic VAD, noise suppression, word timestamps and viseme events) works."
---

We're happy to announce that [jambonz](https://jambonz.org/) now supports Microsoft's
[Azure Voice Live API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/voice-live)
as a first-class speech-to-speech vendor. If you run [jambonz v11](https://jambonz.org/blog/jambonz-v11-release)
or later with the mediajam media engine, you can connect any phone call to a Voice Live
agent with a single verb.

## How Azure Voice Live Compares to Other Speech-to-Speech Vendors

Most speech-to-speech vendors give you one architecture. Voice Live gives you two, and
the model name is the switch.

Name a **native** model such as `gpt-realtime-2.1` and you get what you'd expect from a
realtime API: the model hears audio and answers in its own voice.

Name a **text** model such as `gpt-4.1`, `gpt-4o` or `gpt-5` and the same endpoint runs
**cascaded**. Azure speech to text transcribes the caller, the text model answers, and
an Azure voice speaks the reply. Microsoft manages the wiring; you still get one
WebSocket and one verb. That is genuinely useful when you want a specific text model's
reasoning, or a specific brand voice, without building and operating the pipeline
yourself.

On top of either mode, Voice Live layers Azure capabilities that don't exist on the
OpenAI Realtime API it otherwise resembles:

- **Semantic turn detection:** `azure_semantic_vad` decides the caller has finished
  from *meaning*, not just from silence, and works with every model rather than only
  the realtime ones. Its `remove_filler_words` option means an "umm" no longer counts
  as a barge-in.
- **Server-side audio cleanup:** `azure_deep_noise_suppression` and echo cancellation
  run in the service, which also makes interruption and end-of-turn detection more
  accurate.
- **The full Azure voice catalog:** 600+ standard voices across 150+ locales, plus HD
  voices and custom voices, selectable per call.
- **Word timestamps and visemes**, if you're driving anything visual downstream.

## How to Add Voice Live to a jambonz Call

Here's a minimal application using the [@jambonz/sdk](https://www.npmjs.com/package/@jambonz/sdk)
WebSocket interface:

```js
session
  .answer()
  .s2s({
    vendor: 'voicelive',
    model: 'gpt-realtime-2.1',
    auth: {
      apiKey: process.env.VOICELIVE_API_KEY,
    },
    // the Voice Live endpoint is per-resource, so the host is required
    connectOptions: {
      host: 'my-resource.services.ai.azure.com',
    },
    llmOptions: {
      session_update: {
        modalities: ['text', 'audio'],
        instructions: 'You are a friendly and helpful voice assistant. ' +
          'Keep your responses concise and conversational.',
        voice: {
          name: 'en-US-Ava:DragonHDLatestNeural',
          type: 'azure-standard',
        },
        turn_detection: {
          type: 'azure_semantic_vad',
          silence_duration_ms: 500,
          remove_filler_words: true,
        },
        input_audio_noise_reduction: {
          type: 'azure_deep_noise_suppression',
        },
        input_audio_transcription: {
          model: 'azure-speech',
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

Switching that call to cascaded mode is one line: change `model` to `gpt-4.1`. The rest
of the configuration, including the voice, stays exactly as it is.

## Four Things Worth Knowing Before You Start

These are the things that cost us time, in the order you're likely to hit them.

**Your Azure resource has to be the right kind.** Voice Live needs a **Microsoft
Foundry** resource (`kind=AIServices`) whose endpoint is its own hostname,
`https://your-resource.services.ai.azure.com/`. Strip the scheme and the trailing slash
and that is your `connectOptions.host`.

A plain Speech resource will not do, and this is easy to miss because it *looks* like it
should. Its only endpoint is the shared regional gateway,
`https://eastus.api.cognitive.microsoft.com/`, which every customer in that region
shares. Voice Live can't tell which resource a request belongs to from it, so it answers
`401 ... use a correct regional API endpoint for your resource`. No amount of editing
the URL fixes this: the per-resource hostname simply does not exist in DNS until a
resource is created with one. If you need a new one:

```bash
az cognitiveservices account create \
  --name my-resource --resource-group my-group \
  --kind AIServices --sku S0 --location eastus --yes
```

Voice Live is fully managed, so there is no model to deploy afterwards.

**The session payload is flat, not nested.** Voice Live keeps `voice`, `turn_detection`
and `modalities` at the top level of the session object. OpenAI's GA Realtime format
moved those under `audio.input` / `audio.output`. If you port a `session_update` across
from `openai_s2s` unchanged, Azure won't understand it. Note too that `voice` is an
*object* (`{name, type}`) not a voice-id string.

**Ask for caller transcripts explicitly on native models.** Azure speech to text is
automatic only for non-multimodal models. With `gpt-realtime-2.1` you get no
`conversation.item.input_audio_transcription.completed` events at all unless you set
`input_audio_transcription` yourself, as in the example above. In cascaded mode it's on
by default.

**Model availability is per-region.** The catalog in Microsoft's docs is not what any
one resource offers. In `eastus`, for instance, `gpt-realtime-2.1` and
`gpt-realtime-2.1-mini` are available while plain `gpt-realtime` is not. An unavailable
model comes back as an `invalid_model` error on the first `session.update`, which is a
quick way to check what you actually have.

## Where to Learn More

- A complete working example lives in
  [jambonz/v10-examples](https://github.com/jambonz/v10-examples/tree/main/examples/s2s/voicelive),
  with both modes documented.
- The [llm verb reference](https://docs.jambonz.org/verbs/verbs/llm) covers the Azure Voice Live
  section in detail, including voices, transcription models and the Voice Live-only events.
- Everything in this post (tool calling, the built-in hangup tool, and the event
  stream) is covered by end-to-end tests that place real phone calls in both native
  and cascaded mode.

As always, come find us in the [jambonz community](https://community.jambonz.org/) with
questions. We'd love to hear what you build with it.
