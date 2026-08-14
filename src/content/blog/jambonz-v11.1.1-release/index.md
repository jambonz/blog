---
title: "jambonz v11.1.1 release"
date: 2026-08-14
description: "New TTS and speech-to-speech vendors, Dialogflow tool calling, conference per-member recording, and SRTP on outbound SIP calls."
author: "Dave Horton"
tags: ["release", "changelog"]
draft: true
---

This release covers everything since **v11.0.0**, including the v11.1.0 changes
that were never written up here.

## New features

### Speech and LLM vendors

- **Deepgram Flux** is available as a TTS vendor across the feature server, API
  and portal.
- **Gradium** added as a TTS vendor.
- **Inworld** streaming TTS with word alignment, plus the `inworld-tts-2`
  generation in the API. The older `tts-1` generation is deprecated.
- **Alibaba Qwen Omni-Realtime** (Qwen-Audio-3.0) added as a speech-to-speech
  vendor.
- **OpenAI GPT live** supported for speech-to-speech, and OpenAI live
  transcription is now available for `transcribe`.
- **xAI** and **Resemble** TTS options are selectable in the portal's Extra
  Options.
- Speechmatics now accepts filtering configuration.

### Dialogflow

- **CX** supports client-side tool calls end to end via `toolHook`.
- **CES** supports the same client-side tool-call round trip, and adds
  streaming playout with turn-by-turn observability.
- Recent Calls in the portal has a turn-by-turn transcript view for Dialogflow
  sessions.

### Calls and conferences

- `listen` accepts `scope=members` at the conference level, producing a
  separate fork per participant rather than one mixed stream.
- Conference participants now report the remote party's number.
- `dial` supports `srtpEncryption` for SIP URI targets, and outbound honors the
  `X-Jambonz-SRTP` header on forwarded SIP URI calls.
- `transfer`/handoff supports `onholdHook`.
- `rtcp-mux` is the default for SRTP on both inbound and outbound.

## Fixes

- `transfer`/handoff no longer loses the caller ID.
- Long-running speech-to-speech sessions are torn down cleanly.
- `lcc_DTMF` prefers RFC 2833 through the media server.
- `say` runs the task correctly on the streaming path.
- Ultravox reports the real error when call registration fails, instead of a
  generic failure.
- Outbound no longer emits an SDP `m=` line with no audio codec.
- Inbound no longer misidentifies certain calls as 3PCC.
- The API loads the ecosystem environment in the `bin/` and `upgrade-db` CLIs.
- SSO login no longer returns a 500 for enterprise users, and SP-scoped users
  are no longer redirected to registration after SSO login.
- An enterprise upgrade keeps the customer's existing Stripe subscription.
- Portal corrections: landing on Home after opting into the new console, the
  carrier KYC prompt is hidden when prepaid isn't offered, the placeholder
  "Est. next invoice" card is parked, and the enterprise welcome dialog no
  longer pushes account creation.

## Removals

- **SMPP** has been removed from the feature server, API and portal.
- The last **FreeSWITCH** dependencies are gone: integration tests now run
  against mediajam, and the cron jobs no longer reference FreeSWITCH.

## Component versions

| Component | v11.0.0 | v11.1.1 |
|---|---|---|
| mediajam | v0.4.15 | **v0.5.3** |
| drachtio | 10.0.22 | **10.1.2** |
| upload-recordings | 1.8.5 | **1.8.6** |
| rtpengine | 14.1.1.8-jambonz10 | 14.1.1.8-jambonz10 |
| pcap-server | 1.0.3 | 1.0.3 |
| heplify-server | 1.0.3 | 1.0.3 |

## Images

AWS AMIs are published for all nine deployment variants on both **amd64** and
**arm64**, in all **30** regions the CloudFormation templates support. The AMIs
and their EBS snapshots are public, so `generate-cf.sh` can copy them into your
own account.

Docker images for the feature server, API server, portal, inbound and outbound
are now built multi-arch (amd64 + arm64).
