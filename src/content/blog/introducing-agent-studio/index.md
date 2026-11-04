---
title: "Introducing Agent Studio: one framework for voice AI agents"
date: 2026-11-04
description: "Agent Studio, now in preview, brings cascaded pipelines, speech-to-speech models, hosted agents and your own code into one framework for building voice agents on jambonz."
author: "Dave Horton"
tags: ["agent-studio", "voice-ai", "agent", "speech-to-speech", "llm"]
ogImage: "og-agent-studio.jpg"
---

The Voice AI world has split into four camps. 
- Those who build cascaded voice pipelines, where speech-to-text, a language model and a
voice are chained together to provide a harness with maximum flexibility and choice,
- Those who love the super low latency of speech-to-speech models that hear and speak in one step,
- Those who prefer hosted agent platforms like Dialogflow CES or Elevenlabs, and
- Those developers who want to craft custom Voice AI harnesses using their own code. 

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

## Get started

Anyone can sign up at **[studio.jambonz.org](https://studio.jambonz.org/sign-up)** and connect a jambonz.cloud or
self-hosted jambonz account. It's a preview, so expect some rough edges and changes as we go, and please tell us what
you run into.

No jambonz account yet? Start a free trial at [jambonz.cloud](https://jambonz.cloud).

## What's next

Over the coming weeks I'll go deeper on each engine, starting with building a production pipeline agent.

<!-- TODO: once the video is locked, add the transcript here in a <details> block. -->
