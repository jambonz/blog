---
title: "Introducing Agent Studio: build voice AI agents on jambonz"
date: 2026-11-04
description: "Agent Studio is now in preview: build a voice AI agent with the speech and model vendors you choose, test it in the browser, and put it on a real phone number."
author: "Dave Horton"
tags: ["agent-studio", "voice-ai", "agent", "llm", "turn-detection"]
ogImage: "og-agent-studio.jpg"
---

Today we're launching **Agent Studio** in preview. It's a builder for voice AI agents that runs on your own jambonz
account, on jambonz.cloud or self-hosted.

Agent Studio is built to make one thing fast: going from an idea to an agent that answers a real phone number,
with the speech and language vendors you choose. In the video below I build a receptionist for a fictional dental
practice from scratch. I give it the practice's FAQ, test it from the browser, change its voice, and put it on a
phone number. Then I call it from my phone and ask to speak to a person.

<iframe style="width: 100%; height: auto; aspect-ratio: 16 / 9;" src="https://www.youtube.com/embed/iSDD9UVEJ0U" title="Introducing Agent Studio: build a voice AI agent on jambonz" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## What's different

**You pick every vendor.** A pipeline agent has three parts: speech-to-text, the language model and the voice.
Each one can be any vendor jambonz supports, with your own keys. So you choose for latency, quality or cost, one
piece at a time, and change your mind later without rebuilding the agent.

**Turn-taking is your choice too.** Some speech-to-text models, such as Deepgram Flux, detect the end of a turn
themselves. Or you can use Krisp's turn model, which listens to how the caller speaks, not just for a pause, and
works with any speech-to-text vendor.

**Every call can be inspected.** Each call, test or real, keeps its transcript, its timing and a full trace. When
something goes wrong, you can see what happened instead of guessing.

**Changes are safe to ship.** Prompts are built from blocks, and guardrails can come from a shared library, so one
fix reaches every agent that uses it. Every published version is kept, so you can compare versions, roll back, or
split live calls between two versions to see which one does better.

**Four engines, one way of working.** Besides the cascaded pipeline, an agent can use a speech-to-speech model, a
hosted agent such as Dialogflow or ElevenLabs, or your own code. Phone numbers, tools, transfers and call history
work the same for all of them.

**No lock-in.** You can export any agent as a Node.js application and run it on jambonz yourself.

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

<!-- TODO before publishing: once the video is locked, add the transcript here in a <details> block. -->
