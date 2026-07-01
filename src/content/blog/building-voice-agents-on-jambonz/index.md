---
title: "Building voice agents on jambonz: the nuts and bolts"
date: 2026-07-01
description: "A deep dive on the jambonz agent verb — the cascaded STT → LLM → TTS pipeline, supported vendors, turn detection (native STT and Krisp), VAD, barge-in and interrupt prediction, early generation, tool calling, MCP servers, and the built-in handoff-to-human tool."
author: "Dave Horton"
tags: ["voice-ai", "llm", "turn-detection", "agent", "stt", "tts"]
draft: true
---

Most "how to build a voice agent" tutorials stop at "connect an LLM to a phone number." This is not that post. This is a tour of the machinery — every knob you can turn on a jambonz cascaded voice agent, why it exists, and how the pieces fit together into a low-latency, interruptible, tool-calling conversation.

If you've read LiveKit's excellent write-up on turn detection and interruption handling, this covers the same territory for jambonz, plus the parts they leave out: the LLM layer, tool calling, MCP, and the built-in handoff-to-human tool.

We're going to talk about the **cascaded** pipeline — speech-to-text → LLM → text-to-speech, with a real turn-taking state machine in the middle. (jambonz also supports speech-to-speech / realtime models like the OpenAI Realtime API, but that's a different architecture and a different post.) The cascaded pipeline is what most production agents run, because it lets you mix and match the best STT, LLM, and TTS vendors independently and gives you fine-grained control over turn-taking and barge-in.

Everything below is driven by a single verb: **`agent`** (available since jambonz 10.1).

---

## 1. The `agent` verb at a glance

A jambonz application returns instructions as an array of verbs. To stand up a voice agent, you return one `agent` verb. Here's a minimal one:

```json
{
  "verb": "agent",
  "llm": {
    "vendor": "anthropic",
    "model": "claude-haiku-4-5-20251001",
    "llmOptions": {
      "systemPrompt": "You are a friendly receptionist for Acme Plumbing. Keep replies short.",
      "temperature": 0.4
    }
  },
  "stt": { "vendor": "deepgram", "language": "en-US" },
  "tts": { "vendor": "elevenlabs", "voice": "Rachel" }
}
```

That's a working agent. Everything else in this post is refinement. The full set of top-level properties on the verb:

| Property | Purpose |
|---|---|
| `llm` | The "brain" — vendor, model, prompt, tools, generation params |
| `stt` | Speech recognizer config (falls back to application defaults) |
| `tts` | Speech synthesizer config (falls back to application defaults) |
| `bargeIn` | Interruption behavior |
| `turnDetection` | How the agent decides the user has finished a turn |
| `earlyGeneration` | Speculative LLM generation while the user is still finishing |
| `noiseIsolation` | Krisp / RNNoise background-noise suppression |
| `handoff` | Injects a `transfer_to_human` tool for escalation |
| `hangup` | Injects a `hangup` tool so the model can end the call |
| `toolHook` | Webhook (or WebSocket message) that executes your custom tools |
| `toolFiller` | Audio or backchannel to cover tool-execution latency |
| `mcpServers` | Remote MCP servers whose tools the agent can call |
| `eventHook` | Webhook that receives per-turn and lifecycle events |
| `noResponseTimeout` | Seconds of silence before re-prompting the caller (default 12) |
| `autoLockLanguage` | Lock STT/TTS to the detected language |
| `greeting` | Whether the agent speaks first (default `true`) |

We'll go through each cluster in turn.

---

## 2. Pipeline architecture

The cascaded pipeline is a sequence of stages, and — exactly as in any real-time voice system — each stage answers one question:

```
  caller audio
      │
      ▼
 ┌─────────┐   Is there speech?        (VAD / STT speech-start)
 │  STT +  │   What did they say?      (interim + final transcripts)
 │   VAD   │   Have they finished?     (turn detection)
 └─────────┘
      │  final transcript + end-of-turn
      ▼
 ┌─────────┐   Generate a response     (streaming tokens)
 │   LLM   │   Call a tool?            (tool / MCP / handoff)
 └─────────┘
      │  token stream
      ▼
 ┌─────────┐   Speak it                (streaming TTS)
 │   TTS   │   Stop mid-word if the caller barges in
 └─────────┘
```

