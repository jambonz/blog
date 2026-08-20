---
title: "The carrier requirements nobody demos"
date: 2026-08-20
description: "Mutual TLS and a static IP address are two unglamorous carrier requirements that decide whether a voice AI integration is possible at all. Your platform choice determines whether you can meet them."
author: "Dave Horton"
tags: ["tls", "security", "carriers", "self-hosting"]
---

Voice AI demos are about latency, interruption handling, and how natural the agent sounds. None of
that is what stops a project. What stops a project is a carrier saying "we don't accept traffic
configured that way", three weeks before go-live.

Two requirements come up again and again, and both are pass/fail. Either your platform can do it or
the trunk cannot exist. There is no clever application logic that gets you around them.

## Mutual TLS

Ordinary SIP over TLS proves the carrier's identity to you. Mutual TLS also proves yours to them:
during the handshake their SBC asks for a certificate, and you have to present one it trusts.

This is common in regulated work — collections, healthcare, financial services. In our experience the
carriers who require it treat it as a fixed property of their platform. They are not going to turn it
off for one tenant, however well you ask.

What makes it unforgiving is *where* it fails. The TLS handshake collapses before a single SIP message
is exchanged. There is no 4xx to inspect, no retry, no fallback path, nothing to log at the SIP layer.
Either your platform can present a client certificate on an outbound connection, or that trunk is
simply unavailable to you.

As of jambonz **11.1.2** it can. You configure one identity per server and it is presented whenever a
carrier asks for one — and nothing is sent to carriers that don't ask, so it is harmless for the rest
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

### The part that catches everyone

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

So the instinct to reach for a well-known public CA is the one thing that is actively being removed.
A certificate with only `serverAuth` is rejected outright, however well it is trusted, and the error
you get — `unsupported certificate purpose` — looks nothing like the actual cause.

What works is a certificate from an authority the carrier trusts specifically: a small CA of your own
that they load, a commercial client-authentication or industry PKI they already accept, or their own
CA signing your request. We've documented all three, with the openssl commands, in [Mutual TLS to a
carrier](https://docs.jambonz.org/self-hosting/overview/mutual-tls-to-a-carrier).

## A static IP address

The second requirement is even less glamorous: many carriers allowlist by source address. They want
to be told the IP your SIP traffic will come from, and they want it to stay that way.

This is where managed platforms tend to struggle. Running on shared infrastructure, the best they can
usually offer is a published range of egress addresses — sometimes a large one. That is not always
acceptable to a carrier, and a range you don't control can change under you.

A self-hosted jambonz runs on your own instance with your own address. One IP, stable across restarts,
that you can put in an email and that will still be true next quarter. It is a boring answer to a
boring question, and it closes the conversation.

## Why platforms differ here

Some managed voice platforms don't present a client certificate on outbound TLS at all, and there is
no setting that changes it. When a customer hits that, the usual advice is to put a SIP proxy or
back-to-back user agent in front: terminate one leg, re-originate the other with the right
certificate.

That works. But it means adding a component to the live media path for the entire duration of every
call — something else to scale, to make highly available, to monitor, and to pay for per minute. It
relocates the requirement rather than removing it, and it makes the media path longer for every call
including the ones that never needed it.

If you own the SIP stack, both of these are configuration rather than architecture.

## Worth asking early

If you are evaluating platforms for production telephony, these are cheap questions to ask up front
and expensive ones to discover during integration:

- Can it present a client certificate on outbound TLS, and can I choose the certificate?
- Can I give the carrier a single, stable IP address that I control?

We built jambonz so that the answer to both is yes.
