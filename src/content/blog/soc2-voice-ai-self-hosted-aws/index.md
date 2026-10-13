---
title: "Deploying a Voice AI platform that passes a SOC 2 audit, with jambonz 11.1.6"
date: 2026-10-13
description: "SOC 2 is the price of entry for selling into banking and healthcare. Here's what we learned on our own SOC 2 journey, what we built into jambonz 11.1.6 because of it, and a step-by-step walkthrough of deploying a large jambonz cluster on AWS that's ready for the audit."
author: "Dave Horton"
tags: ["soc2", "security", "compliance", "self-hosting", "aws", "cloudformation", "voice-ai"]
draft: true
faq:
  - question: "Does deploying jambonz with these templates make my company SOC 2 compliant?"
    answer: "No software can do that on its own. SOC 2 is a report on your organization's controls. The 11.1.6 templates take care of the infrastructure controls an auditor will test on your voice platform, such as encryption, least-privilege access, secrets handling and log retention. Your policies, your people's access and your account-wide logging are still yours to put in place."
  - question: "Where does call data live when I self-host jambonz?"
    answer: "In your own AWS account, inside a VPC you control. Call records, recordings, logs and secrets stay under your IAM policies and your audit logs, not in a third party's network."
  - question: "Does jambonz write caller transcripts to its logs?"
    answer: "Not at the default log level. Starting with 11.1.6, caller transcripts and DTMF digits are logged only at debug level, and credentials for listen websockets are never written to the logs."
---

If you sell software into banking, healthcare or insurance, sooner or later a security questionnaire lands on your desk. Near the top of it is one question: *can we see your SOC 2 report?*

For a Voice AI product, that question cuts deeper than it does for most software. Every call your agents handle produces audio, transcripts, phone numbers, and often account details or health information. All of it flows through your voice platform. So the platform you build on becomes part of your audit, whether you planned for that or not.

This post covers three things:

- What SOC 2 is, and why it now matters so much for anyone doing Voice AI in a regulated industry.
- What we learned on our own SOC 2 journey with jambonz.cloud, and what we changed in jambonz 11.1.6 as a result.
- A step-by-step walkthrough of deploying a large jambonz cluster on AWS, showing which choices matter to an auditor and why.

## What SOC 2 is, and why it matters

SOC 2 is an audit framework from the AICPA (the American Institute of Certified Public Accountants). An independent auditor examines your security controls and writes a report saying whether those controls exist and whether they work. The report is organized around five Trust Services Criteria:

- **Security:** systems are protected against unauthorized access. This is the one every SOC 2 report covers.
- **Availability:** systems are up and recoverable as promised.
- **Processing integrity:** systems do what they are supposed to, completely and accurately.
- **Confidentiality:** information marked confidential stays that way.
- **Privacy:** personal information is collected, used and disposed of properly.

There are two kinds of report. A **Type I** report looks at whether your controls are designed properly at a single point in time. A **Type II** report looks at whether they actually operated over a period, usually six to twelve months. Enterprise buyers increasingly ask for Type II.

<!-- EDITOR: consider adding one sourced statistic here on breaches or the cost of a breach in financial services or healthcare. I've left it out rather than invent a number. -->

Why has SOC 2 gone from "nice to have" to "no report, no contract"? Because attacks have become routine, and the costliest ones increasingly come through vendors. A bank can harden its own systems and still be exposed through the contact-center software that records its customers' calls. Vendor-risk teams have learned this the hard way. A SOC 2 report is how they decide whether you are a risk they can take on.

Voice AI raises the stakes. A conversational agent doesn't just route calls. It listens, transcribes, sends what it hears to speech and language models, and often looks up the caller's records partway through a call. That is a lot of sensitive data moving through a lot of systems, and an auditor will want to know where each copy lives and who can reach it.

## Where your customers' data lives

This is the question that should decide which platform you build on.

With a SaaS voice agent platform, your customers' calls, recordings, transcripts and the API keys for your models all live in someone else's network. That vendor may have a SOC 2 report of its own. But their report covers *their* controls; it doesn't bring the data back under yours. If they are breached, you are the one writing to your customers. And when your auditor asks where your call data lives and who can reach it, the honest answer is "a third party we don't control."

