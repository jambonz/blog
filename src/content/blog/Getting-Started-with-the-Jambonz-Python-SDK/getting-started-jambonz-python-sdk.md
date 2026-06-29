# Getting Started with the Jambonz Python SDK

!\[Python code on a computer screen](Jambonz-Python-SDK.jpeg)

The AI developer community runs on Python. Most of the people building voice AI agents today are coming from that world, so asking them to context-switch into Node.js just to get a call working felt like unnecessary friction. That's why we built a Python SDK.

Here's what it looks like to use it. For the full reference, check out our docs.

📹 **Watch the walkthrough:** https://www.youtube.com/watch?v=WJvEBv0-4o4

## How the Jambonz Python SDK Structures Call Flows

Before diving into the code, it helps to understand how Jambonz thinks about calls.

Jambonz structures calls as a list of steps. You define what happens in order: speak something, listen for a response, route based on what you hear, and hang up. The code you write is the call that happens.

For simple menus and routing, you run over webhooks. For a conversation with an AI agent, you switch to a WebSocket. It's the same SDK and verbs, but a different transport.

## The Jambonz Python SDK Verbs You Need

The verb set is the same whether you are using Python or Node.js. These are the ones you will reach for most often:

1. `say` — speaks text to the caller.
2. `play` — plays an audio file.
3. `gather` — listens for speech or DTMF input.
4. `dial` — bridges the call to another number.
5. `agent` — builds a voice agent with STT, TTS, and an LLM.
6. `redirect` — sends the call to another voice application.
7. `hangup` — ends the call.

Everything is typed with Pydantic. Get a field wrong, and it tells you immediately, rather than after the call drops. Full verb reference is in the docs.

## How to Build a Python IVR With the Jambonz Webhook Transport

Webhooks are the right transport for menu-driven flows. Here is a basic IVR that greets the caller, listens for input, and routes accordingly.

```python
from aiohttp import web
from jambonz\_sdk.webhook import WebhookResponse

async def handle\_incoming(request: web.Request) -> web.Response:
    jambonz = WebhookResponse()
    jambonz.say(text="Welcome to the IVR.").gather(
        input=\["speech", "digits"],
        actionHook="/handle-input",
        say={"text": "Press 1 for sales or 2 for support."},
        timeout=5,
    )
    return web.json\_response(jambonz.to\_json())

async def handle\_input(request: web.Request) -> web.Response:
    body = await request.json()
    digits = body.get("digits", "")
    jambonz = WebhookResponse()
    if digits == "1":
        jambonz.say(text="Connecting you to sales.")
    elif digits == "2":
        jambonz.say(text="Connecting you to support.")
    else:
        jambonz.say(text="Invalid option.")
    jambonz.hangup()
    return web.json\_response(jambonz.to\_json())

app = web.Application()
app.router.add\_post("/incoming", handle\_incoming)
app.router.add\_post("/handle-input", handle\_input)
web.run\_app(app, port=8000)
```

When you configure the webhook in Jambonz, make sure the path matches your router. If your handler is at `/incoming`, that is what goes in the portal. To test locally, expose your server with ngrok and point Jambonz at the public URL.

## How to Build a Python Voice AI Agent With WebSockets

For a real AI conversation, switch to WebSocket transport. This enables bidirectional communication, event streaming, and mid-call updates.

```python
import asyncio
from jambonz\_sdk.websocket import create\_endpoint

async def main():
    make\_service, runner = await create\_endpoint(port=3000)
    svc = make\_service(path="/")

    async def handle\_session(session):
        async def on\_gather\_result(evt):
            transcript = (
                evt.get("speech", {})
                .get("alternatives", \[{}])\[0]
                .get("transcript", "")
            )
            session.say(text=f"You said: {transcript}").hangup()
            await session.reply()

        session.on("/gather-result", on\_gather\_result)
        session.say(text="Hello. Say something.").gather(
            input=\["speech"],
            actionHook="/gather-result",
            timeout=10,
        )
        await session.send()

    svc.on("session:new", handle\_session)
    await asyncio.Future()

asyncio.run(main())
```

Use `session.send()` for the initial verb array in response to `session:new`. For everything after that, use `session.reply()`.

Full WebSocket reference is in the docs.

## What Else Can You Build With the Jambonz Python SDK?

The SDK supports the full Jambonz verb set, including outbound calls via the REST client, mid-call control, audio streaming, LLM tool calls, and agent updates mid-conversation.

If you want to see the IVR demo running end to end, watch the full tutorial here. To go straight to the reference, start here. To get involved with the community, head here.

