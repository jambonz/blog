---
title: "I Built a Voice Agent with an LLM. How Do I Get It Answering Real Phone Calls?"
date: 2026-10-21
description: "The simplest way to put an LLM voice agent on a real phone number: get a number and a SIP trunk, connect them to jambonz, and point the number at your agent."
author: "Dave Horton"
tags: ["voice-ai", "llm", "sip", "phone-numbers", "tutorial"]
faq:
  - question: "What's the simplest way to get a phone number and SIP for an LLM voice agent?"
    answer: "Buy a phone number and a SIP trunk from any SIP trunking provider, add both to jambonz, and point the number at an application that runs your agent. jambonz answers the call, handles speech-to-text, turn-taking and text-to-speech, and talks to your LLM."
  - question: "Can I keep my existing voice agent code?"
    answer: "Usually. If your agent speaks to a speech-to-speech model such as OpenAI's realtime models, the jambonz llm verb connects the call to it directly. If your agent is a text LLM, the agent verb adds speech-to-text, turn detection and text-to-speech around it. If your agent already runs on a hosted platform that accepts SIP, jambonz can forward calls to it."
  - question: "Do I need to buy phone numbers from jambonz?"
    answer: "No. jambonz doesn't sell numbers, trunks or minutes. You use the numbers and SIP trunks you get from any carrier, at that carrier's rates."
  - question: "How long does it take to get a first call working?"
    answer: "With a phone number and a SIP trunk already in hand, adding them to jambonz and pointing the number at an application takes a few minutes. Most of the remaining time goes into your agent's prompt and tools."
---

**To get an LLM voice agent answering real phone calls, you need three things: a phone number, a SIP trunk to carry the calls, and a voice platform that turns those calls into conversations with your LLM.** Get the number and the trunk from any SIP trunking provider, add them to jambonz, and point the number at your agent. jambonz handles the telephony and the speech: answering the call, speech-to-text, deciding when the caller has finished talking, text-to-speech, and barge-in.

Here is the whole path, step by step.

## 1. Get a Phone Number and a SIP Trunk

jambonz is a [bring-your-own-carrier](/blog/voice-ai-bring-your-own-carrier) platform, so you get numbers from a carrier of your choice. Any SIP trunking provider will do. Buy a phone number (in carrier terms, a DID) and set up a SIP trunk. Many carriers let you do both in their portal in a few minutes.

If you already have numbers on a PBX or with another provider, you can use those instead.

## 2. Add the Carrier and the Number to jambonz

Sign up for [jambonz.cloud](https://jambonz.cloud/register), or use your own [self-hosted jambonz](https://docs.jambonz.org/guides/get-started/deployment-options). Then, in the portal:

1. [Add a carrier](https://docs.jambonz.org/guides/using-the-jambonz-portal/basic-concepts/creating-carriers) for your SIP trunk: the addresses your carrier sends calls from, the address jambonz should send calls to, and any username and password the carrier gave you.
2. On the carrier's side, point the SIP trunk at your jambonz SIP address.
3. [Add your phone number](https://docs.jambonz.org/guides/using-the-jambonz-portal/basic-concepts/creating-phone-numbers) and select the carrier it comes from.

## 3. Choose How jambonz Talks to Your Agent

How you connect depends on what you've built:

- **Your agent is a text LLM** (OpenAI, Anthropic, Gemini, Llama and others). Use the [agent verb](https://docs.jambonz.org/verbs/verbs/agent). It wires speech-to-text, your LLM and text-to-speech together, with turn detection, barge-in and tool calling built in. You pick each vendor.
- **Your agent uses a speech-to-speech model**, such as OpenAI's realtime models. Use the [llm verb](https://docs.jambonz.org/verbs/verbs/llm), which connects the caller's audio to the model directly.
- **Your agent already runs on a hosted voice AI platform** that accepts SIP. jambonz can forward the call to it, so you keep your agent and choose your own carrier. Our [Retell AI guide](/blog/using-jambonz-for-retell-custom-telephony) shows how.

## 4. Point the Number at Your Agent

Create an application in jambonz with the URL of your app, and assign it to your phone number. When a call arrives, jambonz connects to your app, and your app tells jambonz what to do. With the agent verb and the [Node.js SDK](https://docs.jambonz.org/sdks/node-sdk), that looks like this:

```js
session
  .agent({
    stt: { vendor: 'deepgram', language: 'multi' },
    tts: { vendor: 'cartesia', voice: '9626c31c-bec5-4cca-baa8-f8ba9e84c8bc' },
    llm: {
      vendor: 'openai',
      model: 'gpt-4.1-mini',
      llmOptions: {
        messages: [{ role: 'system', content: 'You are a helpful voice assistant.' }],
      },
    },
    bargeIn: { enable: true },
  })
  .send();
```

The [voice agents guide](https://docs.jambonz.org/guides/features/voice-agents) covers the rest: tools and MCP servers, handing the call to a human, and tuning turn detection. There are runnable examples in the [jambonz examples repository](https://github.com/jambonz/v10-examples/tree/main/examples/agent).

## 5. Call Your Number

That's it: call the number, and your agent answers.

## Where to Go from Here

- **Hand off to a human** when the agent should: see [voice agent handoff](/blog/voice-agent-handoff).
- **Make outbound calls** with the same agent, through the jambonz REST API.
- **Keep your data in your own cloud:** see how to [run jambonz in your own AWS account](/blog/voice-ai-contact-center-own-aws-account).

Questions about your setup? [Contact us](mailto:support@jambonz.org?subject=Voice%20agent%20on%20phone%20calls).
