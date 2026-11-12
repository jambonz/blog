---
title: "Noise isolation head-to-head: Krisp, ai-coustics, RNNoise and KugelAudio Clarity"
subtitle: "We ran four noise filters through 80 real phone calls, plus 10 with no filter for comparison. Some took the hiss down to almost nothing. None came close to removing background chatter."
date: 2026-11-12
description: "We ran the same noisy phone calls through Krisp, ai-coustics, RNNoise and KugelAudio Clarity on a jambonz media server and measured how much noise each removed, what it did to speech recognition, and what it cost in CPU."
tags: ["noise-isolation", "benchmarks", "voice-ai", "krisp", "ai-coustics", "rnnoise", "kugelaudio"]
draft: true
---

Picture your voice agent taking a call from someone standing next to a whirring fan. The fan never stops, the
speech recognizer hears it all, and somewhere in the middle of the hiss is the one sentence that matters.

That is the job of noise isolation: clean up the caller's audio *before* the agent tries to understand it. jambonz
can do this right on the media server, and you have a choice of engines: [Krisp](https://krisp.ai/),
[RNNoise](https://jmvalin.ca/demo/rnnoise/) and [KugelAudio Clarity](https://kugelaudio.com/) today, with
[ai-coustics](https://ai-coustics.com/) on the way.

So which one should you pick? We stopped guessing and ran the same calls through all of them.

## The short version

- **Steady hiss (white and pink noise):** Krisp and ai-coustics' `rook-l` model wiped it out almost completely.
- **Speech recognition already copes with steady noise surprisingly well,** so no filter improved the transcript;
  the best ones cost only a word here and there.
- **Background chatter is a different beast.** None of the filters came close to removing it, and most of them
  let some of the other voices into the transcript.
- **The cost varies a lot.** Krisp's default model was the lightest on-server option; ai-coustics' large models
  used about seven times as much CPU.

## How we tested

We made real phone calls (8 kHz, the way most phone audio arrives) through a jambonz media server and played the
same sentence into each one:

> *"Please repeat exactly these four words: walnut, harbor, velvet, trumpet. I would like to change my delivery
> address before the weekend because I am moving to the city."*

We mixed that sentence with three kinds of noise: **white noise** (TV static), **pink noise** (a deeper, rumbling
hiss) and **babble** (four other synthetic voices talking at once), each at three levels from "noise as loud as the voice"
to "voice clearly louder". Then we turned on each filter, recorded what came out the other side, and asked three
questions:

1. How much of the noise is left?
2. How many words does a speech recognizer (Deepgram nova-3) still get wrong?
3. How much extra CPU does the filter use on the media server?

Nine setups (no filter, three Krisp models, RNNoise, three ai-coustics models and KugelAudio Clarity) times ten
audio conditions makes 90 calls.

## Round 1: does the hiss go away?

This chart shows how loud the steady noise still is after filtering, as a share of the original, averaged over
the six white- and pink-noise recordings. Shorter is better.

<svg class="ncv" viewBox="0 0 520 308" width="100%" role="img" aria-label="Steady noise left after filtering, percent of the original level" xmlns="http://www.w3.org/2000/svg"><style>.ncv .bar{fill:#2a78d6}.ncv .base{fill:#8a8985}.ncv text{fill:currentColor;font:15px system-ui,sans-serif}.ncv .muted{opacity:.65}.ncv .grid{stroke:currentColor;stroke-opacity:.15}:root[data-theme="dark"] .ncv .bar{fill:#3987e5}@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .ncv .bar{fill:#3987e5}}</style><line class="grid" x1="150.0" y1="22" x2="150.0" y2="300"/><text class="muted" x="150.0" y="16" text-anchor="middle">0%</text><line class="grid" x1="223.0" y1="22" x2="223.0" y2="300"/><text class="muted" x="223.0" y="16" text-anchor="middle">25%</text><line class="grid" x1="296.0" y1="22" x2="296.0" y2="300"/><text class="muted" x="296.0" y="16" text-anchor="middle">50%</text><line class="grid" x1="369.0" y1="22" x2="369.0" y2="300"/><text class="muted" x="369.0" y="16" text-anchor="middle">75%</text><line class="grid" x1="442.0" y1="22" x2="442.0" y2="300"/><text class="muted" x="442.0" y="16" text-anchor="middle">100%</text><text x="140" y="42" text-anchor="end">No filter</text><g><title>No filter: 100% of the noise level left (average of 6 steady-noise recordings)</title><path class="base" d="M150,28 h288.0 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-288.0 z"/><text x="448.0" y="42">100%</text></g><text x="140" y="72" text-anchor="end">Krisp tel-lite</text><g><title>Krisp tel-lite: 0.1% of the noise level left (average of 6 steady-noise recordings)</title><rect class="bar" x="150" y="58" width="2.0" height="18"/><text x="158.0" y="72">0.1%</text></g><text x="140" y="102" text-anchor="end">Krisp tel-v2</text><g><title>Krisp tel-v2: 0.2% of the noise level left (average of 6 steady-noise recordings)</title><rect class="bar" x="150" y="88" width="2.0" height="18"/><text x="158.0" y="102">0.2%</text></g><text x="140" y="132" text-anchor="end">Krisp pro</text><g><title>Krisp pro: 0.1% of the noise level left (average of 6 steady-noise recordings)</title><rect class="bar" x="150" y="118" width="2.0" height="18"/><text x="158.0" y="132">0.1%</text></g><text x="140" y="162" text-anchor="end">RNNoise</text><g><title>RNNoise: 7.6% of the noise level left (average of 6 steady-noise recordings)</title><path class="bar" d="M150,148 h18.1 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-18.1 z"/><text x="178.1" y="162">7.6%</text></g><text x="140" y="192" text-anchor="end">ai-coustics quail-s</text><g><title>ai-coustics quail-s: 80.9% of the noise level left (average of 6 steady-noise recordings)</title><path class="bar" d="M150,178 h232.3 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-232.3 z"/><text x="392.3" y="192">80.9%</text></g><text x="140" y="222" text-anchor="end">ai-coustics rook-l</text><g><title>ai-coustics rook-l: &lt;0.1% of the noise level left (average of 6 steady-noise recordings)</title><rect class="bar" x="150" y="208" width="2.0" height="18"/><text x="158.0" y="222">&lt;0.1%</text></g><text x="140" y="252" text-anchor="end">ai-coustics quail-l</text><g><title>ai-coustics quail-l: 39.3% of the noise level left (average of 6 steady-noise recordings)</title><path class="bar" d="M150,238 h110.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-110.7 z"/><text x="270.7" y="252">39.3%</text></g><text x="140" y="282" text-anchor="end">KugelAudio Clarity</text><g><title>KugelAudio Clarity: 8.8% of the noise level left (average of 6 steady-noise recordings)</title><path class="bar" d="M150,268 h21.8 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-21.8 z"/><text x="181.8" y="282">8.8%</text></g></svg>

Krisp (all three models) and ai-coustics' `rook-l` brought the noise down to a tiny fraction of a percent, which should be
inaudible (we didn't run a listening test). Clarity got rid of white noise just as well but left more of the deeper pink noise
behind. RNNoise did well except in the very loudest white noise.

The surprise was ai-coustics' `quail` models, including `quail-s`, the default for phone calls in the upcoming
jambonz integration: they left much of the hiss in place (about 80 % with `quail-s`, about 40 % with `quail-l`). ai-coustics builds Quail for machine listening and Rook for human ears,
and on our phone calls only Rook took out most of the steady noise. If you use ai-coustics on phone calls, choose
the model on purpose.

## Round 2: are the words still there?

Removing noise only helps if the words survive. Across the six steady-noise recordings the speaker said 168
words; here is how many the speech recognizer got wrong. Shorter is better.

<svg class="ncv" viewBox="0 0 520 308" width="100%" role="img" aria-label="Words wrong in steady noise, out of 168" xmlns="http://www.w3.org/2000/svg"><line class="grid" x1="150.0" y1="22" x2="150.0" y2="300"/><text class="muted" x="150.0" y="16" text-anchor="middle">0</text><line class="grid" x1="247.3" y1="22" x2="247.3" y2="300"/><text class="muted" x="247.3" y="16" text-anchor="middle">10</text><line class="grid" x1="344.7" y1="22" x2="344.7" y2="300"/><text class="muted" x="344.7" y="16" text-anchor="middle">20</text><line class="grid" x1="442.0" y1="22" x2="442.0" y2="300"/><text class="muted" x="442.0" y="16" text-anchor="middle">30</text><text x="140" y="42" text-anchor="end">No filter</text><g><title>No filter: 1 of 168 words wrong</title><path class="base" d="M150,28 h5.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-5.7 z"/><text x="165.7" y="42">1</text></g><text x="140" y="72" text-anchor="end">Krisp tel-lite</text><g><title>Krisp tel-lite: 5 of 168 words wrong</title><path class="bar" d="M150,58 h44.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-44.7 z"/><text x="204.7" y="72">5</text></g><text x="140" y="102" text-anchor="end">Krisp tel-v2</text><g><title>Krisp tel-v2: 5 of 168 words wrong</title><path class="bar" d="M150,88 h44.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-44.7 z"/><text x="204.7" y="102">5</text></g><text x="140" y="132" text-anchor="end">Krisp pro</text><g><title>Krisp pro: 8 of 168 words wrong</title><path class="bar" d="M150,118 h73.9 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-73.9 z"/><text x="233.9" y="132">8</text></g><text x="140" y="162" text-anchor="end">RNNoise</text><g><title>RNNoise: 7 of 168 words wrong</title><path class="bar" d="M150,148 h64.1 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-64.1 z"/><text x="224.1" y="162">7</text></g><text x="140" y="192" text-anchor="end">ai-coustics quail-s</text><g><title>ai-coustics quail-s: 1 of 168 words wrong</title><path class="bar" d="M150,178 h5.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-5.7 z"/><text x="165.7" y="192">1</text></g><text x="140" y="222" text-anchor="end">ai-coustics rook-l</text><g><title>ai-coustics rook-l: 2 of 168 words wrong</title><path class="bar" d="M150,208 h15.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-15.5 z"/><text x="175.5" y="222">2</text></g><text x="140" y="252" text-anchor="end">ai-coustics quail-l</text><g><title>ai-coustics quail-l: 1 of 168 words wrong</title><path class="bar" d="M150,238 h5.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-5.7 z"/><text x="165.7" y="252">1</text></g><text x="140" y="282" text-anchor="end">KugelAudio Clarity</text><g><title>KugelAudio Clarity: 25 of 168 words wrong</title><path class="bar" d="M150,268 h239.3 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-239.3 z"/><text x="399.3" y="282">25</text></g></svg>

Here is the twist: with no filter at all, the recognizer got just one word wrong. Modern speech recognition
shrugs off steady noise remarkably well, so no filter could improve on that. The good news is that the best
filters stayed close: ai-coustics `rook-l` missed 2 words, Krisp's default model 5. Clarity missed 25, mostly in
the loudest recordings.

And on clean speech with no noise at all, every engine passed with a perfect transcript.

## Round 3: background chatter

Babble is the hard case, because the "noise" is other voices talking, and these filters are designed to keep
human voices. Here are the words the recognizer got wrong when the background chatter was quieter than the
caller (the 5 and 10 dB recordings, 56 words in total). Shorter is better.

<svg class="ncv" viewBox="0 0 520 308" width="100%" role="img" aria-label="Words wrong with background chatter at 5 and 10 dB, out of 56" xmlns="http://www.w3.org/2000/svg"><line class="grid" x1="150.0" y1="22" x2="150.0" y2="300"/><text class="muted" x="150.0" y="16" text-anchor="middle">0</text><line class="grid" x1="223.0" y1="22" x2="223.0" y2="300"/><text class="muted" x="223.0" y="16" text-anchor="middle">10</text><line class="grid" x1="296.0" y1="22" x2="296.0" y2="300"/><text class="muted" x="296.0" y="16" text-anchor="middle">20</text><line class="grid" x1="369.0" y1="22" x2="369.0" y2="300"/><text class="muted" x="369.0" y="16" text-anchor="middle">30</text><line class="grid" x1="442.0" y1="22" x2="442.0" y2="300"/><text class="muted" x="442.0" y="16" text-anchor="middle">40</text><text x="140" y="42" text-anchor="end">No filter</text><g><title>No filter: 1 of 56 words wrong</title><rect class="base" x="150" y="28" width="7.3" height="18"/><text x="163.3" y="42">1</text></g><text x="140" y="72" text-anchor="end">Krisp tel-lite</text><g><title>Krisp tel-lite: 28 of 56 words wrong</title><path class="bar" d="M150,58 h200.4 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-200.4 z"/><text x="360.4" y="72">28</text></g><text x="140" y="102" text-anchor="end">Krisp tel-v2</text><g><title>Krisp tel-v2: 17 of 56 words wrong</title><path class="bar" d="M150,88 h120.1 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-120.1 z"/><text x="280.1" y="102">17</text></g><text x="140" y="132" text-anchor="end">Krisp pro</text><g><title>Krisp pro: 38 of 56 words wrong</title><path class="bar" d="M150,118 h273.4 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-273.4 z"/><text x="433.4" y="132">38</text></g><text x="140" y="162" text-anchor="end">RNNoise</text><g><title>RNNoise: 15 of 56 words wrong</title><path class="bar" d="M150,148 h105.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-105.5 z"/><text x="265.5" y="162">15</text></g><text x="140" y="192" text-anchor="end">ai-coustics quail-s</text><g><title>ai-coustics quail-s: 11 of 56 words wrong</title><path class="bar" d="M150,178 h76.3 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-76.3 z"/><text x="236.3" y="192">11</text></g><text x="140" y="222" text-anchor="end">ai-coustics rook-l</text><g><title>ai-coustics rook-l: 22 of 56 words wrong</title><path class="bar" d="M150,208 h156.6 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-156.6 z"/><text x="316.6" y="222">22</text></g><text x="140" y="252" text-anchor="end">ai-coustics quail-l</text><g><title>ai-coustics quail-l: 24 of 56 words wrong</title><path class="bar" d="M150,238 h171.2 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-171.2 z"/><text x="331.2" y="252">24</text></g><text x="140" y="282" text-anchor="end">KugelAudio Clarity</text><g><title>KugelAudio Clarity: 25 of 56 words wrong</title><path class="bar" d="M150,268 h178.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-178.5 z"/><text x="338.5" y="282">25</text></g></svg>

Without a filter, the recognizer got one word wrong; it simply ignored the background voices. With a filter
switched on, almost every transcript picked up extra words: some lifted from the voices in the background ("we
ordered", "the wrong drinks"), some nobody said at all. The filters barely reduced the chatter, and with them on the
recognizer started transcribing background voices it had ignored before.

When the chatter was as loud as the caller, every setup struggled. No filter at all returned an empty transcript;
a few of the filters recovered part of the sentence, which with a single call each may well be chance.

The right tool for this job is a model that picks out *one* main speaker. ai-coustics makes those ("Voice Focus"
models), and they deserve their own test with real background talkers.

## Round 4: what does it cost?

Here is the extra CPU each filter added on the media server for one call, as a share of one vCPU. Shorter is
cheaper.

<svg class="ncv" viewBox="0 0 520 308" width="100%" role="img" aria-label="Extra media server CPU per call, percent of one vCPU" xmlns="http://www.w3.org/2000/svg"><line class="grid" x1="150.0" y1="22" x2="150.0" y2="300"/><text class="muted" x="150.0" y="16" text-anchor="middle">0%</text><line class="grid" x1="233.4" y1="22" x2="233.4" y2="300"/><text class="muted" x="233.4" y="16" text-anchor="middle">10%</text><line class="grid" x1="316.9" y1="22" x2="316.9" y2="300"/><text class="muted" x="316.9" y="16" text-anchor="middle">20%</text><line class="grid" x1="400.3" y1="22" x2="400.3" y2="300"/><text class="muted" x="400.3" y="16" text-anchor="middle">30%</text><text x="140" y="42" text-anchor="end">No filter</text><g><title>No filter: 0% of one vCPU added per call</title><rect class="base" x="150" y="28" width="2.0" height="18"/><text x="158.0" y="42">0%</text></g><text x="140" y="72" text-anchor="end">Krisp tel-lite</text><g><title>Krisp tel-lite: 4.4% of one vCPU added per call</title><path class="bar" d="M150,58 h32.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-32.5 z"/><text x="192.5" y="72">4.4%</text></g><text x="140" y="102" text-anchor="end">Krisp tel-v2</text><g><title>Krisp tel-v2: 11.4% of one vCPU added per call</title><path class="bar" d="M150,88 h91.2 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-91.2 z"/><text x="251.2" y="102">11.4%</text></g><text x="140" y="132" text-anchor="end">Krisp pro</text><g><title>Krisp pro: 12.3% of one vCPU added per call</title><path class="bar" d="M150,118 h98.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-98.5 z"/><text x="258.5" y="132">12.3%</text></g><text x="140" y="162" text-anchor="end">RNNoise</text><g><title>RNNoise: 6.3% of one vCPU added per call</title><path class="bar" d="M150,148 h48.2 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-48.2 z"/><text x="208.2" y="162">6.3%</text></g><text x="140" y="192" text-anchor="end">ai-coustics quail-s</text><g><title>ai-coustics quail-s: 8.6% of one vCPU added per call</title><path class="bar" d="M150,178 h67.7 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-67.7 z"/><text x="227.7" y="192">8.6%</text></g><text x="140" y="222" text-anchor="end">ai-coustics rook-l</text><g><title>ai-coustics rook-l: 30.1% of one vCPU added per call</title><path class="bar" d="M150,208 h247.3 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-247.3 z"/><text x="407.3" y="222">30.1%</text></g><text x="140" y="252" text-anchor="end">ai-coustics quail-l</text><g><title>ai-coustics quail-l: 32.8% of one vCPU added per call</title><path class="bar" d="M150,238 h269.5 a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 h-269.5 z"/><text x="429.5" y="252">32.8%</text></g><text x="140" y="282" text-anchor="end">KugelAudio Clarity</text><g><title>KugelAudio Clarity: no measurable added CPU (processing runs in KugelAudio&#x27;s cloud)</title><rect class="bar" x="150" y="268" width="2.3" height="18"/><text x="158.3" y="282">≈0 (cloud)</text></g></svg>

Krisp's default model was the lightest of the filters that run on your own server. ai-coustics' large models used
about seven times as much, which matters when you are sizing media servers for lots of calls. Clarity does its work
in KugelAudio's cloud, so it barely registered on our server; the trade-off is that the audio has to travel to
KugelAudio and back, which we did not measure.

## So which one should you use?

- **For steady hiss on phone calls,** Krisp's default model removed the noise, kept almost every word and was
  the lightest on CPU. ai-coustics `rook-l` was just as thorough and slightly more accurate, at about seven times
  the CPU.
- **On a budget?** RNNoise is free and open source and handled moderate steady noise without losing words.
- **Want almost no load on your servers?** Clarity offloads the work to the cloud, but it lost the most words in steady
  noise in our test.
- **If your callers are in noisy rooms full of people,** don't expect any of these to fix it. Look at
  primary-speaker models instead.

## The fine print

We kept this test small, and here is what it doesn't tell you:

- It used one sentence, one synthetic voice and synthetic noise, with one call per combination. A difference of a
  word or two may be chance.
- It covers 8 kHz phone audio only, and measures noise and speech recognition, not how natural the result sounds
  to a person.
- Krisp ran the models installed on our test server, which are not Krisp's newest. ai-coustics ran its 0.21.4 SDK.
- We did not measure latency. The one figure we have is the 30 ms delay the ai-coustics SDK reported for its
  default phone model in a separate run.

A bigger run with real-world recordings, more voices and listening tests is next on our list.

<details>
<summary><strong>See all the numbers</strong></summary>

**Noise removed (dB, higher = more removed).** Measured on the noise-only seconds before the sentence. Above about 50 dB, what is left is a few units of a 16-bit sample.

| Engine | white 0/5/10 dB | pink 0/5/10 dB | babble 0/5/10 dB |
|---|---|---|---|
| Krisp tel-lite-v1 | 55.5 / 56.5 / 59.8 | 59.7 / 61.7 / 66 | 15.3 / 15.6 / 16.5 |
| Krisp tel-v2 | 54.6 / 54.7 / 55.6 | 55.4 / 56.6 / 58.4 | 10 / 10.6 / 10.3 |
| Krisp pro-v1 | 52.7 / 54.8 / 55.1 | 63.1 / 78.4 / 68.1 | 9.5 / 9.6 / 9.3 |
| RNNoise | 8.9 / 29.1 / 30.7 | 47.2 / 39.7 / 36.4 | 2.8 / 2.4 / 2.2 |
| ai-coustics quail-s-8khz | 1.9 / 1.3 / 2 | 1.9 / 1.9 / 2 | 0.7 / 0.6 / 0.6 |
| ai-coustics rook-l-8khz | 82.7 / 90.2 / 83.5 | 76 / 82 / 88.7 | -1.2 / 0.2 / 4.7 |
| ai-coustics quail-l-16khz | 8.4 / 7.8 / 8.4 | 8 / 8 / 8.1 | 6.6 / 6.1 / 6 |
| KugelAudio clarity-1 | 56.8 / 51.3 / 48.9 | 23.2 / 16.6 / 10.3 | 3.1 / -0.9 / -4 |

**Word error rate (%, Deepgram nova-3, lower = better).** 28 words per recording, so one wrong word is 3.6 %. "I'm", "I'd" and "harbour" count as correct.

| Engine | clean | white 0/5/10 dB | pink 0/5/10 dB | babble 0/5/10 dB |
|---|---|---|---|---|
| No filter | 0 | 3.6 / 0 / 0 | 0 / 0 / 0 | 100 / 3.6 / 0 |
| Krisp tel-lite-v1 | 0 | 10.7 / 3.6 / 0 | 3.6 / 0 / 0 | 100 / 60.7 / 39.3 |
| Krisp tel-v2 | 0 | 10.7 / 3.6 / 0 | 3.6 / 0 / 0 | 100 / 25 / 35.7 |
| Krisp pro-v1 | 0 | 17.9 / 7.1 / 0 | 3.6 / 0 / 0 | 92.9 / 67.9 / 67.9 |
| RNNoise | 0 | 21.4 / 0 / 0 | 3.6 / 0 / 0 | 60.7 / 53.6 / 0 |
| ai-coustics quail-s-8khz | 0 | 3.6 / 0 / 0 | 0 / 0 / 0 | 46.4 / 39.3 / 0 |
| ai-coustics rook-l-8khz | 0 | 7.1 / 0 / 0 | 0 / 0 / 0 | 100 / 42.9 / 35.7 |
| ai-coustics quail-l-16khz | 0 | 3.6 / 0 / 0 | 0 / 0 / 0 | 100 / 42.9 / 42.9 |
| KugelAudio clarity-1 | 0 | 25 / 21.4 / 10.7 | 28.6 / 3.6 / 0 | 57.1 / 57.1 / 32.1 |

**Extra CPU per call (% of one vCPU, median of 10 calls, minus calls with no filter).**

| Engine | Added CPU |
|---|---|
| Krisp tel-lite-v1 | 4.37 |
| Krisp tel-v2 | 11.41 |
| Krisp pro-v1 | 12.29 |
| RNNoise | 6.26 |
| ai-coustics quail-s-8khz | 8.6 |
| ai-coustics rook-l-8khz | 30.12 |
| ai-coustics quail-l-16khz | 32.78 |
| KugelAudio clarity-1 | not measurable (0.27, within the spread of calls with no filter) |

</details>

## Try it in jambonz

Noise isolation is one setting, either on the `agent` verb or for the whole call with `config`:

```json
{ "verb": "config", "noiseIsolation": { "enable": true, "vendor": "krisp" } }
```

```json
{ "noiseIsolation": { "mode": "krisp", "level": 100, "direction": "read" } }
```

Swap in `"rnnoise"` the same way. KugelAudio also needs a KugelAudio speech credential (or the key on the verb), and
Krisp needs a Krisp license on self-hosted systems. ai-coustics (`"aicoustics"`, with a `model` such as
`"rook-l-8khz.aicmodel"`) is coming in an upcoming jambonz release. The
[noise isolation docs](https://docs.jambonz.org/guides/features/voice-agents#noise-isolation) have the options for
each engine.
