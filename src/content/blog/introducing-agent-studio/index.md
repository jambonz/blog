---
title: "Introducing Agent Studio: one framework for voice AI agents"
date: 2026-11-04
description: "Agent Studio, now in preview, brings cascaded pipelines, speech-to-speech models, hosted agents and your own code into one framework for building voice agents on jambonz."
author: "Dave Horton"
tags: ["agent-studio", "voice-ai", "agent", "speech-to-speech", "llm"]
ogImage: "og-agent-studio.jpg"
faq:
  - question: "What is jambonz Agent Studio?"
    answer: "Agent Studio is a builder for voice AI agents that run on jambonz. It brings four ways of building a voice agent into one framework: a cascaded pipeline of speech-to-text, a language model and text-to-speech; a speech-to-speech model; a hosted agent platform; or your own code. Phone numbers, tools, transfers, testing and call traces work the same way for all four. It works with jambonz.cloud or self-hosted jambonz deployments running version 11.1.11 or greater."
  - question: "What is the difference between a cascaded pipeline and a speech-to-speech voice agent?"
    answer: "A cascaded pipeline chains three components: speech-to-text transcribes the caller, a language model decides what to say, and text-to-speech speaks the reply. You choose each vendor separately, which gives the most control over cost, quality and voice. A speech-to-speech model hears and speaks in one step, which usually means lower latency and more natural turn-taking, but one vendor handles the whole conversation. In Agent Studio both are engines of the same agent, so you can switch between them without rebuilding anything else."
  - question: "Which speech-to-speech models does Agent Studio support?"
    answer: "At launch: OpenAI Realtime (gpt-realtime and gpt-realtime-mini), OpenAI GPT Live (gpt-live-1), Rime Prism, Deepgram Voice Agent and Ultravox. Each one uses a speech-to-speech credential already set up in your jambonz account."
  - question: "Can I put a Dialogflow CES or ElevenLabs agent on a phone number?"
    answer: "Yes. The hosted engine connects a phone number to an agent you already run in Dialogflow CES or ElevenLabs Agents. The agent is still built in the vendor's console; Agent Studio provides the telephony, transfers to a person and call history around it."
  - question: "What is a Voice AI custom harness?"
    answer: "A custom harness lets your own code decide what the agent says while jambonz handles the call audio. jambonz transcribes the caller and speaks your replies, and your server receives the conversation over one WebSocket per call. Prompts, history, guardrails and whatever framework you prefer stay in your code. The protocol is documented at docs.jambonz.org/agent-studio/custom-harness."
  - question: "Do I need a jambonz account to use Agent Studio?"
    answer: "Yes. Agent Studio runs on your own jambonz account and connects to it with an account SID and an API key. That can be a jambonz.cloud account, including a free trial, or a self-hosted jambonz system running version 11.1.11 or later."
  - question: "Is Agent Studio free?"
    answer: "Yes. Agent Studio itself is free to use. Your calls still run on your jambonz account and use the speech and AI vendors you choose, with your own keys, so those are billed as usual by jambonz.cloud or the vendors."
  - question: "Do I need to host my own application server for a jambonz voice agent?"
    answer: "Not with Agent Studio. A jambonz application normally needs a webhook or WebSocket server that you run and keep online. Agent Studio hosts that runtime for you, so an agent you build answers calls with no server of your own. The one exception is a custom harness, where you provide a websocket server that runs your own code."
  - question: "Can I use Agent Studio in production while it is in preview?"
    answer: "Yes. Preview means features and screens may still change as we go, not that it is only for experiments. Agents built in Agent Studio answer real calls on real phone numbers."
  - question: "Will Agent Studio change my existing jambonz applications or phone numbers?"
    answer: "No. It uses the phone numbers, carriers and speech credentials already in your jambonz account and never adds its own. Your existing applications are left alone, and a number only routes to an agent when you assign it to one."
  - question: "Can I test a voice agent without a phone number?"
    answer: "Yes. You can call any agent from the browser, and the test shows the live transcript, each tool call and a trace with the timing of every step. When it behaves the way you want, assign it a phone number and call it for real."
  - question: "Does Agent Studio support call handoff to a person?"
    answer: "Yes, Agent Studio supports four different modes of call transfer or handoff. A blind transfer hands the caller over straight away, either by SIP REFER to your carrier or PBX or as a call bridged by jambonz. A warm transfer puts the caller on hold while the agent reaches the person first, and either connects them with no briefing or briefs the person before connecting them. A three-way warm transfer briefs the person with the caller still on the line, so both hear it. The brief can be the model's own summary of the call or follow a template you write, and if a transfer is not answered, is busy, is declined or reaches a machine, you choose whether the caller goes back to the agent, is sent to another jambonz application or is hung up on. Handoff works with every engine: pipeline, speech-to-speech, hosted agents and a custom harness."
  - question: "Can I export an Agent Studio agent as code?"
    answer: "Yes. Any agent can be exported as a jambonz Node.js application: a plain WebSocket app built on @jambonz/node-client-ws that you can run and change yourself. Credentials are not included in the export; the app refers to them by name in your jambonz account."