A self-hosted platform changes that answer. jambonz runs in your own AWS account, inside a VPC you own, behind your security groups, under your IAM policies, and logging to your CloudWatch. The data never leaves the boundary you already audit. For a bank or a health system, that is often the difference between a short security review and a long one.

Self-hosting by itself isn't enough, though. Developer frameworks such as LiveKit can be self-hosted, but they give you building blocks and leave the hardening to you: secrets handling, IAM roles, database encryption, log retention, network rules. That work is where audits are won or lost. With jambonz 11.1.6, we ship that hardening as part of the product.

## What we learned on our SOC 2 journey

We run jambonz ourselves as a hosted service, jambonz.cloud. Going through SOC 2 readiness on our own infrastructure taught us a few things, and most of them were humbling. Systems that had run reliably for years still had gaps an auditor would flag at once:

- **Secrets in places that are easy to read.** Database passwords and API keys had been written into EC2 user data and application config files. On AWS, anyone with `ec2:DescribeInstanceAttribute` can read user data, and so can any process on the host.
- **IAM roles that were far too broad.** Some servers had broad managed policies attached when they needed two or three specific API calls.
- **Settings that looked right but never took effect.** We had configured a CloudWatch log retention period, but the instance roles lacked permission to apply it, so it never actually applied.
- **Logs that recorded more than they should.** Application logs at the normal level contained what callers said.

Every one of these had the same pattern: a default that was convenient for us made trouble for our customers' auditors. So in 11.1.6 we went through the product and the AWS deployment templates and changed those defaults.

### What changed in jambonz 11.1.6

**In the application:**