Internally the `agent` verb is a **state machine**. It's worth understanding, because almost every tuning decision maps onto a state or a transition. The states are:

| State | Meaning |
|---|---|
| `Idle` | Waiting for the caller. May play the greeting. |
| `UserSpeaking` | Caller is talking; transcript is accumulating. |
| `Preflighting` | Speculatively running the LLM before the turn is confirmed (see §9). |
| `AwaitingFinalTranscript` | Turn-end fired but the authoritative transcript hasn't arrived yet. |
| `Thinking` | Committed to a response; LLM is generating. |
| `AssistantSpeaking` | TTS is playing; caller can barge in. |

The happy path is `Idle → UserSpeaking → Thinking → AssistantSpeaking → Idle`, looping for each turn. The interesting states — `Preflighting` and `AwaitingFinalTranscript` — exist entirely to shave latency or improve turn-taking accuracy, and they're what the rest of this post is about.

One invariant worth stating up front, because it explains a lot of the design: **conversation history is only written in committed states.** The user message is written on the transition *into* `Thinking`; the assistant message is written when the LLM stream completes. Speculative work in `Preflighting` never mutates history — on a miss it's simply discarded, with zero cleanup.

---

## 3. Speech-to-text (STT)

The `stt` object selects and configures the recognizer. If you omit it, the agent inherits the account/application default recognizer.

```json
"stt": {
  "vendor": "deepgram",
  "language": "en-US",
  "model": "nova-3",
  "hints": ["Acme Plumbing", "boiler", "thermostat"],
  "hintsBoost": 15,
  "deepgramOptions": { "smartFormatting": true, "endpointing": 500 }
}
```

### Supported STT vendors

jambonz supports a broad set of recognizers, and this is a genuine differentiator — you are not locked to one vendor's ASR:

`google`, `aws` (Amazon Transcribe), `microsoft` (Azure), `deepgram`, `deepgramflux` (Deepgram's turn-aware Flux model), `elevenlabs`, `gladia`, `soniox`, `nvidia`, `assemblyai`, `houndify`, `cartesia`, `speechmatics`, `speechmaticspreview` (Speechmatics' Voice-Agent/turn API), and `openai` (Whisper). You can also register a `custom:*` vendor to point at your own recognizer.

### Common recognizer settings

These apply across vendors (support varies):

- `vendor`, `language`, `label` (which credential to use), `model`
- `hints` / `hintsBoost` — keyword/phrase biasing; hints can be plain strings or `{phrase, weight}` objects
- `altLanguages` — alternative languages for multilingual recognition (Google, Azure)
- `interimResults` — request partial hypotheses
- `punctuation`, `profanityFilter`
- `minConfidence` — reject transcripts below a confidence floor
- `fallbackVendor` / `fallbackLanguage` / `fallbackLabel` — automatic failover to a second recognizer

Every vendor also has its own option bag — `deepgramOptions`, `googleOptions`, `azureOptions`, `assemblyAiOptions`, `speechmaticsOptions`, `openaiOptions`, `nvidiaOptions`, `sonioxOptions`, and so on — for vendor-specific features like diarization, redaction, numeral formatting, entity detection, and endpointing timers. For example, the agent applies sensible defaults automatically: for Deepgram it turns on `smartFormatting` and sets `endpointing: 500` (ms) unless you override them.

### Native turn-taking vendors

This matters a lot for the turn-detection section below. Three recognizers emit **end-of-turn signals as part of their transcription stream** — they've done the turn-detection work for you:

- `deepgramflux`
- `assemblyai`
- `speechmaticspreview`

