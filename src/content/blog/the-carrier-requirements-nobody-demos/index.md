---
title: "Mutual TLS and Static IP Requirements for Voice AI Carrier Integrations"
date: 2026-08-20
description: "Carriers requiring mutual TLS and a static IP will reject a trunk before the first SIP message. Here is what each requires and how jambonz configures both."
author: "Dave Horton"
tags: ["tls", "security", "carriers", "self-hosting"]
---

Voice AI demos are about [latency](https://jambonz.org/blog/text-to-speech-latency-the-jambonz-leaderboard), interruption handling, and how natural the [agent](https://docs.jambonz.org/verbs/verbs/agent) sounds. None of
that is what stops a project. What stops a project is a carrier saying "we don't accept traffic
configured that way", three weeks before go-live.

Two requirements come up again and again, and both are pass/fail. Either your platform can do it or
the trunk cannot exist. There is no clever application logic that gets you around them.

## What Is Mutual TLS and Why Do Carriers Require It?

Ordinary [SIP](https://docs.jambonz.org/verbs/verbs/sip-request) over [TLS](https://docs.jambonz.org/self-hosting/overview/setting-up-web-rtc-and-sip-tls) proves the carrier's identity to you. Mutual TLS also proves yours to them:
during the handshake their SBC asks for a certificate, and you have to present one it trusts.

This is common in regulated work, like collections, healthcare, financial services. In our experience the
carriers who require it treat it as a fixed property of their platform. They are not going to turn it
off for one tenant, however well you ask.

What makes it unforgiving is *where* it fails. The TLS handshake collapses before a single SIP message
is exchanged. There is no 4xx to inspect, no retry, no fallback path, nothing to log at the SIP layer.
Either your platform can present a client certificate on an outbound connection, or that trunk is
simply unavailable to you.

## Configuring Mutual TLS in jambonz 11.1.2

jambonz supports mutual TLS as of **11.1.2.** You configure one identity per server and it is presented whenever a
carrier asks for one, and nothing is sent to carriers that don't ask, so it is harmless for the rest
of your trunks. There is nothing to enable per carrier.

The whole change is a `<client>` element in the `<sip>` section of `/etc/drachtio.conf.xml`:

```
<sip>
   <contacts>
   </contacts>

   <tls>
      <key-file>/etc/letsencrypt/live/sip.example.com/privkey.pem</key-file>
      <cert-file>/etc/letsencrypt/live/sip.example.com/fullchain.pem</cert-file>
      <chain-file>/etc/letsencrypt/live/sip.example.com/fullchain.pem</chain-file>

      <!-- START OF NEW SECTION FOR mTLS -->
      <client>
         <key-file>/etc/drachtio/tls/carrier-client.key</key-file>
         <cert-file>/etc/drachtio/tls/carrier-client.pem</cert-file>
         <ca-file>/etc/ssl/certs/ca-certificates.crt</ca-file>
      </client>

      <verify-server-cert>true</verify-server-cert>
      <verify-server-name>true</verify-server-name>
      <sni>true</sni>
      <!-- END OF NEW SECTION FOR mTLS -->

   </tls>

   <udp-mtu>8192</udp-mtu>

   <reject-register-with-no-realm>true</reject-register-with-no-realm>

</sip>
```

## Why You Cannot Reuse Your Existing SIP TLS Certificate

You cannot reuse the TLS certificate you already have for SIP.

Two reasons, and the second is recent enough that most people haven't hit it yet.

First, a carrier requiring mutual TLS wants a certificate issued by an authority *they* trust. If they
accepted the public authorities, anyone holding a Let's Encrypt certificate could authenticate as you.

Second, a certificate has to carry the `clientAuth` extended key usage to work as a client certificate
at all — and the publicly trusted authorities are being taken out of that business entirely. Under
Chrome root program policy, subordinate CAs disclosed after **15 June 2026** may assert only server
authentication, and from **15 March 2027** every newly issued public TLS certificate will be
server-authentication only. Let's Encrypt issued its last client-capable certificate on **8 July
2026**. The stated migration path across the industry is that client authentication belongs in a
private or enterprise PKI.

So, the instinct to reach for a well-known public CA is the one thing that is actively being removed.
A certificate with only `serverAuth` is rejected outright, however well it is trusted, and the error
you get — `unsupported certificate purpose` — looks nothing like the actual cause.

### Where to Get a Client Authentication Certificate

What works is a certificate from an authority the carrier trusts specifically: a small CA of your own
that they load, a commercial client-authentication or industry PKI they already accept, or their own
CA signing your request. We've documented all three, with the openssl commands, in [Mutual
TLS](https://docs.jambonz.org/self-hosting/overview/mutual-tls).

## Why Carriers Require a Static IP Address for SIP Traffic

The second requirement is even less glamorous: many carriers allowlist by source address. They want
to be told the IP your SIP traffic will come from, and they want it to stay that way.

This is where managed platforms struggle. Running on shared
infrastructure, the best they can usually offer is a published range of egress addresses. Sometimes a
large one. A /21 and a /19 together are around ten thousand addresses.

A carrier that asks for your IP will not always accept that. And when they do, look at what has been agreed upon: an allowlist covering every address the platform might egress from is an
allowlist that admits every other tenant on that platform. It satisfies the paperwork without
providing the isolation the carrier asked for.

There is a related problem in the other direction. If the platform's SIP hostname resolves to an
address with a short TTL, there is nothing stable to put in a carrier's routing table, and some
carriers configure inbound routing by address rather than by name.

A [self-hosted jambonz](https://docs.jambonz.org/self-hosting/overview) runs on your own instance with your own address. One IP, yours alone, stable
across restarts, that you can put in an email and that will still be true next quarter. It is a boring
answer to a boring question, and it closes the conversation.

## The SBC Workaround and What It Costs

Neither of these is a secret. If you go looking, you will find customers of the managed platforms
being told the same thing by support: put a SIP proxy or session border controller of your own in
between, and let it deal with the carrier.

That advice is correct. It is also an admission. The suggestion is that you operate the exact
component you were paying the platform to operate for you, and it does not remove the requirement,
it relocates it to infrastructure you now own.

And it is not free. A back-to-back user agent sits in the signalling path, and usually the media path
too, for the entire duration of every call. That is something else to scale, to make highly available,
to monitor, and to pay for per minute. It lengthens the media path for every call, including the ones
that never needed it. You have taken on the operational burden of self-hosting while still paying for
a managed service.

If you own the SIP stack, both of these requirements are configuration rather than architecture.

## Questions to Ask Before You Choose a Voice AI Platform

If you are evaluating platforms for production [telephony](https://jambonz.org/blog/using-jambonz-for-retell-custom-telephony), these are cheap questions to ask up front
and expensive ones to discover during integration:

- Can it present a client certificate on outbound TLS, and can I choose the certificate?
- Can I give the carrier a single, stable IP address that I control?

We built [jambonz](https://jambonz.cloud/register) so that the answer to both is yes.