---

The Voice AI world has split into four camps. 
- Those who build **cascaded voice pipelines**, where speech-to-text, a language model and a
voice are chained together to provide a harness with maximum flexibility and choice,
- Those who love the super low latency of **speech-to-speech** models that hear and speak in one step,
- Those who prefer **hosted agent** platforms like Dialogflow CES or Elevenlabs, and
- Those developers who want to craft **custom Voice AI harnesses** using their own code. 

Until now, each came with its own development environment, its own tool-calling conventions, and its own way of finding out what went wrong.

Today we're launching **Agent Studio** in preview. It's a unified framework that brings all four architectures together in one application design and runtime environment, running on your own jambonz account, whether that be [jambonz.cloud](https://jambonz.cloud) or [self-hosted](https://docs.jambonz.org/self-hosting/overview).

## Four engines, one way of working

Every agent in Agent Studio picks an engine:

- **Cascaded pipeline:** speech-to-text, a language model and a voice, each from any vendor jambonz supports, with
  your own keys.
- **Speech-to-speech:** a single model that listens and speaks.
- **Hosted:** an agent you already run on a platform such as Dialogflow or ElevenLabs.
- **Custom harness:** your own code does the thinking.

Everything around the engine is shared. Phone numbers, tools, transfers to a person and call history work the
same way whichever engine is behind the agent, and every call keeps its transcript, its timing and
a full trace. So you can change engines as the models change without rebuilding your telephony, your tooling or
the way you debug. 

## See it in action

In the video I build a receptionist for a fictional dental practice from scratch, using the cascaded pipeline. I
give it the practice's FAQ as a knowledge base, test it from the browser, change its voice, and route a phone number to it. Then I call it
from my phone and ask to speak to a person. At the end there's a quick look at the other engines.

> **Tip:** the video shows a lot of on-screen detail. For the sharpest picture, open the player's settings (⚙),
> choose **Quality**, and pick **1080p**.

<iframe style="width: 100%; height: auto; aspect-ratio: 16 / 9;" src="https://www.youtube.com/embed/iSDD9UVEJ0U" title="Introducing Agent Studio: one framework for voice AI agents" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

A few things the video shows along the way:

**You pick every vendor.** In a pipeline agent you choose speech-to-text, the model and the voice one piece at a
time, for latency, quality or cost, and change your mind later without rebuilding the agent.

**Turn-taking is your choice too.** Some speech-to-text models, such as Deepgram Flux, detect the end of a turn
themselves. Or you can use Krisp's turn model, which listens to how the caller speaks, not just for a pause, and
works with any speech-to-text vendor.

**Every call can be inspected.** When something goes wrong, the call's trace shows what happened, down to which
knowledge-base search ran and how long each step took, so you don't have to guess.

**Changes are safe to ship.** Prompts are built from blocks, and guardrails can come from a shared library, so one
fix reaches every agent that uses it. Every published version is kept, so you can compare versions, roll back, or
split live calls between two versions to see which one does better.

## It runs on jambonz

Agent Studio connects to a jambonz account with an account SID and an API key. It uses the phone numbers,
carriers and speech credentials already in that account. It never adds its own, and it leaves your existing
applications alone. Because jambonz is an open-source voice platform, your agents work with your carriers and
your SIP setup.

And there's no server to run. A jambonz application normally needs a webhook or WebSocket server that you host and
keep online. Agent Studio hosts that runtime for you, so an agent you build answers calls with nothing of your own
to deploy. The custom harness is the one exception, because there your own code is the point.

## Get started

Anyone can sign up at **[studio.jambonz.org](https://studio.jambonz.org/sign-up)** and connect a jambonz.cloud or
self-hosted jambonz account. It's a preview, so expect some rough edges and changes as we go, and please tell us what
you run into.

No jambonz account yet? Start a free trial at [jambonz.cloud](https://jambonz.cloud).

## What's next

Over the coming weeks I'll go deeper on each engine, starting with building a production pipeline agent.

<!-- TODO: once the video is locked, add the transcript here in a <details> block. -->