When you use one of these, the agent uses its native `endOfTurn` events and doesn't need an external turn-taking mechanism. A slightly larger set also emits native **speech-start** events (`deepgramflux`, `assemblyai`, `openai`), which means the agent doesn't need to spin up a separate VAD just to know when the caller started talking.

---

## 4. Text-to-speech (TTS)

The `tts` object selects and configures the synthesizer; omit it to inherit the application default voice.

```json
"tts": {
  "vendor": "elevenlabs",
  "language": "en-US",
  "voice": "21m00Tcm4TlvDq8ikWAM",
  "options": {
    "model_id": "eleven_turbo_v2_5",
    "voice_settings": { "stability": 0.5, "similarity_boost": 0.8, "speed": 1.05 }
  }
}
```

### Supported TTS vendors

`deepgram`, `cartesia`, `elevenlabs`, `rimelabs`, `google`, `microsoft`, `whisper`, `inworld`, `resemble`, `nvidia`, plus `custom:*`.

### Synthesizer settings

- `vendor`, `language`, `voice`, `label`, `engine` (e.g. `neural`)
- `options` — the vendor-specific bag (ElevenLabs `model_id` and `voice_settings`; Cartesia `speed`, `emotion`, `add_timestamps`; etc.)

### Streaming and word-level alignment

For low latency, jambonz streams TTS: LLM tokens flow into the synthesizer and audio flows to the caller before the full response is generated. Several vendors (ElevenLabs, Cartesia, Rimelabs, and others) also emit **word-level timing alignment**. That alignment is not cosmetic — it's what makes clean barge-in possible. When a caller interrupts, the agent asks the streaming buffer *which words were actually spoken* and rewrites the assistant's conversation-history entry to exactly that prefix (see §8). Without alignment, the model would "think" it said things the caller never heard.

### Caching

TTS output is cached by default, keyed on the text plus the full voice identity (account, vendor, language, voice, engine, model, credentials). Static prompts — greetings, menu prompts, hold messages — cost you one synthesis and then replay from cache. Set `disableTtsCache: true` to opt out.

---

## 5. The LLM (the brain)

The `llm` object is where you pick the model and shape its behavior:

```json
"llm": {
  "vendor": "openai",
  "model": "gpt-4o",
  "label": "my-openai-key",
  "llmOptions": {
    "systemPrompt": "You are ...",
    "temperature": 0.5,
    "maxTokens": 400,
    "tools": [ /* ... */ ],
    "initialMessages": [ /* seed the conversation */ ]
  }
}
```

`vendor`, `model`, and `label` (which stored credential to use) select the model. `llmOptions` carries `systemPrompt`, `temperature`, `maxTokens`, `tools`, and optional `initialMessages`/`messages` to seed history. If you don't set `systemPrompt` but include a `system`-role message in `initialMessages`, that's used instead.

### Supported LLM vendors

jambonz uses a pluggable LLM layer (`@jambonz/llm`) with a vendor-agnostic wire contract, so the same agent config runs against any of these by changing `vendor`/`model`. The `agent` verb accepts these vendor ids:

| Vendor | Auth | Example models |
|---|---|---|
| `openai` | API key | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `o1-mini` |
| `anthropic` | API key | `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5` |
| `google` (Gemini API) | API key | `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash` |
| `vertex-gemini` | Service account | Gemini 2.5 / 2.0 / 1.5 on Vertex |
| `vertex-openai` | Service account | `mistral-large`, Llama-3.x MaaS |
| `azure-openai` | API key + endpoint + deployment | GPT-4o / GPT-4 deployments |
| `bedrock` | IAM or Bedrock API key + region | Nova, Claude, Llama 3, Mistral |
| `groq` | API key | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `gemma2-9b-it` |
| `huggingface` | Token | HF Inference Providers |
| `deepseek` | API key | DeepSeek models |
| `baseten` | API key | Hosted OpenAI-compatible models |

(The underlying library ships a few additional OpenAI-compatible adapters, e.g. Moonshot and Z.ai, that you can wire up as custom endpoints.)

