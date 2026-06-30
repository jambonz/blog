---
title: "Speech companies are failing at conversational AI"
date: 2023-05-06
description: "Conversational AI has unique needs that long-form transcription doesn't — endpointing control, prompt-aware APIs, and pause/resume billing. Three features speech vendors still aren't shipping."
author: "Dave Horton"
tags: ["conversational-ai", "asr", "speech-to-text", "deepgram"]
draft: false
---

It might seem that we're in a golden age of deploying speech technology into contact centers. You'd be forgiven for thinking that, what with the large numbers of new companies in the space, most funded with planeloads of VC cash, exciting new applications of AI to speech recognition, and strategic imperative that enterprises see in finally making automated voice interactions...well, not suck.

The truth, however, is that speech technology providers are still failing at conversational AI for the simple reason behind most business failures: they aren't listening to and anticipating their customers' needs.

As the creator of [jambonz](https://jambonz.org), the open source voice gateway for conversational AI, I've spent the past three years working with most of the commercial speech vendors. Based on that experience, I'm suggesting three high-value (and blindingly obvious) features for conversational AI that speech vendors need to implement to improve the conversational AI experience.

But first, let's begin by enumerating the different requirements that conversational AI has from long-form speech-to-text transcription. There are some seemingly subtle yet very important distinctions:

- Every piece of audio from a caller we transcribe in a conversational AI use case is in response to a question or a prompt. There is always something that we **just** asked or said to the user that he or she is responding to **now**. In other words, conversational AI is highly contextual on a *short-term* (query-response) basis.
- Conversational AI is about....(wait for it)...conversations. It's a two-way discussion, **even if we're only transcribing one side of it** (the caller). The conversation proceeds turn by turn. The deeper into the conversation we get, the more accurate and faster we ought to become at accurately transcribing what is being said. Conversational AI, therefore, is also highly contextual on a *medium-term* (conversation length) basis (and that context includes both sides of the conversation).
- During a conversation, there are times when we don't want or need to transcribe a caller's speech. We're in essence not listening to them for certain periods. For instance, we may want to make them listen to a lengthy prompt in full (perhaps for legal purposes). We need to be listening/transcribing most of the time, but not all of the time.

Those are simple properties of a conversational dialog that we can probably all agree on. So what? Well, from these properties we can draw the following critical features that we would require from the underlying speech recognition technology:

- fine-tuned control of endpointing,
- an API interface that includes relevant prompt, and
- suitable billing models.

Here's what I mean:

## Fine-tuned control of endpointing

"endpointing" is a feature wherein the speech provider uses speech energy detection to determine the end of an utterance and then returns a transcript for that utterance.

In conversational AI, we prompt the user, and then we want to gather their response. This process is somewhat more an art than a science as you can imagine. We want to get the user's full thought (i.e. not have the recognizer return only the first half of a sentence). Yet we also want to minimize the latency in the conversation (i.e., not have the recognizer take so long to determine the user has finished speaking that the conversation becomes laden with periods of unnatural silence).

All the speech providers that we support in the open source [jambonz](https://jambonz.org) conversational AI voice gateway support endpointing. But only one of them -- [Deepgram](https://deepgram.com) exposes via their API the ability to control the endpointing behavior.

Controlling endpointing behavior would be (and in the case of Deepgram, *is*) a highly useful feature. When I have a voicebot ask a user a question that implies a quick confirmation ("Would you like to speak to an agent?"), I'm expecting a yes/no answer. As a result, I want the endpointing to be very quick (maybe 500 milliseconds). If I'm asking the customer a broader question ("Please tell us how can we help you today?"), however, I want endpointing to wait for maybe 2 seconds of silence to make sure I get everything they want to say, which may, in this case, be more than a single sentence.

All speech providers should expose via their API the ability to control endpointing behavior.

## API interface that includes relevant prompt

Today, most of us are enchanted by the power of ChatGPT, right? And like me, I bet you're really impressed with how generative language models can create such high quality responses in response to nothing but prompt text.

If so, you might also find it strange that while **every time** we connect to a speech recognizer during conversational AI we have **just provided a prompt** to the caller, the speech provider's API apparently has no interest in knowing what that prompt was. Wouldn't that prompt help shape answers? For that matter, wouldn't that prompt also help determine the most effective endpointing configuration to use for the current user response?

Today, speech providers allow for things like hints in their APIs -- an array of words or phrases that should be "boosted" in terms of making the recognizer more aware of them. That's great, and we should have hints, but even more valuable than hints is the **question I just asked the user which she is now responding to**. And guess what -- we have that exact question, in text form, because we probably just did text-to-speech to generate that question!

So please, speech vendors, augment your APIs to let me tell you the current prompt the user is responding to with their speech. Then, use that information to create more accurate responses.

Some examples may be helpful:

- I just prompted the user, "Could you please spell your last name?", so the recognizer should now expect some spoken letters (i.e. don't transcribe "T" as "tee").
- I just prompted the user, "Could you tell me what is wrong with your medical equipment?", so the recognizer should automatically boost medical equipment words or phrases.
- I just prompted the user, "Is this the best number to call you back on?", so the recognizer should be prepared to return quickly after "yes", "no," or other confirmatory/negatory phrases.

## Suitable billing model

The billing model that most (all?) speech providers use is per-second billing for the time we are connected to the recognizer, sometimes rounded up to threshold. We get charged this regardless of whether we actively want a transcript at any given point in the conversation. This result leads to an implementation model where the voice gateway connects to the speech recognizer for each turn of the conversation, creates a transcript, and then drops the connection. In the next turn of the conversation, we will prompt the user, connect again to the recognizer, and get a new transcript.

Dropping and re-establishing the connection like this is done to save cost, but it isn't ideal for several reasons. For one thing, there's a bit of overhead each time in establishing the connection, during which speech from the user might be lost (though in [jambonz](https://www.jambonz.org/), we queue incoming voice frames during connection to avoid this).

More importantly, though, any chance for using longer term context to improve results is lost. Consider again the ChatGPT experience: the longer the conversation that you have with it becomes, the better results you receive. As the conversation proceeds, ChatGPT has more context to form its answers.

What speech providers should do is to provide an API that lets a [voice gateway platform like jambonz](https://www.jambonz.org/) connect once, at the start of the call. Then at any time during the connection, they should allow the voice gateway to call an API to "pause" recognition. During the paused interval, they shouldn't charge me and should simply discard any voice packets that are sent over the connection. When I'm ready to gather a response from the user again, I should be able to call an API to "resume" recognition over this same connection. Billing again can start at this point.

Most importantly, speech providers should use the enhanced context gained from the ongoing conversation to give me more accurate and faster results the deeper into the conversation we go.

## Conclusion

I hope I'll look back at this blog post in a year and laugh at how outdated it has become. I hope that I'll see an array of speech companies that really "get" conversational AI and have invested time and attention to properly support our use case. Unfortunately, that's not the situation today.

Conversational AI has some unique requirements for speech recognition, and today's speech providers are not meeting them. The result is that conversational AI experiences are by and large not matching the industry hype. Speech providers need to stop looking at transcription as a one-size-fits all solution and build the services that we in the conversational AI space need to create the experiences that will truly delight customers.

If you like what you've read, check out the [jambonz blog](/blog) or [subscribe to our newsletter](https://jambonz.us6.list-manage.com/subscribe?u=2ab4d55936b7267b749491c84&id=d75214535e).
