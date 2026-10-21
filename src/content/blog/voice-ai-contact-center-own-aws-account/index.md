---
title: "Can You Run a Voice AI Contact Center in Your Own AWS Account? (2026)"
date: 2026-10-21
description: "Yes: jambonz runs in your own AWS account, connects to your own SIP trunks, and provides the voice layer of a contact center, from call routing and queues to recording, supervision and AI agents."
author: "Dave Horton"
tags: ["contact-center", "aws", "self-hosting", "sip", "voice-ai"]
faq:
  - question: "Can I run a cloud contact center in my own AWS account with my own SIP trunks?"
    answer: "Yes. jambonz deploys into your own AWS account from CloudFormation templates and connects to any SIP trunk, PBX or SBC you bring. Call records, recordings, logs and secrets stay in your account, under your IAM policies."
  - question: "Is jambonz a complete contact center suite?"
    answer: "No. jambonz is the voice layer of a contact center: carriers and phone numbers, call routing, IVR, queues, conferencing, recording, live supervision and AI voice agents. It does not include an agent desktop, workforce management or omnichannel chat; you build those, or connect the products you already use, through its webhooks, WebSocket API and REST API."
  - question: "Can human agents take calls in a self-hosted jambonz contact center?"
    answer: "Yes. Agents can take calls on SIP phones, a PBX, or WebRTC softphones in a browser. Calls can wait in queues, and supervisors can listen, whisper to the agent, or barge in."
  - question: "Is a self-hosted jambonz contact center on AWS SOC 2-ready?"
    answer: "The jambonz 11.1.6 CloudFormation templates include the infrastructure controls a SOC 2 auditor will test, such as secrets in Parameter Store, least-privilege IAM roles, an encrypted database and log retention. Your own policies, people's access and account-wide logging are still yours to put in place."
---

**Yes. jambonz runs in your own AWS account, connects to your own SIP trunks, and gives you the voice layer of a contact center:** carriers and phone numbers, call routing, IVR, queues, conferencing, recording, live supervision and AI voice agents. Calls, recordings and logs stay in your account, in the region you choose.

To be clear about what it is not: jambonz is not a packaged contact center suite. It has no agent desktop, workforce management or omnichannel chat. You connect those, or the CRM and helpdesk you already use, through jambonz's webhooks, WebSocket API and REST API. Teams that want full control of the voice side, and their data, choose this approach.

## Why Run It in Your Own AWS Account?

- **Data stays in your boundary.** Recordings, transcripts and call records stay in a VPC you own, under your IAM policies and your audit logs. That matters for banks, health systems, public-sector agencies and anyone bound to keep data in one country.
- **Your security tooling already covers it.** GuardDuty, CloudTrail, Security Hub and AWS Config apply to jambonz like any other workload.
- **Your carriers, your rates.** jambonz is a [bring-your-own-carrier](/blog/voice-ai-bring-your-own-carrier) platform, so you use the SIP trunks you already have.
- **Ready for a SOC 2 audit.** The jambonz 11.1.6 templates include the infrastructure controls an auditor will test. Our [SOC 2 guide for AWS](/blog/soc2-voice-ai-self-hosted-aws) walks through them.

## What jambonz Provides

**Telephony**
- Any SIP trunk, PBX or SBC, with your existing phone numbers.
- Several carriers at once, with [outbound routing](https://docs.jambonz.org/guides/using-the-jambonz-portal/advanced-concepts/outbound-call-routing) by carrier name or by destination.

**Call handling**
- IVR menus with speech and touch-tone input ([gather](https://docs.jambonz.org/verbs/verbs/gather)).
- Queues ([enqueue](https://docs.jambonz.org/verbs/verbs/enqueue) and [dequeue](https://docs.jambonz.org/verbs/verbs/dequeue)), including [priority queues](/blog/priority-queues-in-jambonz).
- Transfers and [conferences](https://docs.jambonz.org/verbs/verbs/conference).

**Human agents and supervisors**
- Agents on SIP phones, your PBX, or [WebRTC softphones](/blog/supporting-webrtc-clients-with-jambonz) in a browser.
- [Live supervision](/blog/call-center-supervision-with-jambonz): a supervisor can listen, whisper to the agent, or barge in.

**AI voice agents**
- Agents built from your choice of speech-to-text, LLM and text-to-speech vendors, or speech-to-speech models, with [handoff to a human](/blog/voice-agent-handoff) when the agent should.

**Recording**
- Call recordings streamed to your own cloud storage, and a [SIPREC server](https://docs.jambonz.org/guides/features/siprec-server) for recording calls from existing systems.

## What You Bring

- **An agent desktop and CRM:** your own, or the tools your team already uses, driven by jambonz webhooks and its REST API.
- **Reporting:** jambonz records call details and exposes them through its API; dashboards and workforce management are yours.
- **Your security program:** the account-level controls, policies and access reviews a SOC 2 audit expects.

## How to Deploy It

jambonz publishes public AMIs in 30 AWS regions, for amd64 and arm64. A script copies them into your account and generates a CloudFormation template for your region. For a production contact center we recommend the **large** deployment, where every role runs on its own servers and the SIP, media, feature server, web and recording tiers each scale on their own. The [AWS self-hosting guide](https://docs.jambonz.org/self-hosting/hosting-providers/aws) and our [SOC 2 walkthrough](/blog/soc2-voice-ai-self-hosted-aws) cover the steps.

If AWS isn't your cloud, the same is available on [Azure](/blog/soc2-voice-ai-self-hosted-azure) and [Google Cloud](/blog/soc2-voice-ai-self-hosted-gcp) through Terraform.

Planning a contact center on your own infrastructure? [Talk to us](mailto:support@jambonz.org?subject=Contact%20center%20on%20my%20own%20AWS%20account).