A note on **latency**: for a real-time voice agent, time-to-first-token dominates the felt responsiveness of the bot. This is exactly why the Groq adapter exists — Llama on LPU silicon delivers sub-200ms TTFT and much faster inter-token cadence than GPU-backed providers, and the agent feels noticeably snappier. When you tune an agent, pick the model with the latency you need, not just the raw quality score.

### `reasoningEffort` — the thinking-budget knob

Reasoning models can burn hundreds of milliseconds "thinking" before the first token — poison for a voice turn. `llmOptions.reasoningEffort` is a vendor-neutral control (`minimal`, `low`, `medium`, `high`) that the adapter maps to each provider's native mechanism (Gemini `thinkingLevel`, OpenAI `reasoning_effort`, Anthropic extended thinking) and ignores where there's no equivalent. For latency-sensitive turns, `minimal` keeps TTFT low. You can also pass `connectOptions` (`timeout`, `maxRetries`, `endpoint`/`baseURL`) to tune the client itself.

### Conversation history

The agent maintains history as a simple `{role, content}` array (`user`, `assistant`, `tool`), and the vendor adapter translates it to each provider's native wire shape (Gemini uses `model` instead of `assistant`; Anthropic and Bedrock have their own tool-turn ordering rules). You mostly don't think about this — but two capabilities are exposed to you: **history summarization** (optionally condense old turns to keep context small and cheap on long calls) and mid-call **context injection** (§13).

---

## 6. Turn detection: knowing when the caller is done

This is the heart of a good voice agent. End the turn too early and you interrupt the caller mid-thought; end it too late and the bot feels sluggish. jambonz gives you a layered set of mechanisms, configured with `turnDetection`.

### Layer 1 — Native STT endpointing

If your recognizer is one of the native turn-taking vendors (`deepgramflux`, `assemblyai`, `speechmaticspreview`), turn detection is built in. Deepgram Flux, for instance, uses an acoustic+semantic model and emits `EndOfTurn` directly on the transcription stream. This is the default and the lowest-latency option — you don't configure anything. `turnDetection: "stt"` (or omitting it) uses native turn-taking when available.

### Layer 2 — Krisp acoustic turn-taking

If your recognizer doesn't do turn detection natively (Deepgram standard, Google, Azure, …), or you want to override the native behavior, you can bolt on **Krisp** — an acoustic model that listens for natural turn boundaries (intonation, pausing) independent of the transcript.

```json
"turnDetection": { "mode": "krisp", "threshold": 0.5 }
```

or the shorthand `"turnDetection": "krisp"`. The `threshold` (0–1, default `0.5`) trades off eagerness against patience — lower fires sooner. Krisp emits an `endOfTurn` with a probability score. If Krisp fires before the STT final transcript has arrived (it often does — acoustics beat transcription), the agent enters `AwaitingFinalTranscript` and waits up to a bounded timeout (2000 ms by default) for the words to catch up before prompting the LLM.

### Endpointing timers, at a glance

| Timer | Default | What it governs |
|---|---|---|
| Awaiting-final-transcript | 2000 ms | Max wait for STT text after Krisp fires end-of-turn |
| Deepgram `endpointing` | 500 ms | Silence before Deepgram finalizes a transcript |
| `noResponseTimeout` | 12000 ms | Silence in `Idle` before re-prompting the caller |

---

## 7. Voice Activity Detection (VAD)

VAD answers the simplest question — "is anyone talking right now?" — and jambonz uses **Silero** for it. You rarely configure VAD directly; the agent enables it automatically only when it's actually needed:

- **For barge-in**, when the STT vendor doesn't provide native speech-start events and you're not using Krisp interrupt prediction (which runs its own internal VAD). Silero then feeds the tentative-interruption path.
- **For measurement**, when full observability is on and you're using a native-turn-taking STT — here Silero exists purely to timestamp when the caller stopped talking, so the dashboard can report accurate STT latency.

