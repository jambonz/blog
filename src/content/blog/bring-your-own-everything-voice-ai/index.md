---
title: "jambonz: The Bring-Your-Own-Everything Voice AI Platform"
date: 2026-11-17
description: "Bring your own carrier, speech vendors, LLM and cloud. How jambonz compares with LiveKit, Vapi, Retell and Bland on STT and TTS vendor choice."
author: "Dave Horton"
draft: true
tags: ["voice-ai", "stt", "tts", "speech-vendors", "livekit", "vapi", "retell", "bland"]
faq:
  - question: "How many speech vendors does jambonz support?"
    answer: "jambonz supports 27 speech-to-text (STT) vendors and 39 text-to-speech (TTS) vendors natively, and you can add any other vendor through its custom STT and custom TTS APIs."
  - question: "Can I use my own API keys for speech vendors in jambonz?"
    answer: "Yes. Every speech vendor in jambonz works with your own account and API key, so you pay the vendor directly with no per-minute markup on speech."
  - question: "How is jambonz different from LiveKit for speech vendor support?"
    answer: "LiveKit supports a similar number of vendors, but each one is a code plugin inside an agent you write and host. In jambonz a vendor is a credential you add in the portal or through the API, with no code to write or maintain."
  - question: "Can I use a speech vendor that jambonz doesn't support?"
    answer: "Yes. jambonz has a custom STT API over WebSocket, a custom TTS API over HTTP, and a streaming custom TTS API over WebSocket that accepts text as the LLM generates it. Point jambonz at your server and it is treated like any other vendor."
---

Most voice AI platforms make some of your choices for you. They pick your carrier, your speech vendors, sometimes your LLM, and they run it all in their cloud. That's fine until you need a vendor they don't support, a language they don't cover, or a contract that says the audio can't leave your network.

jambonz takes the opposite approach. **Bring your own everything:**

- **Your own carrier.** Any SIP trunk, any carrier, any country.
- **Your own speech vendors.** 27 STT and 39 TTS vendors built in, each one used with your own account and key.
- **Any speech vendor, even one we don't support.** Custom STT and TTS APIs let you plug in anything, including a model you host yourself.
- **Your own LLM.** Use a hosted model or your own endpoint.
- **Your own infrastructure, if you want it.** Run jambonz on jambonz.cloud, or self-host it on AWS, GCP, Azure, Kubernetes or bare metal.

This post focuses on the speech part, because that's where the differences between platforms are easiest to measure.

## How Many Speech Vendors Do Voice AI Platforms Support?

We counted the STT and TTS vendors supported by jambonz, LiveKit, Vapi, Retell and Bland, using each platform's own docs, API specs and source code, as of 14 November 2026.

| Platform | What it is | STT vendors | TTS vendors |
|---|---|---|---|
| **jambonz** | Open-source voice AI platform, plus jambonz.cloud | **27** | **39** |
| LiveKit | Open-source agent framework, plus LiveKit Cloud | 29 | 37 |
| Vapi | Managed voice agent platform | 13 | 14 |
| Retell | Managed voice agent platform | 4 | 6 |
| Bland | Managed voice agent platform | Own engine only | Own engine only |

A vendor counts once per company, so Deepgram Nova and Deepgram Flux are one vendor, and Azure counts as Microsoft. We only counted vendors with a hosted, public API you can call with a key, and only streaming STT, since batch-only STT can't serve a live call. We left out inference hosts that resell other companies' models, and each platform's in-house engine on its own platform.

Two things stand out. Among managed voice agent platforms, jambonz supports roughly twice as many STT vendors as Vapi and nearly three times as many TTS vendors. And LiveKit, the one platform with a comparable catalog, gets there in a very different way.

## Vendor by Vendor

Here is every vendor we counted, and which platforms support it. Vendors supported by the most platforms are at the top.

### Speech-to-text

