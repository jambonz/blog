---
title: "Hearing past the noise: noise isolation for outbound AMD"
description: "Why answering-machine detection struggles on noisy outbound calls, and how jambonz noise isolation gives your speech recognizer a clean signal to work with."
tags: [jambonz, AMD, answering-machine-detection, noise-isolation, outbound, STT]
date: 2026-09-21

---

# Hearing past the noise: noise isolation for outbound AMD

If you place outbound calls with jambonz and rely on **answering machine detection (AMD)** to tell a live human apart from a voicemail greeting, there's a small configuration change that can make a big difference to your accuracy: **noise isolation**.

It's a one-line addition to the API request that creates the call — right next to where you enable AMD — and on outbound campaigns it can be the difference between AMD making the right call and AMD guessing.

## AMD is really a speech problem

It helps to understand what AMD is actually doing under the hood. jambonz doesn't detect voicemail by magic — it **listens to the greeting and runs it through your speech-to-text (STT) recognizer**, then applies heuristics to the result:

- How many words were spoken in the greeting? A long, uninterrupted greeting looks like a machine; a short "Hello?" looks like a human. (This is the `thresholdWordCount` setting — it defaults to 9 words.)
- Was a beep or tone detected?
- Did anyone speak at all before the timers expired?

In other words, AMD is only ever as good as the transcription it's fed. If the recognizer mishears the greeting — or hears nothing usable — AMD's decision degrades with it. You start seeing `amd_no_speech_detected`, `amd_decision_timeout`, or, worse, confident-but-wrong results where a human gets flagged as a machine or vice versa.

## The problem with outbound calls: you don't control the room

On an **inbound** call, the person calling you has usually chosen a moment where they can talk. On an **outbound** call, you're interrupting someone wherever they happen to be — and you have no idea what that environment sounds like.

They might be:

- driving, with road noise and the radio on;
- walking down a busy street;
- in a café or an open-plan office;
- on a cheap speakerphone in a big, echoey room.

All of that background noise lands in the same audio stream as their "Hello?" — and it's exactly the kind of interference that trips up a speech recognizer. The greeting the recognizer *should* hear as three clean words arrives smeared with engine noise and cross-talk, so the transcript comes back garbled, padded with noise-induced tokens, or empty. AMD then has bad input to reason about, and your automation downstream — whether to drop a message, connect an agent, or hang up — inherits the mistake.

This is where noise isolation earns its place.

## What noise isolation does

Noise isolation runs the call audio through a noise-suppression model that strips out background noise while preserving speech. Enable it and the recognizer powering AMD gets a **clean voice signal** instead of a voice-plus-traffic signal — so the greeting transcribes accurately, the word count is meaningful, and AMD reaches the right decision faster.

Crucially for outbound work: by default, noise isolation cleans the **inbound** audio — the audio arriving at jambonz *from the far end*, i.e. the person you dialled. That's precisely the audio AMD is analysing. You're cleaning up the noisy environment you can't control, before it ever reaches the recognizer.

## Turning it on

The most common way to run AMD on outbound calls is to enable it right in the **createCall API request** — the same call that kicks off the outbound dial. As of the latest jambonz release, `noiseIsolation` can be set there too, sitting alongside your `amd` configuration. So you enable both in one place, at the moment you launch the call.

Using the jambonz SDK's REST client:

```javascript
const { JambonzClient } = require('@jambonz/sdk/client');

const client = new JambonzClient({ baseUrl, accountSid, apiKey });

await client.calls.create({
  from: '+15085551212',
  to: { type: 'phone', number: '+15085551213' },
  call_hook: '/outbound',
  // Detect human vs. machine on the answered call
  amd: {
    actionHook: '/amd',
  },
  // Clean the far-end audio before it reaches AMD's recognizer
  noiseIsolation: {
    enable: true,
  },
});
```

Or as a raw REST request to `POST /v1/Accounts/{accountSid}/Calls`:

```json
{
  "from": "+15085551212",
  "to": { "type": "phone", "number": "+15085551213" },
  "call_hook": "/outbound",
  "amd": { "actionHook": "/amd" },
  "noiseIsolation": { "enable": true }
}
```

With that in place, jambonz places the call, runs noise isolation on the incoming audio, and fires AMD events to the `actionHook` you specified as it decides. Your application just handles those events:

```javascript
// Leave the voicemail message once — whether triggered by the beep or the fallback
let messageLeft = false;
const leaveMessage = () => {
  if (messageLeft) return session.reply();
  messageLeft = true;
  session
    .say({ text: 'Hi, this is a message from us. Please call us back when you get a chance.' })
    .hangup()
    .reply();
};

// Fires for each AMD event (human, machine, tone, timeout, ...)
session.on('/amd', (evt) => {
  switch (evt.type) {
    case 'amd_human_detected':
      session.say({ text: 'Hi there! Do you have a moment to talk?' }).reply();
      break;
    case 'amd_machine_detected':
      // Voicemail detected — don't talk over the greeting; wait for the beep
      session.reply();
      break;
    case 'amd_tone_detected':
      // The beep — safe to leave a message
      leaveMessage();
      break;
    case 'amd_machine_stopped_speaking':
    case 'amd_tone_timeout':
      // No beep arrived, but the greeting has finished — leave the message anyway
      leaveMessage();
      break;
    case 'amd_no_speech_detected':
    case 'amd_decision_timeout':
      session.hangup().reply();
      break;
    default:
      session.reply();
      break;
  }
});
```

