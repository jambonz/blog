---
title: "Voice AI for Outbound Campaigns: How Guayaba Got 34% More Fulfillments per Dial on jambonz"
date: 2026-11-06
description: "Guayaba moved its Spanish and English outbound voice AI campaigns from a leading hosted voice-AI platform to voice agents built on the jambonz agent verb, and now gets 34% more fulfillments from the same number of dials."
author: "Dave Horton"
tags: ["case-study", "outbound", "voice-ai", "agent-verb", "self-hosting"]
draft: true
whitepaper:
  title: "Guayaba × jambonz: customer case study"
  file: "/whitepapers/guayaba-jambonz-case-study.pdf"
  description: "Results across twelve outbound campaigns, the turn-taking measurements, and Guayaba's methodology."
  pages: 3
---

Guayaba runs AI calling campaigns for US consumer-finance businesses, mostly for the US Hispanic market, in Spanish and English. In July 2026 it moved its main outbound campaigns from one of the leading hosted voice-AI platforms to jambonz, running on its own infrastructure.

Three months later, Guayaba gets **34% more fulfillments from the same number of dials** across twelve campaigns.

## Why Did Guayaba Leave a Hosted Voice-AI Platform?

The hosted platform worked. But the behaviours that decide whether an outbound call converts were hard to tune from outside: when the agent yields to the caller, how voicemail is detected, and how a qualified caller is handed to a human.

Guayaba wanted to own those decisions, and to measure them on its own calls.

## How Long Did the Move Take?

