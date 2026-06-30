---
title: "Some initial thoughts on OpenAI's Realtime API"
date: 2024-10-07
description: "I added OpenAI's Realtime API to jambonz, then ran the caller's audio through Deepgram in parallel to compare accuracy and latency — and what that reveals about speech-to-speech vs. traditional ASR pipelines."
author: "Dave Horton"
tags: ["openai", "realtime-api", "asr", "deepgram", "voice-ai"]
draft: false
---

I spent the past weekend adding support for [OpenAI's Realtime API](https://openai.com/index/introducing-the-realtime-api/) to jambonz. My first impression was very positive: as others have reported, the conversational flow was very much at the tempo of a normal conversation.

I'd implemented support for interrupting the agent, so that worked nicely and I was able to have amazingly lifelike conversations with the agent. I'd also implemented support for function calls, so I was able to supply tools to the agent and see them used properly to increase the value content delivered by the conversation.

Then I decided to do a little experiment. I decided to use jambonz to create an application that would use the OpenAI API for a Voice/AI conversation, **while at the same time** sending the user's audio input to Deepgram for simultaneous speech recognition processing.

The goal was to compare the transcripts returned by OpenAI (Whisper) with those returned by Deepgram for the same audio stream, delivered simultaneously to each service. And furthermore, to measure the relative latency of each in processing the same realtime audio stream.

I chose Deepgram as the comparison because in my opinion they are the premier ASR vendor in terms of accuracy and latency for English language recognition.

## The setup

The setup consisted of a jambonz server running on an AWS EC2 instance, configured to receive calls from a Twilio Elastic SIP Trunk. The calls were routed to a jambonz application that simultaneously started a Voice/AI conversation with OpenAI API while streaming the caller's audio to Deepgram for recognition. To make it a fair comparison, I did not provide any phrase hints to Deepgram or other special configuration. The OpenAI and Deepgram services were both accessed via their hosted endpoints, and my EC2 instance was in the us-east-2 region of AWS.

## The measurements

The OpenAI API provides a wealth of event data during the conversation by means of [server events](https://platform.openai.com/docs/guides/realtime/server-events) that it sends back over the websocket connection. These include `conversation.item.input_audio_transcription.completed` which is emitted when a final transcript is made from a user utterance. So I used this event to determine when OpenAI, and the underlying Whisper ASR, had completed speech recognition of the user's speech and what it determined that the user had said.

Similarly, Deepgram also provides events over a websocket interface that include both partial and final transcripts. I used the arrival of final transcripts for the same user utterance to compare with OpenAI.

## The conversation

For this test, I had a conversation where I asked OpenAI a series of questions about Alexander the Great. You can listen to the conversation below, it went pretty well although you'll hear the OpenAI assistant misunderstood one of my questions at the end and had to be nudged back on track. All in all though, a very positive conversation experience, especially since I was calling in from my mobile phone and not making any effort to speak more clearly or slower than usual.

You can listen to the conversation [here](https://recordings.jambonz.cloud/alex-the-great-conversation-with-openai.mp3)

However, when we look at the detail of the transcripts that OpenAI made and the latency compared to Deepgram, we find that OpenAI is both less accurate and slower. Let's go through the conversation turn by turn, and look at what happens:

### Turn by turn analysis

#### Turn 1
- Assistant: _"How can I help you today?"_
- Me: _"Well, I'd like to ask some questions about Alexander the Great."_
- OpenAI transcript: _"Well, I'd like to ask some questions about Alexander the Great."_
- Deepgram transcript: _"well i'd like to ask some questions about alexander the great"_
- latency: Deepgram faster by **0.965 secs**

> So far, so good. Both OpenAI whisper and Deepgram return accurate transcripts, with Deepgram being faster.

#### Turn 2
- Assistant: _"Sure, I'm happy to help! What do you want to know about Alexander the Great?"_
- Me: _"Well, I understand he had a pretty brief reign, can you tell me about when that was?"_
- OpenAI: _"understand he had a pretty brief reign. Can you tell me a little bit about when that was?"_
- Deepgram: _"well i understand he had a pretty brief rein can you tell me a little bit about when that was with"_
- Latency: Deepgram faster by **3.12  secs**

> Again, both basically captured what I said in a form that was understandable to the LLM. However, OpenAI missed the first two words I spoke. This seems to be an intermittent problem with OpenAI because I have observed it on multiple occasions. Deepgram was basically accurate though strangely it invented the word "rein".
> In this turn, Deepgram was  much faster than OpenAI. However, if you listen to audio you can see the slower latency did not impact the conversational flow in a noticeable way. More on that later.

#### Turn 3
- Assistant: _"Certainly! Alexander the Great reigned from 336 BC until his death in 323 BC. Despite the brevity of his reign, he created one of the largest empires in history, stretching from Greece to Egypt and into northwest India. Quite the accomplishment for about 13 years of work, wouldn't you say?"_
- Me: _"How far into Asia did his empire extend and where did he stop?"_
- OpenAI: _"How far into Asia did his empire extend and where did he stop?"_
- Deepgram: _"how far into asia did his empire extend and and where did he stop"_
- Latency: Deepgram faster by **1.64  secs**

> Everything still going well and both recognizers achieved accurate transcripts.

#### Turn 4
- Assistant: _"Alexander's empire extended as far as the Hyphasis River, known today as the Beas River, in what is now the Punjab region of modern-day India and Pakistan. He reached this point in 326 BC, but his troops, exhausted and longing to return home, mutinied, forcing him to turn back. So, he never actually lost a battle, but his campaign ended due to the morale and fatigue of his army."_
- Me: _"I thought he actually stopped at the Inus river. Am I wrong?"_
- OpenAI: _"I thought he actually stopped at the Inis River, am I wrong?"_
- Deepgram: _"i thought he actually stopped at the ines river am i wrong"_
- Latency: Deepgram faster by **1.9  secs**

> Both recognize the utterance.

#### Turn 5
- Assistant: _"Ah, close but not quite! Alexander reached the Hyphasis River—modern-day Beas River— and intended to push further into the Indian subcontinent toward the Ganges River. However, his army, weary and anxious about facing larger armies and more war elephants, refused to march further east. This forced Alexander to turn back, marking the easternmost extent of his conquests, rather than at the Indus River."_
- Me: _"In those days, I understand many people thought of Alexander as a god or the son of a god.  But what about his generals? How did they regard him?"_
- OpenAI: _"In those days, I understand many people thought of Alexander as the son of a god.  But what about his generals? How did they regard him?"_
- Deepgram: _"those days understand many people thought of alexander as god or a son of a god but what about his generals how did they regard him"_
- Latency: Deepgram faster by **1.63  secs**

> Conversation still on track and user utterances being recognized more or less accurately by both recognizers, though OpenAI missed the reference to "a god".

#### Turn 6
> Here things start to get a little more interesting..
- Assistant: _"Alexander's relationship with his generals was complex. While many respected and admired him for his brilliance and battlefield successes, there was also tension. Alexander's adoption of Persian customs and his claim to divine status, presenting himself as the son of Zeus-Ammon, created friction. Some generals felt alienated by his shift away from traditional Macedonian ways, leading to conspiracies and tension within his ranks. Nonetheless, his unparalleled success in expanding the empire often kept them loyal, despite their personal misgivings. His ability to maintain control over such a vast and diverse group was a testament to his leadership and charisma."_
- Me: _"On a modern day map where is Macedonia?  I understand Macedonia is where he's from, is that right?"_
- OpenAI: _"On a modern day map, where is Macedonia? I understand Macedonia's where I'm from, is that right?"_
- Deepgram: _"on a modern day map where is macedonia i understand macedonian is where he's from is that right"_
- Latency: Deepgram faster by **1.36  secs**

> Here OpenAI makes an interesting mistake. I said "he's from" but it transcribed "I'm from" even though those two utterances don't sound alike. I don't think this is a one-off error either, as I spotted other instances where I used a pronoun like "you" and OpenAI returned a transcript with "I" instead. We'll note in the next turn though that OpenAI's LLM does not get knocked off track by this error - an example of the LLM "covering up" for mistakes in the Whisper ASR.

#### Turn 7
- Assistant: _"That's right, Alexander the Great was from Macedon, an ancient kingdom located in the northern part of Greece. On a modern map, the region that was ancient Macedon is mostly in the northern part of Greece, ..(interrupted)."_
- Me: _"How did he defeat Greece..in the first part..in the first place?"_
- OpenAI: _"How did he eat reef?  in the first place."_
- Deepgram: _"how did he defeat greece in the first part, the first place"_
- Latency: Deepgram faster by **0.53  secs**

> Whoops. Now OpenAI Whisper has failed and recognized "defeat" as "eat" and "Greece" as "reef". Meanwhile, Deepgram recognizes the statement correctly. This will briefly derail the conversation in the next turn.

#### Turn 8
- Assistant: _"Alexander the Great died in 323 BC in the palace of Nebuchadnezzar II in Babylon, which is in modern-day Iraq. The exact cause of his death remains a mystery and has been the subject of much ..(interruption)."_
- Me: _"How did he defeat mainland Greece was the question."_
- OpenAI: _"How do you eat mainland Greece? was the question."_
- Deepgram: _"how did he defeat mainland greece was the question"_
- Latency: Deepgram faster by **0.80  secs**

> Given another chance, OpenAI still does not accurately understand what I said while Deepgram does. But now something really interesting happens. Even though the Whisper ASR returns an incorrect, meaningless (how would one eat "mainland Greece"?), and misleading transcription, the LLM again manages to use its context to power through to a response that is on target.

#### Turn 9
- Assistant: _"My apologies for the confusion. Alexander the Great never actually invaded mainland Greece. He was from Macedon, which was a kingdom located to the north of the Greek city-states. After the assassination of his father, King Philip II, in 336 BC, Alexander became king and continued his father's efforts to unite the Greek city-states under Macedonian hegemony. Alexander's influence over Greece was solidified by his role as the leader of the Corinthian League, a coalition of Greek states. From there, he launched his campaign against the Persian Empire, which is where most of his famous conquests took place. So, rather than invading mainland Greece, Alexander integrated it into his empire before embarking on his legendary campaigns across Asia."_

## Conclusions

### Deepgram is more accurate
Deepgram fairly consistently returned more accurate transcripts. OpenAI return two transcripts that had significant errors (I define "significant" as an error that could potentially derail the conversation) while Deepgram returned none.

#### BUT, it doesn't always matter
The errors in the Whisper ASR were sometimes handled or "covered up", if you will, by the OpenAI LLM model. Presumably, the previous context of the conversation up to that point is used to inform the model in a way that lets it answer accurately even within some range of incorrect transcriptions.

### Deepgram is faster
Deepgram was faster in returning final transcripts in every turn of the conversation, by significant amounts.

### BUT, the conversation latency was still extremely low
Even though Whisper had greater latency, the conversation flowed at near-human tempo. Why is this? Why does OpenAI not pay a noticeable penalty for the slower latency? Most likely because of the nature of streaming recognized tokens into the LLM. Even though the full transcript took longer, the ability to stream tokens well before the final transcript was created allows the rapid conversational response.

### Context matters, and what this says about ASR APIs in general
We can see here that speech-to-speech APIs enjoy a big advantage over more traditional "voice => ASR => text => NLU/Intent/Dialog => text => TTS => voice" pipelines, and that is....**Context**. We see context of the conversation being used here to improve results and rub out imperfections in transcriptions.

In the more traditional speech-to-text APIs provided by speech vendors this opportunity for context is lost, for several reasons:

1. When we send speech to the ASR for transcription, the ASR has no knowledge of what question or prompt we just served up to the user. In other words, the users speech is in response to some prompt, but the ASR has no knowledge of what that prompt was. This is a shortcoming I have cited for some time - see my earlier blog post: [Speech companies are failing at Conversational AI](/blog/speech-companies-are-failing-at-conversational-ai), but so far I have been unsuccessful to get speech companies to recognize the opportunity here to expand their apis to take advantage of this.
2. Often, in traditional ASR, each distinct utterance sent to the speech vendor is treated as a separate, standalone utterance. The ASR does not even have the ability to comprehend that 10 different utterances from the same user are all part of the same conversation, and likely on the same topic.

This makes the traditional voice => speech => pipeline much more brittle and easier to derail than speech-to-speech. But it does not need to be this way, and I do not conclude that speech-to-speech will necessarily dominate in areas like CXAI.

Why is this? Because first, the only significant improvement (and make no mistake, it is hugely significant) that speech-to-speech offers is that it approaches human-level conversational flow. But to the extent that this is due to more effective use of context, as I've just described, this is something that can be radically improved in the traditional voice=>text=>voice pipeline, as I have also just described.

Second, to be usable in CXAI environments by global brands, guardrails are necessary. And guardrails inevitably damage latency. Traditional NLU/Intent/Dialog based CXAI platforms already have guardrails built in, and if you start losing a significant amount of the latency improvement in speech-to-speech all you are left with is a more expensive solution without that compelling differentiator.

Visit us at jambonz.org or email us at support@jambonz.org to learn more, or to find out about installing your own jambonz voice platform for Voice/AI applications.