In other words: if your STT already tells the agent when speech starts, jambonz doesn't waste CPU running a redundant VAD. This is a deliberate "no redundant work" design, and it's why VAD is mostly invisible in your config.

---

## 8. Interruption handling (barge-in)

When the caller talks over the bot, you want the bot to stop — but not for a cough, a "mm-hmm," or a burst of background noise. `bargeIn` controls this.

```json
"bargeIn": {
  "enable": true,
  "minSpeechDuration": 0.7,
  "strategy": "vad"
}
```

- `enable` — master switch (default `true`).
- `minSpeechDuration` — seconds of confirmed speech before a barge-in is committed (default `0.7`).
- `sticky` — once interrupted, stay interrupted until the caller stops (rather than resuming the assistant).
- `strategy` — `"vad"` (default) or `"interruptPrediction"`.

### Strategy 1 — VAD (tentative then confirmed)

Speech onset during `AssistantSpeaking` triggers a **tentative** interruption: the agent flips to `UserSpeaking` and starts a timer (`minSpeechDuration`, 700 ms by default). When the timer expires:

- if VAD still shows speech (or an interim transcript has arrived), the interruption is **confirmed**;
- if VAD already reported speech-stopped, it was a blip — the agent **reverts** to `AssistantSpeaking` and keeps talking.

An interim transcript arriving during the window is treated as definitive proof and confirms immediately, without waiting out the timer.

### Strategy 2 — Krisp interrupt prediction

VAD can't tell a real interruption from a backchannel — "uh-huh," "right," "okay" — because acoustically they're all just speech. Krisp's **interrupt prediction** is an ML model that judges whether overlapping caller speech is a genuine attempt to take the floor or just active-listening noise.

```json
"bargeIn": { "strategy": "interruptPrediction", "threshold": 0.5 }
```

With this strategy there's **no tentative pause and no `minSpeechDuration` debounce** — when the model says "this is a real interruption," the agent cuts over immediately. The result is a bot that stops promptly for genuine interruptions but ignores backchannels, which is exactly the behavior that makes a conversation feel natural. (Currently the interrupt-prediction vendor is Krisp; `threshold` defaults to `0.5`.) If interrupt prediction fails to start for any reason, the agent falls back to VAD barge-in automatically.

### Trimming the response on interruption

When a barge-in is confirmed, the agent doesn't just stop audio — it repairs history. Using the TTS word-alignment described in §4, it grabs the text that was *actually spoken*, truncates the assistant's history entry to that prefix (with a trailing marker), clears the TTS buffer, and interrupts the in-flight LLM stream. The model's memory of the conversation now matches what the caller actually heard. It also fires a `user_interruption` event on your `eventHook`.

---

## 9. Early generation (preflight)

This is the most interesting latency optimization in the pipeline, so it gets its own section.

**The problem.** There's inherent dead time between "the caller finished" and "the bot starts talking": you wait for the end-of-turn signal, *then* wait for the final transcript, *then* send it to the LLM, *then* wait for the first token. Turn detection and transcription are partly serialized, and the LLM's time-to-first-token stacks on top.

**The idea.** What if, the moment we have a *tentative* transcript, we start generating the response speculatively — while the turn-detection machinery is still confirming the caller is done? If our guess at the transcript was right, the response is already generated and we release it instantly. If it was wrong, we throw it away.

That's early generation. It comes in two flavors depending on your turn detector:

