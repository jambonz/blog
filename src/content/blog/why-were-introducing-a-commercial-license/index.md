---
title: "Why we're introducing a commercial license"
date: 2026-01-20
description: "jambonz introduces a commercial license option to fund faster innovation — and, in return, to stop making self-hosting deliberately hard."
author: "Dave Horton"
tags: ["licensing", "commercial-license", "open-source", "self-hosting"]
---

Today we're introducing a commercial license option for jambonz. The open source version isn't going away—we'll continue to maintain it with security fixes and bug fixes—but over time new features will land first in the commercially licensed version.

**If you're an existing support customer, nothing changes for you**. You can continue on your current plan indefinitely with the same level of service. If you choose to migrate to the commercial version at some point, most customers will be able to do so at no additional cost. We're also offering an OEM license for those who need source code access and redistribution rights.

Now let me explain why we're doing this.

## Why this change now

We're making this change for two reasons:

- To increase the pace at which we deliver meaningful innovation to our customers, and
- To make the product more widely available to prospective customers.

When companies adjust their open source strategy, they often cite the same reason: sustainability of the project. That's true for us too, but I want to be more specific about what that means.

Our open source strategy served us well in the early days. When jambonz was new and I was the only developer, "free" was the right price to attract customers willing to take a chance on unproven software. It got us off zero. It worked.

But over time, the challenges facing us have changed, what it means to compete in the VoiceAI space has changed—and the cracks in our business model have become harder to ignore.

### The Paradoxes We've Been Living With

Here's something that's bothered me for years: to build a services-only business, we've had to make jambonz harder to deploy without our help. Our deployment scripts and know-how? We've deliberately withheld them from non-paying users, because support revenue is how we fund development.

This has never felt right to me. Many of our users have been frustrated by it too (maybe you were one of them). But when services are your only revenue, you have to create reasons for people to pay for services. The result is a worse product for everyone who isn't a customer yet.

Here's another paradox: the better jambonz works, the worse our business model worked. Support contracts look less necessary when things run smoothly. We frequently have customers sign up to get running, then cancel after a month or two because everything is working fine. We're penalized for building reliable software.

### The Math Doesn't Work Anymore

A services-only business is labor-intensive with thin margins. That limits what we can invest in the product. Meanwhile, VC-funded companies that we compete with have significantly more resources than our small team.

There's so much happening in this space right now. The product needs to evolve in multiple dimensions at once just to keep pace with the rate of innovation. If we stay on our current path, jambonz eventually becomes a project that can only afford security patches—no meaningful new development. That's not good for anyone.

### Being Honest About What I Want

I apologize for making this a bit personal, but perhaps you'll grant me this brief aside since jambonz was at the beginning, a personal passion project. I started jambonz because I wanted to challenge myself to build something large and ambitious. I'm in it for the innovation—for doing hard things that I find genuinely fun to try to do. I want to build great software and I want to build a great company.

To do that, we need the resources to compete. Services revenue alone won't get us there. Software licensing revenue will help.

## Making jambonz easier to deploy

There's a silver lining here. Once we're not dependent on making self-hosting difficult..well, we can stop doing that! We'll be able to provide our devops tools and deployment scripts to everyone. We'll make it much easier to spin up jambonz on your own infrastructure.

To start with, for instance, you can [find Cloudformation scripts here](https://github.com/jambonz-selfhosting/cloudformation) to deploy jambonz in your AWS account, along with [step-by-step instructions](https://docs.jambonz.org/self-hosting/hosting-providers/aws). We'll be adding additional devops scripts and docs shortly in our public repos to deploy on all of the major hosting providers (Azure, GCP, Exoscale, OVHCloud etc) as well as Kubernetes and Docker Compose.

**We're also introducing free usage for pre-revenue companies and non-commercial use**. If you're a student, a hobbyist, or a startup that hasn't found its footing yet, jambonz will be available to you at no cost.

## For Current Customers

If you're on a support contract today, you can stay on it. We're not forcing anyone to migrate, and we're not raising prices on existing customers. The open source version will continue to receive security and bug fixes through 2026 and beyond.

For those who want access to new features as they land, we'll offer commercial licensing terms that respect your existing relationship with us.

## What does the license look like and how does it work

There are two different types of licenses:

1. The standard license, which you can review [here](https://www.jambonz.org/legal-terms-selfhosted)
2. The OEM license, which you can review [here](https://www.jambonz.org/legal-terms-oem)

Most of our existing customers will be well-served by the standard license; only those who want to redistribute our code as an embedded part of their product would need an OEM license.

Running the commercial version of jambonz under the standard license requires a software license key. The license key is tied to a specific jambonz system or cluster, identified by the unique DNS domain name that you assign when you deploy jambonz. Everyone can get a trial license to start with and, as mentioned above, non-production users can access extended trial licenses.

Licenses can be purchased for a specific capacity, measured by the maximum number of concurrent sessions that jambonz will handle; or for larger capacities a flat monthly fee can be opted for that enables unlimited capacity on a single cluster or system. Details on pricing can be found [here](https://www.jambonz.org/pricing).

Standard licenses are billed as a monthly subscription fee. They can be canceled or modified at any time and unless modified they auto-renew on a monthly billing cycle. Customers with special needs, such as running air-gapped systems can contact us for accommodations.

## Some housekeeping items

- The commercial software versions will be named version 10.x and above.
- The open source software versions (of which the current release is 0.9.5-10) will continue to be named 0.9.x.
- Many of our Github repos used with version 10 will remain public, MIT-licensed, and open for PRs. These include our client sdks, our Node-RED plugin, and various npm libraries.

## Looking Forward

My goal has never changed: to build great software that delivers real value. Open source was the right tactic to get us started. Commercial licensing is the right tactic to let us keep growing—to fund the innovation that keeps jambonz competitive and to build the kind of company I've always wanted to build.

Thank you for being part of this journey. As always, I'm happy to hear your thoughts. You can reach me at daveh@jambonz.org, or ping me on our [community forum](https://community.jambonz.org) if you are with us there.

—Dave