| STT vendor | **jambonz** | LiveKit | Vapi | Retell | Bland |
|---|:-:|:-:|:-:|:-:|:-:|
| AssemblyAI | ● | ● | ● | ● |  |
| Deepgram | ● | ● | ● | ● |  |
| Microsoft | ● | ● | ● | ● |  |
| Soniox | ● | ● | ● | ● |  |
| Cartesia | ● | ● | ● |  |  |
| ElevenLabs | ● | ● | ● |  |  |
| Gladia | ● | ● | ● |  |  |
| Google | ● | ● | ● |  |  |
| OpenAI | ● | ● | ● |  |  |
| Speechmatics | ● | ● | ● |  |  |
| xAI | ● | ● | ● |  |  |
| AWS | ● | ● |  |  |  |
| Gnani | ● | ● |  |  |  |
| Gradium | ● | ● |  |  |  |
| Inworld | ● | ● |  |  |  |
| Meta | ● | ● |  |  |  |
| Mistral | ● | ● |  |  |  |
| NVIDIA | ● | ● |  |  |  |
| Reson8 |  | ● | ● |  |  |
| Sarvam | ● | ● |  |  |  |
| Smallest AI | ● | ● |  |  |  |
| Zoom | ● | ● |  |  |  |
| Fish Audio |  | ● |  |  |  |
| Giggy | ● |  |  |  |  |
| KugelAudio | ● |  |  |  |  |
| Lokutor |  | ● |  |  |  |
| Modulate | ● |  |  |  |  |
| Nabrah |  | ● |  |  |  |
| Naver Clova |  | ● |  |  |  |
| Palabra |  | ● |  |  |  |
| Paxa | ● |  |  |  |  |
| Rime |  | ● |  |  |  |
| RTZR |  | ● |  |  |  |
| Saidwire | ● |  |  |  |  |
| SoundHound | ● |  |  |  |  |
| Talkscriber |  |  | ● |  |  |
| **Total** | **27** | 29 | 13 | 4 | 0 |

### Text-to-speech

| TTS vendor | **jambonz** | LiveKit | Vapi | Retell | Bland |
|---|:-:|:-:|:-:|:-:|:-:|
| Cartesia | ● | ● | ● | ● |  |
| ElevenLabs | ● | ● | ● | ● |  |
| Inworld | ● | ● | ● | ● |  |
| MiniMax | ● | ● | ● | ● |  |
| OpenAI | ● | ● | ● | ● |  |
| Deepgram | ● | ● | ● |  |  |
| Fish Audio | ● | ● |  | ● |  |
| Hume | ● | ● | ● |  |  |
| Microsoft | ● | ● | ● |  |  |
| Neuphonic | ● | ● | ● |  |  |
| Rime | ● | ● | ● |  |  |
| Smallest AI | ● | ● | ● |  |  |
| xAI | ● | ● | ● |  |  |
| AssemblyAI | ● | ● |  |  |  |
| Async | ● | ● |  |  |  |
| AWS | ● | ● |  |  |  |
| Bland | ● | ● |  |  |  |
| CAMB.AI | ● | ● |  |  |  |
| Gnani | ● | ● |  |  |  |
| Google | ● | ● |  |  |  |
| Gradium | ● | ● |  |  |  |
| LMNT |  | ● | ● |  |  |
| Mistral | ● | ● |  |  |  |
| Murf | ● | ● |  |  |  |
| NVIDIA | ● | ● |  |  |  |
| Resemble | ● | ● |  |  |  |
| Respeecher | ● | ● |  |  |  |
| Sarvam | ● | ● |  |  |  |
| Soniox | ● | ● |  |  |  |
| Speechify | ● | ● |  |  |  |
| Speechmatics | ● | ● |  |  |  |
| Spitch | ● | ● |  |  |  |
| Vakyam | ● | ● |  |  |  |
| WellSaid | ● |  | ● |  |  |
| Giggy | ● |  |  |  |  |
| Kalpa |  | ● |  |  |  |
| KugelAudio | ● |  |  |  |  |
| Lokutor |  | ● |  |  |  |
| NineNineSix | ● |  |  |  |  |
| Palabra |  | ● |  |  |  |
| Paxa | ● |  |  |  |  |
| Phonic | ● |  |  |  |  |
| Svara | ● |  |  |  |  |
| Uplift AI |  | ● |  |  |  |
| **Total** | **39** | 37 | 14 | 6 | 0 |

