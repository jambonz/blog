---
title: "Which Voice AI Platforms Let You Bring Your Own Telephony Carrier? (2026)"
date: 2026-10-21
description: "What bring-your-own-carrier (BYOC) means for voice AI, what to check before you choose a platform, and how jambonz connects any SIP trunk or PBX to your voice agents."
author: "Dave Horton"
tags: ["byoc", "sip", "voice-ai", "telephony", "carriers"]
faq:
  - question: "What does bring your own carrier (BYOC) mean for a voice AI platform?"
    answer: "It means the platform connects to the SIP trunking provider, PBX or SBC you already use, and to phone numbers you already own, instead of requiring you to buy numbers and minutes through the platform or its bundled CPaaS. You keep your carrier contracts, rates and numbers, and the voice AI platform handles the calls."
  - question: "Does jambonz let me bring my own carrier?"
    answer: "Yes. jambonz is a bring-your-own-carrier platform: it does not sell phone numbers, SIP trunks or minutes. You add your carriers (SIP trunks, PBXs or SBCs) and your phone numbers, then route each number to a voice AI application. You can use several carriers at once and choose which one handles each outbound call."
  - question: "Can I use my own carrier with a hosted voice AI platform like Retell?"
    answer: "Often, yes, through SIP. Some hosted voice AI platforms accept calls over SIP as custom telephony, and jambonz can sit between your carrier and that platform. Our Retell guide shows the setup."
  - question: "Do I have to self-host jambonz to bring my own carrier?"
    answer: "No. Bring your own carrier works the same on jambonz.cloud, our hosted service, and on a self-hosted jambonz in your own cloud account or data center."
---

**jambonz lets you bring your own telephony carrier.** It connects to any SIP trunking provider, PBX or SBC, uses the phone numbers you already own, and doesn't sell you numbers, trunks or minutes at all. Many hosted voice AI platforms instead bundle telephony through a single CPaaS, so the carrier, the per-minute rate and often the phone numbers come with the platform.

This post explains what bring your own carrier (BYOC) means for voice AI, what to check before you choose a platform, and how jambonz does it.

## Why the Carrier Matters for Voice AI

Telephony can be a large share of what a voice AI call costs. When a platform bundles a CPaaS, you typically pay its per-minute rate, any rounding it applies, and sometimes extra fees for streaming audio to your AI, on top of the AI itself. With your own carrier, you pay the rates you negotiated.

The carrier also decides practical things: which countries you can call, which numbers you can keep, whether you can meet local regulations, and what happens when that carrier has an outage. Being tied to one provider limits all of those choices.

## What to Check Before You Choose a Platform

If bringing your own carrier matters to you, ask these questions of any platform:

- **Any SIP provider?** Can it connect to any SIP trunk, PBX or SBC, or only to a short list of partners?
- **Your existing numbers?** Can you keep the numbers you have, or must you buy or port numbers through the platform?
- **More than one carrier?** Can you use several carriers at once, and choose one per call: for example, by destination country, or as a fallback?
- **Registration trunks?** Some carriers and PBXs require the platform to register with them, like a phone does. Does it support that?
- **Encryption?** Does it support SIP over TLS and encrypted media (SRTP)?
- **Where does it run?** Can you run it in your own cloud account if data residency or compliance requires that?

## How jambonz Does It

jambonz was built as a bring-your-own-carrier platform from the start.

- **Carriers:** you [add a carrier](https://docs.jambonz.org/guides/using-the-jambonz-portal/basic-concepts/creating-carriers) for each SIP trunk, PBX or SBC, with its inbound and outbound gateways and authentication. Carriers that require registration are supported, and jambonz sends calls for a registration trunk from the server that holds the registration.
- **Phone numbers:** you [add the numbers](https://docs.jambonz.org/guides/using-the-jambonz-portal/basic-concepts/creating-phone-numbers) you already have from your providers and point each one at an application.
- **Several carriers at once:** an outbound call can [name the carrier](https://docs.jambonz.org/guides/using-the-jambonz-portal/advanced-concepts/outbound-call-routing) to use, or follow destination-based routes you set up, such as one carrier for calls to a country where it is cheaper and another for everything else.
- **Encryption:** SIP over TLS is supported, and calls to devices that register over TLS are offered SRTP.
- **Your AI, your choice:** the application behind a number can be a [voice agent](https://docs.jambonz.org/guides/features/voice-agents) built with the [agent verb](https://docs.jambonz.org/verbs/verbs/agent) and the speech and LLM vendors you pick, a speech-to-speech model through the [llm verb](https://docs.jambonz.org/verbs/verbs/llm), or another platform reached over SIP.
- **Where it runs:** on [jambonz.cloud](https://docs.jambonz.org/guides/get-started/jambonz-cloud), or self-hosted in your own AWS, Azure or Google Cloud account.

## Using Your Own Carrier with a Hosted Voice AI Platform

If you have already built an agent on a hosted platform, you may not have to move it. Some platforms accept calls over SIP as "custom telephony", and jambonz can sit between your carrier and the platform: your carrier sends calls to jambonz, and jambonz sends them on to the platform over SIP. Our [Retell AI guide](/blog/using-jambonz-for-retell-custom-telephony) walks through this setup.

## Getting Started

1. Sign up for [jambonz.cloud](https://jambonz.cloud/register), or [deploy jambonz](https://docs.jambonz.org/guides/get-started/deployment-options) in your own cloud.
2. Add your carrier and your phone numbers.
3. Point a number at an application, and call it.

If you want to go further, read [how to connect an LLM voice agent to real phone calls](/blog/connect-llm-voice-agent-to-phone-calls), or [contact us](mailto:support@jambonz.org?subject=Bring%20your%20own%20carrier) about your carrier.