- **Caller transcripts and DTMF digits are no longer logged at `info` level.** They appear only at `debug`, which you turn on briefly to troubleshoot, not in normal operation. That keeps what callers say, and the digits they key in (account numbers, PINs, dates of birth), out of your everyday logs.
- **Credentials for [listen](https://docs.jambonz.org/verbs/verbs/listen) websockets are never written to the logs**, at any level.
- **Per-account API rate limits:** limits on call creation, call status reads, sign-in and sign-up, returning `429` when a client exceeds them.
- **Tighter permissions:** service-provider users can no longer change operator-only settings, carrier changes stay within the user's own organization or account, and calls from a registration trunk's address match only carriers that belong to the right account.
- **No default credentials:** new installs generate a random admin API token instead of using a fixed one. The portal's initial password is unique to each deployment, and you must change it the first time you sign in.
- **Encrypted media for encrypted signaling:** SIP clients that register over TLS are offered SRTP, so the audio is encrypted along with the signaling.
- **Control over support audio capture:** accounts and organizations can turn off the capture of call audio for troubleshooting.

**In the AWS CloudFormation templates:**

- **SSH is closed by default.** There is no default source CIDR. You must name your admin IP or VPN range.
- **Every secret lives in AWS Systems Manager Parameter Store** as an encrypted SecureString, and the database password is generated into Secrets Manager. None is written into user data, application config files or systemd units.
- **Least-privilege instance roles:** each server tier gets only the AWS API calls its software actually makes.
- **The instance metadata service requires IMDSv2** on every server, which blocks a common way of stealing instance credentials.
- **The database is encrypted and protected:** Aurora is encrypted at rest, with 30 days of backups, deletion protection, and a final snapshot if the stack is ever deleted. Database logins, logouts and failed logins are logged to CloudWatch.
- **Log retention is enforced:** 90 days by default, with 180 or 365 available.
- **Redis survives an availability-zone failure:** it runs as two nodes in separate zones with automatic failover.
- **TLS everywhere public:** the web tier can sit behind an Application Load Balancer that terminates TLS 1.2 and 1.3, with the certificate issued and renewed by AWS. SIP over TLS and WSS are enabled automatically when you store a certificate in Parameter Store.

## Walkthrough: deploying a large cluster on AWS

Here's the whole process, start to finish, for a **large** deployment. In a large deployment every role (SIP, media, feature servers, web, monitoring, recording) runs on its own servers, and the SIP, media, feature server, web and recording tiers each scale in their own Auto Scaling group. It's the size we recommend for production in regulated environments.

### Step 1: Generate the template for your region

jambonz images are published as public AMIs. A short script copies them into your own AWS account and writes a CloudFormation template for your region. Clone the [jambonz CloudFormation repository](https://github.com/jambonz-selfhosting/cloudformation) and run:

```bash
./generate-cf.sh
```

The script asks for three things: the deployment size (choose **large**), the CPU architecture, and your AWS region. It then copies the AMIs, which takes 5 to 15 minutes, and writes a file such as `jambonz-large-eu-west-3-arm64-v11.1.6.yaml`.

Copying the images into your account is itself a control: the images your servers boot from live in your account and stay there, no matter what happens upstream.

### Step 2: Upload the template

In the AWS console, go to **CloudFormation → Create stack**. Choose **Upload a template file**, and pick the file the script wrote.

![Uploading the generated template in the CloudFormation console](./cf-1.png)

### Step 3: The required parameters

Give the stack a name, then fill in the three values the template requires.

![The stack name and the three required parameters](./cf-2-required.png)

- **EC2 key pair:** the SSH key for reaching the servers.
- **DNS name for the web server:** the hostname for your jambonz portal, for example `voice.example.com`.
- **SSH source CIDR:** the one address range allowed to SSH to any server. Use your admin IP as a `/32`, or your VPN's range. There is no default on purpose.

> **SOC 2:** the SSH CIDR is your logical access control at the network level (criteria CC6.1 and CC6.6). An auditor will look for administrative access limited to known sources. If you enter `0.0.0.0/0` here, you open SSH to the whole internet, and you'll have to explain why.

### Step 4: The web tier

![Choosing the load-balanced web tier](./cf-3-web-tier.png)

Set **Web tier deployment** to `autoscaling-alb`. This runs one to four web servers in an Auto Scaling group behind an Application Load Balancer that terminates TLS.

If your domain is in Route 53, enter its **hosted zone ID**. The stack then issues the TLS certificate through AWS Certificate Manager, validates it, and creates the DNS records for the portal and the API. If your DNS lives elsewhere, leave the zone blank and supply an ACM certificate ARN instead.

The **third-party API keys** below are optional. Leave a key blank if you don't use the service. Any key you do enter is hidden in the console and stored in Parameter Store, not on the servers' disks.

> **SOC 2:** the load balancer enforces TLS 1.2 or higher, with a certificate AWS renews automatically. That covers encryption in transit for the portal and the API (CC6.7), and it removes an expired certificate as a cause of an outage or a finding.

### Step 5: Compute

![Choosing the CPU architecture and instance types](./cf-4-architecture-and-compute.png)

Choose `amd64` or `arm64` (AWS Graviton, lower cost per vCPU) to match the AMIs you copied. Leave the instance types blank to get defaults suited to your architecture and region. There's nothing audit-specific here; size for your call volume.

### Step 6: Database, cache and networking

![Database, cache and VPC settings](./cf-5-database-and-networking.png)

The defaults suit most deployments. Aurora Serverless v2 scales between the minimum and maximum capacity you set here. Notice what you *don't* enter: a database password. The stack generates one and stores it in Secrets Manager, so no person ever has to see it.

The VPC and subnet ranges only matter if this VPC must connect to your existing networks without overlapping.

> **SOC 2:** the database is encrypted at rest, keeps 30 days of backups, can't be deleted by accident, and logs every connection attempt. Those settings are fixed in the template, not offered as parameters, so nobody can turn them off by mistake. They support confidentiality (C1.1), your backup and recovery evidence (A1.2), and monitoring (CC7.2).

### Step 7: Features, logging, monitoring and encryption

![Features, logging and OpenTelemetry settings](./cf-6-features-and-logging.png)

This group holds the settings an auditor will care about most:

- **EnablePcaps:** captures SIP signaling for troubleshooting in the portal's Recent Calls view. SIP messages contain phone numbers, so decide whether you need it. Most teams keep it, because diagnosing call failures without it is slow.
- **Cloudwatch:** keep it `true`. Your application logs go to CloudWatch in your own account.
- **CloudwatchLogRetention:** the default is `90` days, and most SOC 2 auditors expect at least that. Choose `365` if your policies require a full year. The retention is applied when the servers boot.
- **EnableOpenTelemetry:** leave it `false` unless you need distributed tracing. Traces are another copy of call details, and a copy you don't make is one you don't have to protect.
- **EnableEBSEncryption:** below the edge of this screenshot, defaulting to `true`. Keep it. Every disk in the cluster is then encrypted at rest.

> **SOC 2:** retained, centralized logs are the evidence an auditor samples to confirm you monitor your systems (CC7.2). Encrypted disks cover data at rest (CC6.1). Keep in mind that the application logs no longer contain caller transcripts at the default log level. Leave the log level at `info` in production, and turn on debug logging for an account only for as long as a support case needs it.

### Step 8: Tags and permissions

![Adding tags to the stack](./cf-7-tags.png)

Add tags such as `Application=jambonz` and `Environment=production`. CloudFormation applies them to the resources it creates. That gives you an asset inventory you can filter on, which is another thing auditors ask for.

![Acknowledging that the stack creates IAM roles](./cf-8-capabilities.png)

At the bottom of the page, acknowledge that the stack creates IAM resources. These are the least-privilege roles for each server tier. Each grants only the API calls that tier's software makes, such as reading its own parameters from Parameter Store or completing an Auto Scaling lifecycle action. Review them in IAM after the stack is up. An auditor may ask you to show that no server holds broader access than it needs (CC6.3).

Then click **Next**, review, and **Submit**. You can follow progress on the stack's **Events** tab.

<!-- EDITOR: add how long the large stack took to create. I didn't have a timing for it. -->

### Step 9: Outputs and first sign-in

![The stack outputs, including the portal URL and initial password](./cf-8-outputs.png)

When the stack finishes, the **Outputs** tab lists the portal URL, the SBC addresses to give your carriers, and the portal's initial password. That password is the stack's unique ID, so it differs for every deployment. You must change it the first time you sign in.

### After the stack is up

A few steps finish the job:

1. **Sign in and change the admin password.** The portal requires it.
2. **Activate your jambonz license** ([licensing.jambonz.org](https://licensing.jambonz.org)).
3. **Turn on SIP over TLS**, if your carriers or SIP clients support it. Store your certificate in Parameter Store as `TLS_PRIVKEY`, `TLS_CERT` and `TLS_CHAIN` under `/jambonz/<stack>/sbc`. Each SBC enables TLS on port 5061 and WSS on port 8443 when it boots.
4. **Narrow the SIP and RTP source ranges** to your carriers' addresses if you know them. The template's `AllowedSipCidr`, `AllowedRtpCidr` and `AllowedHttpCidr` parameters default to open, because most deployments take calls from many sources.
5. **Restrict who can read `/jambonz/<stack>/` in Parameter Store.** The servers can read their own secrets; your people should need a reason to.

## What's still yours to do

A CloudFormation template can harden a deployment. It can't run your security program. These controls sit at the AWS account or company level, and an auditor will ask about them too:

- **CloudTrail**, with an organization trail writing to a locked-down S3 bucket, so every API call in the account is recorded.
- **Human access through IAM Identity Center** (or your identity provider), with MFA, rather than long-lived IAM users.
- **Change management:** how stack updates are reviewed and approved.
- **Written policies:** access reviews, incident response, vendor management, backup testing.

That list is shorter than it would be if you were also building the voice platform's controls yourself. That's the point.

## Getting started

jambonz 11.1.6 is available now as public AMIs in 30 AWS regions, for both amd64 and arm64, and as Debian packages. Start with the [AWS self-hosting guide](https://docs.jambonz.org/self-hosting/hosting-providers/aws), or [talk to us](https://jambonz.org) about running jambonz in your environment. If you're preparing for an audit of your own, we're happy to compare notes.