- **With Krisp turn detection**, it's opt-in — set `earlyGeneration: true`. Krisp emits an early signal that fires the speculative prompt before it confirms the turn has actually ended.
- **With Deepgram Flux**, it's automatic — Flux's native `EagerEndOfTurn` event drives preflight regardless of the `earlyGeneration` flag (provided you've set an eager threshold; see the caveat below). The other native-turn-taking recognizers (AssemblyAI, Speechmatics) don't emit a preflight signal, so early generation isn't available with them.

```json
"turnDetection": "krisp",
"earlyGeneration": true
```

**How it works.** On an early/eager end-of-turn signal, the agent enters `Preflighting` and calls the LLM speculatively (`promptSpeculative`) with the interim transcript. Generated tokens are **buffered, not spoken**, and — critically — this speculative prompt **does not touch conversation history**. Then one of three things happens:

- **Hit.** The authoritative end-of-turn arrives and its (normalized) transcript matches what we preflighted. The buffered tokens are released to TTS *immediately* — the LLM latency has been hidden entirely behind the turn-detection wait. The user and assistant messages are committed to history at this point.
- **Miss.** The final transcript differs from our guess. Buffered tokens are discarded and the agent re-prompts with the correct transcript — no harm done, and no history pollution.
- **Cancel.** The caller keeps talking during preflight (a new interim arrives). That means the first "final" was mid-utterance. The speculative prompt is aborted, tokens discarded, and the agent returns to `UserSpeaking`.

The agent tracks hit/miss/cancel counts so you can see how often preflight is paying off.

**The Deepgram Flux caveat.** Flux's early generation needs an *eager* end-of-turn threshold to trigger on. You must set `stt.deepgramOptions.eagerEotThreshold` — otherwise Flux never emits `EagerEndOfTurn` events and preflight never fires. (The agent logs a warning if it sees `earlyGeneration: true` on Flux without it.)

```json
"stt": {
  "vendor": "deepgramflux",
  "deepgramOptions": { "eagerEotThreshold": 0.7 }
}
```

---

## 10. Noise isolation

Background noise hurts everything downstream — it lowers transcription confidence and confuses barge-in detection. jambonz can run **Krisp** (or **RNNoise**) noise cancellation on the audio before STT and VAD ever see it.

```json
"noiseIsolation": "krisp"
```

or, with control:

```json
"noiseIsolation": { "mode": "krisp", "level": 100, "direction": "read" }
```

- `mode` — `krisp` or `rnnoise`.
- `level` — 0–100 suppression strength (default `100`).
- `direction` — `read` (default) suppresses noise on the *inbound* caller audio.

Note this is independent of Krisp turn-taking and interrupt prediction, even though they share the vendor — you can run noise isolation with any STT and any turn-detection strategy.

---

## 11. Tool calling

An agent that can only talk isn't very useful. Tools let the model look up an order, book an appointment, or check availability. Define tools in `llmOptions.tools` using standard JSON-Schema function definitions:

```json
"llm": {
  "vendor": "openai",
  "model": "gpt-4o",
  "llmOptions": {
    "systemPrompt": "...",
    "tools": [{
      "name": "lookup_order",
      "description": "Look up an order by its ID",
      "parameters": {
        "type": "object",
        "properties": { "order_id": { "type": "string" } },
        "required": ["order_id"]
      }
    }]
  }
}
```

When the model decides to call `lookup_order`, the agent dispatches it to your **`toolHook`** and feeds the result back into the conversation so the model can continue:

```json
"toolHook": "/tools"
```

The agent POSTs an `agent:tool-call` request to that hook with the tool name, call ID, and arguments. You return the result. If your app is connected over WebSocket instead of HTTP, you respond asynchronously with an `llm:tool-output` message. Either way there's a safety timeout (20 seconds by default) so a hung tool can't wedge the call. After the result comes back, the agent re-prompts the LLM with the tools still in scope (some providers — Anthropic in particular — require the tool definitions to stay visible across the tool-call turn).

### Covering tool latency with a filler

A three-second database lookup is an awkward silence on a phone call. `toolFiller` covers it:

```json
"toolFiller": {
  "type": "backchannel",
  "startDelaySecs": 2,
  "style": "casual"
}
```

- `type: "audio"` loops an audio file (`url`) — think hold music or keyboard clicks.
- `type: "backchannel"` speaks short LLM-generated phrases ("Let me pull that up…"), pre-warmed at agent startup in the TTS voice so there's no synthesis delay. `style` gives the model a tone hint ("casual", "professional and patient").
- `startDelaySecs` (default 2) is how long to wait before the filler kicks in — fast tools finish before the caller notices any gap.
- `escalationSecs` (default 10) is when a backchannel filler escalates to a longer explanatory line, for tools that run 10+ seconds.

Set `toolFiller: false` to disable it entirely.

---

## 12. Calling MCP servers

Beyond locally-defined tools, the agent can connect to remote **MCP (Model Context Protocol)** servers and expose *their* tools to the model — no glue code, no redeploying your app when the toolset changes.

```json
"mcpServers": [
  { "url": "https://tools.example.com/mcp/sse",
    "auth": { "Authorization": "Bearer TOKEN" } }
]
```

At agent startup, jambonz connects to each server (auto-detecting SSE vs. streamable-HTTP transport), discovers its tools, and **merges them into the same tool list** as your local tools, the handoff tool, and the hangup tool. From the model's perspective it's one flat toolset. When the model calls an MCP tool, the agent routes it to the right MCP client, applies a per-call timeout (10 s by default), and — if the connection has dropped — reconnects once and retries before giving up. Connections are cleanly torn down when the call ends.

This is the clean way to give an agent access to a shared, independently-deployed capability (a booking system, a knowledge base, an internal API gateway) that many agents use.

---

## 13. Built-in tools: handoff and hangup

Two behaviors are common enough that jambonz ships them as built-in tools you enable declaratively — you don't have to define the schema or handle them in your `toolHook`.

### The handoff tool (`transfer_to_human`)

Set a `handoff` config and the agent injects a `transfer_to_human` tool the model can call to escalate to a person:

```json
"handoff": {
  "mode": "warm",
  "target": "+15125551212",
  "brief": "auto"
}
```

The injected tool always takes a `reason`, and — unless `brief: "none"` — a required `summary` argument, with a description that tells the model to brief the human ("who the caller is, what they want, and anything verified or attempted"). You can rename the tool (`toolName`) and override its description (`toolDescription`).

When the model calls it, the agent:

1. suspends itself (detaches its STT/LLM/TTS handlers and stops any in-flight generation),
2. builds a transfer using your `handoff` config merged with the model's tool arguments, and executes it (blind or warm, to a SIP URI / phone number / queue),
3. branches on the outcome — if the transfer **returns** (no answer, human hangs up), the agent re-attaches and resumes the conversation, firing a `transfer.returned` event; if it **bridges or ends**, the agent completes with a `transferred` reason.

So a caller can be handed to a human with a spoken summary, and if the human doesn't pick up, the bot seamlessly takes the call back.

### The hangup tool

Similarly, a `hangup` config injects a `hangup` tool so the model can end the call itself when the conversation is genuinely over — with an optional reason. Both built-ins are intercepted *before* MCP/`toolHook` routing, so they never leak to your webhook.

---

## 14. Mid-call control

An agent isn't frozen once it starts. You can steer it live (via the REST API / a WebSocket message), which the state machine applies at the next safe moment:

- **`update_instructions`** — hot-swap the system prompt (TTS guidance is re-appended automatically).
- **`inject_context`** — push messages into history, e.g. "the caller just completed payment," so the model reacts without the caller having to say it.
- **`update_tools`** — replace the tool set for the next turn.
- **`generate_reply`** — make the agent speak now, optionally interrupting the current response — useful for event-driven prompts ("your callback is ready").

---

## 15. Observability

Your `eventHook` receives real-time events throughout the conversation: `user_transcript` (recognized caller speech), `llm_response` (the assistant's reply text), `user_interruption` (a barge-in was confirmed), and `turn_end` (the end-of-turn summary). The `turn_end` payload is the one you'll build dashboards on — it carries the transcript, the response, whether the turn was interrupted, and a `latency` object with per-component timings:

- `stt_ms` — caller stopped talking → final transcript
- `eot_ms` — final transcript → end-of-turn decision
- `ttft_ms` / `llm_ms` — prompt → first LLM token (minus any tool-call time)
- `tts_ms` — first token → first audio
- `preflight` — hit / miss / cancel and token count, when early generation is on

Plus the session-level counters — barge-in attempts/confirmations/reverts, preflight hits/misses/cancels, no-response timeouts — which are exactly the numbers you use to tune the thresholds in §6 and §8. If a barge-in is reverting too often, your `minSpeechDuration` is too low or you want interrupt prediction. If preflight misses dominate, your STT is producing unstable interims. The instrumentation tells you which knob to turn.

---

## 16. Putting it together

Here's a fully-specified agent that uses most of what we've covered — a low-latency configuration built around Krisp: acoustic turn-taking, a semantic gate, interrupt prediction, early generation, noise isolation, a tool webhook, and human handoff. (Interrupt prediction and Krisp turn detection ride the same Krisp session, so they pair naturally.)

```json
{
  "verb": "agent",
  "greeting": true,
  "llm": {
    "vendor": "groq",
    "model": "llama-3.3-70b-versatile",
    "llmOptions": {
      "systemPrompt": "You are a support agent for Acme. Be concise and warm.",
      "temperature": 0.4,
      "maxTokens": 300,
      "reasoningEffort": "minimal",
      "tools": [{
        "name": "lookup_order",
        "description": "Look up an order by ID",
        "parameters": {
          "type": "object",
          "properties": { "order_id": { "type": "string" } },
          "required": ["order_id"]
        }
      }]
    }
  },
  "stt": { "vendor": "deepgram", "language": "en-US" },
  "tts": {
    "vendor": "elevenlabs",
    "voice": "21m00Tcm4TlvDq8ikWAM",
    "options": { "model_id": "eleven_turbo_v2_5" }
  },
  "turnDetection": "krisp",
  "earlyGeneration": true,
  "bargeIn": { "strategy": "interruptPrediction", "threshold": 0.5 },
  "noiseIsolation": "krisp",
  "toolHook": "/tools",
  "toolFiller": { "type": "backchannel", "startDelaySecs": 2 },
  "handoff": { "mode": "warm", "target": "+15125551212", "brief": "auto" },
  "hangup": {},
  "eventHook": "/agent-events"
}
```

> **Krisp requires an API key** on self-hosted jambonz — that covers turn detection, interrupt prediction, and Krisp noise isolation. RNNoise noise isolation is the key-free alternative.

## 17. A tuning cheat-sheet

| Symptom | Likely cause | Knob |
|---|---|---|
| Bot cuts callers off mid-sentence | Turn ending too early | Raise Krisp `threshold`; rely on native STT turn-taking |
| Bot is slow to reply | LLM TTFT stacked on turn detection | Turn on `earlyGeneration` (Krisp) or use Flux; pick a faster model (e.g. Groq); set `reasoningEffort: "minimal"` |
| Bot stops for "uh-huh" | VAD can't tell backchannels from interruptions | `bargeIn.strategy: "interruptPrediction"` |
| Bot stops for coughs/noise | Debounce too short | Raise `bargeIn.minSpeechDuration`; add `noiseIsolation` |
| Bot ignores real interruptions | Barge-in disabled or debounce too long | Check `bargeIn.enable`; lower `minSpeechDuration` |
| `earlyGeneration` seems to do nothing on Flux | No eager EOT signal | Set `stt.deepgramOptions.eagerEotThreshold` |
| Long calls get expensive / lose the plot | Unbounded history | Enable history summarization |
| Awkward silence during lookups | No latency cover | Add `toolFiller` |

---

## Wrapping up

The cascaded `agent` verb is a lot of machinery, but the mental model is simple: it's a pipeline — *is there speech? what did they say? are they done? respond, and stop if they interrupt* — with an explicit state machine you can tune at every stage. Mix the STT, LLM, and TTS vendors that fit your latency and quality budget; let native STT turn-taking or Krisp decide when the caller is done; use interrupt prediction to stop for real interruptions and ignore backchannels; and hide LLM latency with early generation. Wire in tools, MCP servers, and human handoff, and you have a production voice agent — all from one verb and a JSON object.
