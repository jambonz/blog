---
title: "The eMudhra Certificate Incident: What It Means for Your jambonz Platform"
date: 2026-10-26
description: "A set of intermediate certificates used by the certificate authority eMudhra can no longer be trusted. Here's how it affects self-hosted jambonz and exactly what to patch."
author: "Sam Machin"
tags: ["security", "tls", "certificates", "self-hosting", "voice-ai"]
faq:
  - question: "Is my jambonz platform vulnerable to the eMudhra certificate issue?"
    answer: "Server-to-server platforms like jambonz are a lower risk than end-user apps and browsers, because exploiting the flaw also requires an attacker to redirect your traffic to their server, usually through DNS or network compromise. But jambonz does make outbound TLS connections, so there are surfaces worth patching: webhooks and websockets from the node applications, audio and AI connections from the media server, and recording uploads."
  - question: "How do I fix the eMudhra certificate issue on jambonz?"
    answer: "There is no single trust store on a server, so there are a few places to patch. Upgrade Node.js to v22.23.4, v24.22.1 or v26.12.1 (or later), which removes the affected certificates from Node's built-in store. Update the system ca-certificates package to 20250419~deb12u2 or later on Debian 12, which covers the media server and recording uploads. New server images built from the updated packer scripts pull in the fixes automatically."
  - question: "Does setting NODE_USE_SYSTEM_CA fix Node.js?"
    answer: "No. Node's option to use the system trust store adds those certificates in addition to its own built-in store, so the affected certificates would still be trusted. The fix is to upgrade Node.js itself to a version that has removed them."
---

On the morning of 21 October 2026 an internet-wide problem came to light with a
set of intermediate certificates operated by the certificate authority
**eMudhra**. Those intermediates are used to sign TLS certificates, and they can
no longer be trusted.

This post explains what the issue is, why it matters less for server platforms
like jambonz than it does for your phone or laptop, and exactly what to patch on
a self-hosted jambonz deployment.

## Key Takeaways

- **A trusted CA's intermediate certificates have been compromised.** A bad actor
  could issue a valid-looking TLS certificate for a domain they do not own or
  control, and a client that connects would trust it as the real host.
- **Server platforms are a lower risk than end-user devices.** Exploiting this in
  the wild also requires redirecting the victim's traffic to the attacker's
  server, usually via DNS or network compromise — the kind of thing a malicious
  Wi-Fi network does to phones and laptops. jambonz talks server-to-server, which
  raises that bar.
- **jambonz still has TLS surfaces worth patching.** Webhooks, websockets, media
  connections and recording uploads all make outbound TLS connections.
- **The fix is to remove the affected certificates from your trust stores.**
  There is no single trust store per host, so this means upgrading Node.js *and*
  the system `ca-certificates` package.

## What happened

TLS — the padlock in your browser, and the encryption behind HTTPS, secure
websockets — depends on a chain of trust. Your device trusts a
small set of root certificate authorities, those roots vouch for intermediate
certificates, and the intermediates sign the certificates presented by the
servers you connect to.

When an intermediate certificate is compromised, that chain breaks. A bad actor
in possession of the affected eMudhra intermediates could issue a TLS
certificate for a domain they do not own — `google.com`, say — and a client that
connected to their server would see a certificate that chains back to a trusted
root and treat the connection as legitimate.

A full background on the incident, along with the details of the affected
certificates, is available at
[emudhra.we-have-a-problem.com](https://emudhra.we-have-a-problem.com/).

## Why this is a smaller problem for jambonz

Issuing a rogue certificate is only half of an attack. To actually use it, an
attacker also has to get the victim to connect to *their* server instead of the
real one. That normally means compromising DNS or the network path — for
example, a malicious Wi-Fi network silently pointing `api.example.com` at an
attacker-controlled address.

That is a realistic threat for end-user clients: phones, laptops and web browsers
that roam across untrusted networks. It is a much higher bar for a server-based
platform like jambonz, which runs on infrastructure you control and talks
server-to-server over known network paths.

So we consider this primarily a risk to client apps and browsers rather than to
jambonz itself. That said, "lower risk" is not "no risk", and a thorough fix
closes the server surfaces too.

## The TLS surfaces in a jambonz deployment

A jambonz installation makes outbound TLS connections in several places, each of
which validates certificates using a different trust store:

- **The node applications** (such as the feature-server) send webhooks and open
  websocket connections to your clients over TLS.
- **The media server** connects audio to listen websockets over TLS, and
  connects out to TTS, STT and LLM providers.
- **Recording upload** sends recording files to object storage over HTTPS/TLS.

Because these use different trust stores, there is no single place to apply the
fix — you patch each surface in turn.

## What to patch

The fix in every case is the same in principle: remove the affected certificates
from the trust store that each component uses.

### Node.js applications

Node.js ships with its own built-in trust store, separate from the operating
system's. The affected certificates have now been removed in:

- **Node 22:** v22.23.4
- **Node 24:** v24.22.1
- **Node 26:** v26.12.1

Upgrade your Node.js runtime to one of these versions (or later).

A word of warning on a tempting shortcut: Node has an option to use the system
trust store, but it does so *in addition to* its own built-in store rather than
instead of it. That means the affected certificates would still be trusted, so
it is **not** a fix here. Upgrading Node.js is the fix.

Our packer scripts have been updated to pin **24.22.1** as the minimum Node 24
version used when building new servers. If you build a fresh server image, you
get the fix automatically. To keep an existing server running, upgrade its
Node.js to one of the versions above.

### The media server and recording uploads

The media server and recording uploads rely on the operating system's trust
store rather than Node's. On Debian that is the `ca-certificates` package.

For Debian 12 hosts the fix is in **`20250419~deb12u2`** (note: `u2`, not `u1`).
Check your installed version with:

```bash
dpkg -l ca-certificates
```

For recording uploads specifically, the certificate is validated by one of two
clients depending on where you store recordings — the AWS SDK for S3 and
S3-compatible storage, or libcurl (built against OpenSSL) for providers such as
Azure and Google. Both ultimately use the system trust store, so the same
`ca-certificates` update covers them.

New server images built from our updated scripts pull in the latest
`ca-certificates` package automatically. On an existing server, the package is
normally kept current by unattended upgrades. You can confirm those are enabled
with:

```bash
systemctl status unattended-upgrades apt-daily-upgrade.timer
cat /etc/apt/apt.conf.d/20auto-upgrades
```

If automatic updates are not enabled, update the package manually.

## What you should do

1. **Upgrade Node.js** on your jambonz servers to v22.23.4, v24.22.1 or
   v26.12.1 (or later).
2. **Confirm `ca-certificates`** is at `20250419~deb12u2` or later on Debian 12
   hosts, and that unattended upgrades are keeping it current.
3. **Rebuild from current images** where you can — fresh builds pick up both
   fixes automatically.

If you run on **jambonz.cloud**, these fixes have already been applied — there's
nothing you need to do. If you self-host and have a support contract with us,
reach out — we're happy to help you work through the patching and confirm your
platform is covered.
