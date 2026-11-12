---
title: "Noise isolation head-to-head: Krisp, ai-coustics, RNNoise and KugelAudio Clarity"
subtitle: "90 live calls through the jambonz media server, measuring how much noise each one removes, what it does to speech recognition, and what it costs in CPU."
date: 2026-11-12
description: "We ran the same noisy speech through Krisp, ai-coustics, RNNoise and KugelAudio Clarity on live 8 kHz calls through jambonz, and measured noise removed, word error rate and media server CPU."
tags: ["noise-isolation", "benchmarks", "voice-ai", "krisp", "ai-coustics", "rnnoise", "kugelaudio"]
draft: true
---

Background noise is the quiet killer of voice agents. A barking dog or a fan in the background turns into
misheard words, false interruptions and an agent that answers questions nobody asked. jambonz can filter the
caller's audio on the media server before it reaches speech recognition. Today you can choose
[Krisp](https://krisp.ai/), [RNNoise](https://jmvalin.ca/demo/rnnoise/) or [KugelAudio Clarity](https://kugelaudio.com/),
and [ai-coustics](https://ai-coustics.com/) support is on its way.

They are very different products: an on-server commercial SDK, a small open-source network, a cloud service, and
an on-server SDK with several model families. So we put all four through the same test.

## How we tested

Every result here comes from a live phone call through a jambonz media server, not from feeding files to the
SDKs directly. Each call played the same audio into jambonz, turned on noise isolation with the `config` verb, and
forked the filtered caller audio back to us with `listen`.

- **Calls:** G.711 (PCMU), 8 kHz, one call at a time on a 4 vCPU AWS host (Xeon Platinum 8124M).
- **Speech:** one 28-word sentence spoken by a text-to-speech voice: *"Please repeat exactly these four words:
  walnut, harbor, velvet, trumpet. I would like to change my delivery address before the weekend because I am
  moving to the city."*
- **Noise:** white noise, pink noise, and babble (four other text-to-speech voices talking at once), each at 0, 5
  and 10 dB signal-to-noise ratio, plus clean speech. Every prompt starts with 3 seconds of noise only.
- **Measured:**
  - how much quieter the noise-only audio got (1.0–2.8 s into the call), compared with the same audio without
    noise isolation
  - the word error rate of Deepgram nova-3 on the filtered audio. "I'm" for "I am", "I'd" for "I would" and
    "harbour" for "harbor" count as correct.
  - the media server's CPU use during the call
- **Engines (8 configurations):**
  - Krisp, with the three noise models on our test server (`vi-tel-lite-v1`, jambonz's default, plus `vi-tel-v2`
    and `vi-pro-v1`)
  - RNNoise
  - ai-coustics, with `quail-s-8khz` (its default for 8 kHz calls in the jambonz integration), `rook-l-8khz` and
    `quail-l-16khz`
  - KugelAudio `clarity-1`

  Every engine ran at its default level, with no tuning.

That is 90 calls, one run per combination. Read small differences with care: one wrong word in our sentence is
3.6 % word error rate, and since we did not repeat runs, a difference of a word or two may be chance.

## Steady noise: who removes it

With white or pink noise, the question is simple: does the hiss go away while the voice stays?

| Engine | Noise removed, white 0/5/10 dB | Noise removed, pink 0/5/10 dB |
|---|---|---|
| Krisp tel-lite-v1 | 55.5 / 56.5 / 59.8 dB | 59.7 / 61.7 / 66.0 dB |
| Krisp tel-v2 | 54.6 / 54.7 / 55.6 dB | 55.4 / 56.6 / 58.4 dB |
| Krisp pro-v1 | 52.7 / 54.8 / 55.1 dB | 63.1 / 78.4 / 68.1 dB |
| ai-coustics rook-l-8khz | 82.7 / 90.2 / 83.5 dB | 76.0 / 82.0 / 88.7 dB |
| KugelAudio clarity-1 | 56.8 / 51.3 / 48.9 dB | 23.2 / 16.6 / 10.3 dB |
| RNNoise | 8.9 / 29.1 / 30.7 dB | 47.2 / 39.7 / 36.4 dB |
| ai-coustics quail-l-16khz | 8.4 / 7.8 / 8.4 dB | 8.0 / 8.0 / 8.1 dB |
| ai-coustics quail-s-8khz | 1.9 / 1.3 / 2.0 dB | 1.9 / 1.9 / 2.0 dB |

Krisp and ai-coustics' `rook-l-8khz` took steady noise down by more than 50 dB in every case. What is left is a
few units out of a 16-bit sample range, which we would expect to be inaudible (we did not run a listening test).
Clarity did the same on white noise but removed much less pink noise. RNNoise removed 29–47 dB, except in the
loudest white noise, where it removed 9 dB.

The surprise is ai-coustics' `quail` models: on 8 kHz calls they removed 1–8 dB of steady noise. ai-coustics
describes Quail as built for machine listening and Rook for human listeners; on our calls, only Rook removed
most of the steady noise. If you use ai-coustics on phone calls, choose the model deliberately.

## What it does to speech recognition

Removing noise only matters if the words survive. Word error rate on the filtered audio (lower is better):

| Engine | Clean | White 0/5/10 dB | Pink 0/5/10 dB |
|---|---|---|---|
| No noise isolation | 0 % | 3.6 / 0 / 0 % | 0 / 0 / 0 % |
| Krisp tel-lite-v1 | 0 % | 10.7 / 3.6 / 0 % | 3.6 / 0 / 0 % |
| Krisp tel-v2 | 0 % | 10.7 / 3.6 / 0 % | 3.6 / 0 / 0 % |
| Krisp pro-v1 | 0 % | 17.9 / 7.1 / 0 % | 3.6 / 0 / 0 % |
| RNNoise | 0 % | 21.4 / 0 / 0 % | 3.6 / 0 / 0 % |
| ai-coustics quail-s-8khz | 0 % | 3.6 / 0 / 0 % | 0 / 0 / 0 % |
| ai-coustics rook-l-8khz | 0 % | 7.1 / 0 / 0 % | 0 / 0 / 0 % |
| ai-coustics quail-l-16khz | 0 % | 3.6 / 0 / 0 % | 0 / 0 / 0 % |
| KugelAudio clarity-1 | 0 % | 25.0 / 21.4 / 10.7 % | 28.6 / 3.6 / 0 % |

A modern speech recognizer copes with steady noise remarkably well on its own: without any filtering, Deepgram
missed one word, at white 0 dB. No engine improved on that. In the loudest white noise the engines that removed
most of the noise lost words (Krisp 3–5, `rook-l-8khz` 2, Clarity 7, against 1 with no filter), and RNNoise,
which removed little there, lost 6.
Clarity lost the most words on steady noise overall (14.9 % on average across the six noisy cells; the next was
Krisp pro-v1 at 4.8 %).

On clean speech, every engine transcribed our sentence without an error and changed its level by no more than
1.2 dB.

## Babble: the hard case

Babble is other people talking, and these engines are built to keep human speech. They mostly did:

| Engine | Noise removed, babble 0/5/10 dB | Word error rate, babble 0/5/10 dB |
|---|---|---|
| No noise isolation | — | 100 / 3.6 / 0 % |
| Krisp tel-lite-v1 | 15.3 / 15.6 / 16.5 dB | 100 / 60.7 / 39.3 % |
| Krisp tel-v2 | 10.0 / 10.6 / 10.3 dB | 100 / 25.0 / 35.7 % |
| Krisp pro-v1 | 9.5 / 9.6 / 9.3 dB | 92.9 / 67.9 / 67.9 % |
| RNNoise | 2.8 / 2.4 / 2.2 dB | 60.7 / 53.6 / 0 % |
| ai-coustics quail-s-8khz | 0.7 / 0.6 / 0.6 dB | 46.4 / 39.3 / 0 % |
| ai-coustics rook-l-8khz | -1.2 / 0.2 / 4.7 dB | 100 / 42.9 / 35.7 % |
| ai-coustics quail-l-16khz | 6.6 / 6.1 / 6.0 dB | 100 / 42.9 / 42.9 % |
| KugelAudio clarity-1 | 3.1 / -0.9 / -4.0 dB | 57.1 / 57.1 / 32.1 % |

No engine removed more than 16.5 dB of babble. At 5 dB, Deepgram ignored the background voices on the unfiltered
call, but on every filtered call the transcript picked up extra words. Many of them come from the background
lines ("we ordered", "the wrong drinks", "meeting"); others match nothing that was said. At 10 dB, RNNoise
and `quail-s-8khz` transcribed the sentence perfectly; the other filters still had errors.

At 0 dB, where the background voices are as loud as the caller, the unfiltered call returned an empty transcript,
as did `rook-l-8khz` and `quail-l-16khz`. The three Krisp models returned almost none of our sentence (partly
background words, partly words nobody said), and `quail-s-8khz`, Clarity and RNNoise returned part of the sentence. `quail-s-8khz` barely changes the audio, so this is more likely the
recognizer behaving differently from one call to the next than a real benefit; one run cannot tell.

The tool built for background talkers is a model that isolates the *primary* speaker. ai-coustics ships such
"Voice Focus" models. We did not include them in this run; in an earlier, smaller check on white noise, Voice Focus
left most of the noise in and damaged the speech, so it needs its own test with real background talkers.

## What it costs

Media server CPU for one call, as a share of one vCPU, on top of a call without noise isolation (median of 10
calls each):

| Engine | Added CPU per call |
|---|---|
| KugelAudio clarity-1 | not measurable (0.3 %, within the spread of calls without noise isolation) |
| Krisp tel-lite-v1 | 4.4 % |
| RNNoise | 6.3 % |
| ai-coustics quail-s-8khz | 8.6 % |
| Krisp tel-v2 | 11.4 % |
| Krisp pro-v1 | 12.3 % |
| ai-coustics rook-l-8khz | 30.1 % |
| ai-coustics quail-l-16khz | 32.8 % |

Among the engines that run on the media server, the large ai-coustics models added about seven times the CPU of
Krisp's default model. That matters when you size media servers. Clarity does its processing in KugelAudio's
cloud, so it adds no measurable CPU on the media server; we did not measure the network cost or delay of sending
the audio there.

## So which one?

In this test:

- **For steady background noise on phone calls,** Krisp's default `tel-lite` model removed it, averaged 3.0 % word error
  rate across the steady-noise cells, and was the cheapest on-server option. ai-coustics `rook-l-8khz` removed
  it as well and lost slightly fewer words (1.2 %), at about seven times the CPU.
- **If you use ai-coustics on 8 kHz calls,** pick the model: `quail-s-8khz` left steady noise in place.
- **RNNoise** is free and open source, and removed moderate steady noise without costing words; it struggled with
  the loudest white noise.
- **Clarity** adds no measurable load on your server, but it lost the most words on steady noise.
- **For other voices in the background,** none of these general noise removers reliably helped recognition, and at
  5 dB every one of them let background words into the transcript.

## What this test does not tell you

We kept this test small, so here is what it leaves out. It used one sentence and one synthetic voice, synthetic
noise instead of real recordings, one run per combination, and 8 kHz phone audio only. It measured noise energy and
speech recognition, not how natural the result sounds to a person. Krisp ran the models installed on our test
server, which are not Krisp's newest. ai-coustics ran SDK 0.21.4. We did not measure latency; the one figure we have
is the 30 ms output delay the ai-coustics SDK reported for `quail-s-8khz` on 8 kHz audio in a separate run of the
jambonz integration. A bigger run with real-world recordings, more speakers, repeated runs and a perceptual quality
score is the obvious next step.

## Turning it on in jambonz

Noise isolation is one setting, on the `agent` verb or for the whole call with `config`:

```json
{ "verb": "config", "noiseIsolation": { "enable": true, "vendor": "krisp" } }
```

```json
{ "noiseIsolation": { "mode": "krisp", "level": 100, "direction": "read" } }
```

Use `"rnnoise"` the same way. KugelAudio also needs a KugelAudio speech credential (or the key on the verb), and
Krisp needs a Krisp license on self-hosted systems. ai-coustics (`"aicoustics"`, with a `model` such as
`"rook-l-8khz.aicmodel"`) is coming in an upcoming jambonz release. See the
[noise isolation docs](https://docs.jambonz.org/guides/features/voice-agents#noise-isolation) for the options of each
engine.