Bland's column is empty because Bland runs only its own STT and TTS engines. Bland appears as a TTS vendor because jambonz and LiveKit both let you use its voices through Bland's API.

## Configuration, Not Code

LiveKit's vendor support comes from plugins in its Python agents framework. Each vendor is code that runs inside an agent you write, deploy and keep up to date. If a vendor's plugin changes, you update your agent.

In jambonz, a speech vendor is a credential. You add it in the portal or through the REST API, and then name the vendor and voice in your application. Switching from one TTS vendor to another is a configuration change, not a code change and a redeploy.

That difference matters most when you're testing vendors against each other, which most teams building voice agents end up doing. Latency, accuracy and voice quality vary by language, accent and use case, and the only way to know what works for your callers is to try several.

## Your Keys, Your Vendor Bill

Every jambonz speech vendor works with your own vendor account. You pay the vendor directly, at the price you negotiated, and jambonz adds no per-minute markup on speech.

That's not true everywhere:

- **Retell** hosts all its speech vendors. You can't use your own vendor account.
- **Bland** runs only its own STT and TTS engines, sold as part of a flat per-minute rate.
- **Vapi** supports your own keys for most of its vendors.
- **LiveKit** plugins use your own keys. LiveKit Cloud's hosted inference gateway, which covers a smaller set of vendors, bills through LiveKit instead.

## When Your Vendor Isn't on the List

No platform supports every vendor, so the question is what happens when the one you want is missing.

| Platform | Use your own vendor keys | Custom STT API | Custom TTS API | Streaming custom TTS | Self-hostable |
|---|---|---|---|---|---|
| **jambonz** | Yes, every vendor | Yes (WebSocket) | Yes (HTTP) | Yes (WebSocket) | Yes |
| LiveKit | Yes (plugins) | Code only | Code only | Code only | Yes |
| Vapi | Most vendors | Yes (WebSocket) | Yes (HTTP) | No | No |
| Retell | No | No | No | No | No |
| Bland | No | No | No | No | Enterprise on-prem only |

jambonz gives you three ways to plug in any vendor without changing jambonz itself:

- **Custom STT** over WebSocket. jambonz streams the caller's audio to your server, and your server returns transcripts.
- **Custom TTS** over HTTP. jambonz sends text, and your server returns audio.
- **Streaming custom TTS** over WebSocket. jambonz keeps a connection open and sends text as the LLM generates it, so synthesis starts before the LLM has finished its response.

That last one is the important one for voice agents. Vapi also has a custom TTS API, but it takes one HTTP request per chunk of text, so it can't accept text as it streams out of the LLM. As far as we can tell, jambonz is the only platform here with a configuration-level custom TTS API that does.

Once your custom server is registered, jambonz treats it like any other vendor. We wrote up [an example using Vosk](/blog/tutorial-adding-support-for-a-custom-speech-provider), an open-source recognizer you can run yourself.

## What's New Since October

We last ran this comparison on 5 October. Since then jambonz has added 11 STT vendors and 21 TTS vendors.

**New STT vendors:** Gnani, Gradium, Giggy, Inworld, KugelAudio, Meta, Mistral, Paxa, Saidwire, Sarvam and Smallest AI.

**New TTS vendors:** AssemblyAI, Async, Bland, CAMB.AI, Fish Audio, Giggy, Gnani, Hume, MiniMax, Mistral, Neuphonic, Paxa, Phonic, Respeecher, Sarvam, Smallest AI, Soniox, Speechmatics, Spitch, Svara and Vakyam.

Some of these are big names, like MiniMax, Hume and Fish Audio. Others cover languages the large vendors serve poorly: Sarvam, Gnani and Vakyam for Indian languages, Paxa for Thai, and Spitch for African languages. If your callers speak those languages, the best vendor for them may not be one of the big ones.

## Your Stack, Your Choice

Vendor counts change every month, at jambonz and everywhere else. The number that doesn't change is how many of your choices a platform makes for you. With jambonz, the carrier, the speech vendors, the LLM and the infrastructure are all yours to pick, and to change later.

[Try jambonz.cloud free](https://jambonz.cloud), or [read about self-hosting](https://jambonz.org/self-hosting).