**Five days**, July 10–15, 2026. Guayaba runs jambonz on its own servers and keeps its campaign logic in its own application, which talks to jambonz over the [WebSocket API](https://docs.jambonz.org). jambonz runs the calls; Guayaba decides what the agent says and does.

## How Are Guayaba's Voice Agents Built?

Every campaign's voice agent is built on the jambonz [agent verb](https://docs.jambonz.org/verbs/verbs/agent). The agent verb is a complete voice AI pipeline in a single verb: speech-to-text, a language model and text-to-speech, with turn-taking, barge-in, tool calls and handoff to a person built in.

On each call, Guayaba's application starts the agent verb with the campaign's prompt and tools. From there the agent verb runs the conversation: it decides when the caller has finished speaking, whether speech over the agent is a real interruption, and when to call a tool, such as transferring a qualified lead to a live agent.

Guayaba's campaigns use two specialised models for the listening side:

- **[Deepgram Flux](https://deepgram.com/flux)** for speech-to-text, in Spanish (es-419) and English. Flux also decides when the caller has finished their turn, so the agent verb uses its end-of-turn signal directly rather than waiting on a fixed silence.
- **Interrupt prediction** for barge-in. When the caller speaks while the agent is talking, an AI model running inside the agent verb scores whether it's a real attempt to take the floor or just "uh-huh", "sí" or background noise. Only a real interruption stops the agent.

That's Guayaba's choice, not a requirement. Every part of an agent verb is pluggable, with your own keys:

| | Options |
| --- | --- |
| Speech-to-text | More than 25 vendors, including Deepgram (Nova and Flux), Google, Microsoft, AWS, AssemblyAI, Speechmatics, Soniox, Gladia, ElevenLabs, Cartesia and OpenAI, plus your own |
| Text-to-speech | More than 35 vendors, including ElevenLabs, Cartesia, Deepgram, Google, Microsoft, Rime, Inworld, Hume, Speechify, Murf, Resemble AI and Fish Audio, plus your own |
| Language model | Anthropic, OpenAI, Google Gemini (direct or Vertex AI), AWS Bedrock, Azure OpenAI, Groq, Hugging Face, OpenRouter, or any OpenAI-compatible endpoint |
| End of turn | Native from the recognizer (Deepgram Flux, AssemblyAI, Speechmatics and others), an AI turn-detection model, or silence-based |
| Barge-in | Voice-activity detection, or AI interrupt prediction |
| Voice-activity detection | Silero, or the recognizer's own speech events |

Since September every campaign has run on the agent verb, with answering-machine detection tuned for campaigns that mix Spanish and English. Each change was measured on Guayaba's own calls before it went to every campaign.

## What Changed for the Business?

Against the hosted platform, across twelve outbound campaigns from five accounts:

| Measure | Change |
| --- | ---: |
| Fulfillments per dial | **+34%** |
| Transfers per live conversation | **2×** |
| Fulfillments per live conversation | **2×** |

Fulfillments per dial is the measure to watch, because it doesn't depend on how calls are classified: it's up a third. The first three weeks after the move ran at the old level while voicemail detection and prompts were tuned. From August, weekly fulfillments per dial stayed well above the hosted-platform level, averaging 43% above it from August to October. The gain varies by campaign and by language.

Guayaba's methodology: all figures come from its own call log, one row per call. "Before" is June 15 to each campaign's move date; the headline "after" is October 16–25, 2026. Seasonality, lead lists and prompt changes weren't controlled.

## Do Callers Notice the Difference?

Turn-taking is where they do. In late September Guayaba switched barge-in from plain voice-activity detection to AI interrupt prediction. End of turn came from Deepgram Flux in both periods, so the difference below is how the agent handles speech over itself.

On calls that reached a person, same accounts, weekday calls:

| | Before, Sep 22–29 | After, Oct 20 – Nov 4 |
| --- | ---: | ---: |
| Agent cut off only by a backchannel or greeting ("uh-huh", "hello") | 33.4% | **5.4%** |
| Agent turns cut off at all | 18.7% | **14.2%** |
| Agent replies restarted from the top after a cut | 11.3% | **5.6%** |
| Caller turns repeating what they just said | 0.2% | 0.2% |

False interruptions fell from a third of the agent's cuts to about one in twenty, and callers didn't repeat themselves more often. The later window is the system as it runs today.

On jambonz's side, caller speech is lost in about **0.1% of sessions**, and there is no dead air after an interruption. When a caller interrupts and then says nothing, the agent can be configured to take the turn back.

## How Does It Hold Up at Volume?

Guayaba runs every campaign on a single jambonz server, handling **4,200–5,000 voice agent sessions a day**. Measured from jambonz's logs, November 2–4:

| | |
| --- | ---: |
| Server restarts | **0** |
| Calls dropped by an LLM or WebSocket failure (Nov 2–3) | **0** |
| Language model first token, median | **about 720 ms** |
| Text-to-speech first audio, median | **about 150 ms** |

## What Did Guayaba Learn?

**Budget for tuning, not just migration.** Moving took five days. The conversion gains came over the next three months, each change measured on real calls.

**Measure by language and by campaign.** What worked for the Spanish campaigns wasn't what worked for the English ones, and an aggregate number would have hidden it.

**Work with the jambonz team on your data.** We analysed Guayaba's calls, proposed fixes, and upgraded their system overnight, often within a day of a report.

> "On a hosted platform we couldn't tune the things that decide whether an outbound call converts. We moved our main campaigns to jambonz in five days, and with a team that turned our reports into fixes, often overnight, we now get a third more fulfillments from the same number of dials."
>
> — [Name, title], Guayaba

## What's Next: Agent Studio

Guayaba builds its agents in its own application, which suits a team that wants its campaign logic in its own code. For teams that would rather not write and host an application server, we've just launched [Agent Studio](/blog/introducing-agent-studio) in preview.

Agent Studio is a builder for voice AI agents on jambonz. You choose an engine (a cascaded pipeline, a speech-to-speech model, a hosted agent, or your own code), then add tools, transfers to a person and phone numbers, and test from the browser with a full trace of every call. Agent Studio hosts the runtime, so an agent answers calls with no server of your own, and any agent can be exported as a jambonz Node.js application if you later want it in your own code.

## Running Outbound AI Calling at Volume?

If you run outbound AI campaigns and want to own how your agent listens, detects voicemail and hands off to people, **[talk to us](https://jambonz.org/contact-us)**.

**[Download the full case study (PDF)](/blog/whitepapers/guayaba-jambonz-case-study.pdf)**, with Guayaba's methodology and weekly results.
