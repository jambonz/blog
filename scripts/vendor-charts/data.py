"""Vendor lists behind the STT/TTS support charts. Counted by company, as of 14 Nov 2026.
Rules: hosted public API only, streaming STT only; no inference hosts, gateways,
local models, or a platform's own engine on its own platform."""
S=lambda s:[x.strip() for x in s.split(',')] if s else []
P=['jambonz','Twilio','Telnyx','LiveKit','Pipecat','Vapi','Retell','Bland']
stt={
'jambonz':S('AssemblyAI, AWS, Cartesia, Deepgram, ElevenLabs, Giggy, Gladia, Gnani, Google, Gradium, Inworld, KugelAudio, Meta, Microsoft, Mistral, Modulate, NVIDIA, OpenAI, Paxa, Saidwire, Sarvam, Smallest AI, Soniox, SoundHound, Speechmatics, xAI, Zoom'),
'Twilio':S('Deepgram, Google'),
'Telnyx':S('Deepgram, AssemblyAI, Google, Microsoft, Soniox, Speechmatics, xAI, NVIDIA, Reson8'),
'LiveKit':S('Deepgram, AssemblyAI, Google, Microsoft, Soniox, Speechmatics, xAI, Cartesia, ElevenLabs, Gladia, NVIDIA, OpenAI, AWS, Gradium, Meta, Mistral, Sarvam, Smallest AI, Gnani, Inworld, Naver Clova, Palabra, RTZR, Fish Audio, Rime, Nabrah, Reson8, Zoom, Lokutor'),
'Pipecat':S('Deepgram, AssemblyAI, Google, Microsoft, Soniox, Speechmatics, xAI, Cartesia, ElevenLabs, Gladia, NVIDIA, OpenAI, AWS, Gradium, Meta, Mistral, Sarvam, Smallest AI, Rime, Zoom'),
'Vapi':S('Deepgram, AssemblyAI, Google, Microsoft, Soniox, Speechmatics, xAI, Cartesia, ElevenLabs, Gladia, OpenAI, Talkscriber, Reson8'),
'Retell':S('Deepgram, AssemblyAI, Microsoft, Soniox'),
'Bland':[]}
tts={
'jambonz':S('AssemblyAI, Async, AWS, Bland, CAMB.AI, Cartesia, Deepgram, ElevenLabs, Fish Audio, Giggy, Gnani, Google, Gradium, Hume, Inworld, KugelAudio, Microsoft, MiniMax, Mistral, Murf, Neuphonic, NineNineSix, NVIDIA, OpenAI, Paxa, Phonic, Resemble, Respeecher, Rime, Sarvam, Smallest AI, Soniox, Speechify, Speechmatics, Spitch, Svara, Vakyam, WellSaid, xAI'),
'Twilio':S('AWS, Google, ElevenLabs'),
'Telnyx':S('ElevenLabs, Inworld, AWS, Microsoft, Rime, xAI, Resemble, Murf, MiniMax, Fish Audio, Soniox, Alibaba, AssemblyAI'),
'LiveKit':S('ElevenLabs, Inworld, AWS, Cartesia, Microsoft, OpenAI, Rime, xAI, Deepgram, Google, Resemble, Gradium, Murf, NVIDIA, Speechify, MiniMax, Fish Audio, Hume, Neuphonic, Smallest AI, Soniox, Async, CAMB.AI, LMNT, Mistral, Sarvam, Speechmatics, Gnani, Palabra, Respeecher, Spitch, Uplift AI, Vakyam, AssemblyAI, Kalpa, Lokutor, Bland'),
'Pipecat':S('ElevenLabs, Inworld, AWS, Cartesia, Microsoft, OpenAI, Rime, xAI, Deepgram, Google, Resemble, Gradium, NVIDIA, Speechify, MiniMax, Fish Audio, Hume, Neuphonic, Smallest AI, Soniox, Async, CAMB.AI, Mistral, Sarvam, Speechmatics, AssemblyAI, HeyGen, Bland'),
'Vapi':S('ElevenLabs, Inworld, Cartesia, Microsoft, OpenAI, Rime, xAI, Deepgram, WellSaid, MiniMax, Hume, Neuphonic, Smallest AI, LMNT'),
'Retell':S('ElevenLabs, Inworld, Cartesia, OpenAI, MiniMax, Fish Audio'),
'Bland':[]}