### Prefer to set it in-call? Use `config`

If you're not creating the call via the API — for example the outbound leg is bridged from an inbound call, or you simply prefer to keep everything in your application logic — you can set exactly the same `noiseIsolation` and `amd` options on the **`config` verb** instead:

```json
[
  {
    "verb": "config",
    "recognizer": { "vendor": "deepgram", "language": "en-US" },
    "noiseIsolation": { "enable": true },
    "amd": { "actionHook": "/amd" }
  },
  { "verb": "pause", "length": 25 }
]
```

> **Note:** AMD runs asynchronously. When you attach it to the `config` verb, follow it with a `pause` (or another verb that keeps the call up) so the call doesn't hang up before AMD has had a chance to decide. Setting AMD in the createCall API avoids this bookkeeping — the call stays up on its own while AMD works.

## Switching it off when you're done

Noise isolation was there to help AMD reach a decision — once it has, you often don't need it running for the rest of the call. Leaving it on for a live conversation is rarely harmful, but there's no reason to keep spending media-server (or, for Krisp, licensed) processing on audio you're no longer analysing.

Turning it off is symmetrical to turning it on: send a `config` verb with `noiseIsolation.enable` set to `false`. A natural place to do this is right in your AMD hook, the moment you know a human has answered:

```javascript
session.on('/amd', (evt) => {
  switch (evt.type) {
    case 'amd_human_detected':
      // A human answered — AMD is done, so drop noise isolation and start talking
      session
        .config({ noiseIsolation: { enable: false } })
        .say({ text: 'Hi there! Do you have a moment to talk?' })
        .reply();
      break;
    // ... other cases
  }
});
```

Or as a standalone verb array in any actionHook response:

```json
[
  { "verb": "config", "noiseIsolation": { "enable": false } }
]
```

Because `config` sets session-level state, this takes effect immediately for the rest of the call — no need to repeat it on subsequent verbs.

## Choosing a noise-isolation vendor

jambonz currently supports two noise-isolation engines, selected with the `vendor` property:

- **RNNoise** — a lightweight, open-source noise-suppression model. It runs entirely on your jambonz media servers with no external dependencies and no API key, so it's free to use and available out of the box on any jambonz deployment. A great default, and an easy way to try noise isolation before deciding whether you need more.
- **Krisp** — a best-in-class commercial noise-cancellation engine. Krisp is more aggressive and more capable at stripping out difficult, real-world background noise — road noise, wind, café chatter, the kind of things your outbound recipients are actually surrounded by — while keeping speech clean. Using Krisp requires an API key, which you enable on your jambonz platform.

```json
{
  "noiseIsolation": { "enable": true, "vendor": "rnnoise" }
}
```

```json
{
  "noiseIsolation": { "enable": true, "vendor": "krisp" }
}
```

If you're running on **[jambonz.cloud](https://jambonz.cloud)**, there's good news: **Krisp is included as standard on all accounts** — no separate API key to provision, no extra setup. You can switch it on immediately and get commercial-grade noise cancellation in front of your AMD recognizer.

For a self-hosted deployment, RNNoise is the zero-configuration starting point, and you can bring your own Krisp API key when you want to step up the suppression quality.

## Tuning it

Beyond `enable` and `vendor`, `noiseIsolation` also accepts an optional **`level`** — how aggressively to suppress noise. More aggressive suppression removes more background noise but can start to eat into speech, so it's worth testing against real recordings from your campaign.

And on the AMD side, remember you can tune the detection itself to match your traffic:

- **`thresholdWordCount`** — lower it if your greetings are short, raise it if humans in your market tend to answer more verbosely.
- **`timers`** — `noSpeechTimeoutMs`, `decisionTimeoutMs`, `toneTimeoutMs` and `greetingCompletionTimeoutMs` let you trade a faster decision against a more confident one.

A good rule of thumb: **clean the audio first with noise isolation, then tune AMD's thresholds against the improved transcripts.** Tuning thresholds on top of noisy audio is chasing a moving target.

## Wrapping up

AMD lives or dies by the quality of the speech it hears, and on outbound calls you're at the mercy of whatever environment your recipient happens to be in. Noise isolation puts a clean-up stage in front of the recognizer so a "Hello?" from a moving car reads as clearly as one from a quiet office — giving AMD the clean signal it needs to get the answer right.

It's one line in your `config` verb. If you're running outbound campaigns with AMD, it's well worth switching on.

*Want to go deeper on the AMD event model and the recognizer options behind it? Check out the [jambonz documentation](https://www.jambonz.org/docs) or come find us in the community.*
