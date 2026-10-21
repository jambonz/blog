---
title: "SOC 2 Hardening for Self-Hosted Voice AI on Google Cloud: A 2026 Guide"
subtitle: "What changed in the jambonz 11.1.6 Terraform modules for GCP, and why each change matters to an auditor"
date: 2026-10-21
description: "A 2026 guide: jambonz 11.1.6 brings the SOC 2 hardening from our AWS templates to Google Cloud: secrets out of instance metadata, a least-privilege service account, per-role firewall rules, audited Cloud SQL, Redis AUTH and zone redundancy."
author: "Dave Horton"
tags: ["soc2", "security", "compliance", "self-hosting", "gcp", "google-cloud", "terraform", "voice-ai"]
draft: true
faq:
  - question: "Does deploying jambonz on Google Cloud with these Terraform modules make my company SOC 2 compliant?"
    answer: "No. SOC 2 is a report on your organization's controls, and no software can produce it for you. The 11.1.6 GCP modules take care of infrastructure controls an auditor will test on your voice platform, such as secrets handling, least-privilege access, network restrictions and log retention. Your identity and access management, your organization-wide audit logging, your change management and your written policies are still yours."
  - question: "Where does call data live when I self-host jambonz on Google Cloud?"
    answer: "In your own GCP project, in a VPC network you control. Recordings, call records, logs and secrets stay under your IAM policies and your Cloud Audit Logs."
  - question: "Which GCP deployment sizes include the SOC 2 hardening?"
    answer: "All three Terraform modules (mini, medium and large) close SSH by default, keep secrets out of instance metadata, use a least-privilege service account and keep logs in a dedicated Cloud Logging bucket with a retention period. Medium and large also spread every tier across zones and add per-role firewall rules, Cloud SQL connection auditing and Redis authentication."
---

In our last post, [How to build a SOC-2 compliant Voice AI platform on AWS](/blog/soc2-voice-ai-self-hosted-aws), we described what we learned preparing jambonz.cloud for SOC 2, and how jambonz 11.1.6 builds that learning into our AWS CloudFormation templates. We have now done the same work on our [Google Cloud Terraform modules](https://github.com/jambonz-selfhosting/terraform/tree/main/gcp).

This post is the GCP follow-up. It doesn't repeat the background on SOC 2 or the application-level changes in 11.1.6. Those apply on every platform, and the AWS post covers them. Here we focus on what changed in the GCP modules, and why an auditor would care.

## Key Takeaways

- **Convenient defaults are audit findings.** The older modules put secrets in instance metadata, gave the VMs broad Compute Engine permissions and allowed all traffic inside the network. None of that broke anything, which is exactly why it went unnoticed.
- **The 11.1.6 modules close those gaps:** secrets in Secret Manager, a service account that can do almost nothing, firewall rules per server role, an audited and highly available Cloud SQL, Redis authentication, and zone redundancy.
- **Your SOC 2 program is still yours.** The modules harden the voice platform. Identity, organization-wide audit logging, change management and policy remain your work.

## What We Changed, and Why It Matters

### No secrets in instance metadata

The older modules passed the MySQL password, the encryption secret and any API keys to each VM in its startup script, which GCP stores as instance metadata. Anyone in the project with permission to view an instance could read them, and so could any process on the VM through the metadata server. The scripts also ran with `bash -x`, which echoed every command, secrets included, to the serial console and the startup log.

In 11.1.6, on medium and large, every secret lives in Secret Manager. Each VM reads the ones it needs at boot with its service account, which is granted access to each of those secrets by name, and the scripts no longer echo their commands. On mini, the MySQL password and the encryption secret are generated on the VM itself at first boot, so they never leave it. Any apiban or Krisp keys you supply go in Secret Manager only when you set one.

**Why it matters:** secrets handling is a core part of logical access control ([CC6.1](#cc6-1)). A secret readable by anyone who can view a VM, or sitting in a serial console log, is a finding, and a reasonable auditor will ask who could have read it.

### A service account that can do almost nothing

The VMs' service account held `roles/compute.instanceAdmin.v1` on the whole project. With it, a process on any jambonz VM could create, change or delete any VM in the project. The only Compute Engine call jambonz makes is a feature server deleting itself after it drains at scale-in.

In 11.1.6 that is all the service account can do: a custom role with the single permission `compute.instances.delete`, limited by an IAM condition to the deployment's own feature servers. Beyond that, it can read its secrets and write logs and metrics. Mini, which previously had no service account of its own, now gets one with the same limits.

**Why it matters:** an auditor may ask you to show that no system holds more access than it needs ([CC6.3](#cc6-3)). "Delete only my own feature servers" is an easy answer to defend; "administer every VM in the project" is not.

### Firewall rules per server role

The older modules had a rule that allowed all TCP and UDP traffic between every VM in the network. Several internal ports were also open to the internet: the API server's port 3000 on medium; 3000, 9080 (Homer) and 16686 (Jaeger) on large's monitoring server; and 3000, 3010 (Grafana), 9080 and 16686 on mini.

In 11.1.6, on medium and large, each server role has its own firewall rule listing only the ports it serves, and GCP denies everything else. Public access is limited to HTTP/HTTPS and SIP/RTP, and on mini the portal, API and Grafana are all reached through nginx on 80 and 443.

**Why it matters:** an auditor will look at how you restrict access from outside your boundary ([CC6.6](#cc6-6)) and at whether access inside the network follows least privilege ([CC6.1](#cc6-1)). In an attack, a compromised server can't reach ports that are not open to it.

Tightening the rules also taught us something. Once the allow-all rule was gone, our tests showed that the feature servers' media port range in the firewall did not match the range our media server actually uses. The allow-all rule had been hiding the mismatch. If you tighten network rules on any deployment, test calls end to end afterward.

### SSH closed by default

`allowed_ssh_cidr` no longer defaults to `0.0.0.0/0`. It has no default at all: you name your admin IP as a `/32`, or your VPN range, and Terraform checks that it is a valid range before it deploys.

**Why it matters:** limiting administrative access to known sources is one of the first network controls an auditor checks ([CC6.1](#cc6-1), [CC6.6](#cc6-6)).

### A protected, audited database

On medium and large, Cloud SQL now runs with a standby in a second zone and automatic failover, has deletion protection on, keeps 30 backups, and supports point-in-time recovery. The Cloud SQL audit plugin records every connection (logins, logouts and failed logins), and the modules turn on Data Access audit logs for Cloud SQL so those records reach Cloud Logging. Google encrypts the data at rest.

**Why it matters:** this is your evidence for protecting confidential data ([C1.1](#c1-1)), for backup and recovery ([A1.2](#a1-2)), and for monitoring access to the database ([CC7.2](#cc7-2)).

### Redis authentication

Memorystore holds call state for the cluster. It was already reachable only from inside the VPC, but it accepted connections from any VM there without a password. In 11.1.6 on medium and large, Redis requires AUTH, with the password kept in Secret Manager.

**Why it matters:** a password on Redis means a VM in the network can't read or change call state just because it can reach the port ([CC6.1](#cc6-1)).

### Centralized logs with retention

Google's Ops Agent on every VM sends the systemd journal (including SSH logins) and the jambonz application logs to Cloud Logging. A sink routes this deployment's logs (and, on medium and large, the Cloud SQL audit log) into a log bucket of its own, kept for `log_retention_days`: 90 days by default, with 180 and 365 available. Your project's default log bucket and its retention are left alone.

**Why it matters:** retained, centralized logs are what an auditor samples to confirm that you monitor your systems ([CC7.2](#cc7-2)).

### Surviving a zone failure

On medium and large, `zones` (by default the region's first three) spreads the SIP and RTP servers (large) or SBCs (medium) across zones, and runs the feature server and recording instance groups across all of them. Cloud SQL keeps its standby in a second zone, and Memorystore runs on the Standard Tier with a replica in another zone.

**Why it matters:** if your report includes the Availability category, an auditor will look at how you keep the service running and recover it ([A1.2](#a1-2)).

### A bug found by testing

We deployed every module on the 11.1.6 images and ran our release test suite against it. Besides the firewall mismatch above, the testing found an older bug in the large module: with more than one RTP server, every call failed. That is fixed: the SIP servers now find the RTP servers through Redis.

## What These Modules Don't Do (Yet)

We'd rather tell you now than have your auditor find it:

- **Cloud SQL still accepts unencrypted connections.** That traffic stays on a private connection inside your VPC, and we will require TLS once we have confirmed every jambonz component works with it.
- **Redis traffic is not encrypted.** It is password-protected and stays inside your VPC; TLS will follow once every component supports it.
- **Terraform state contains every secret.** Keep it in an encrypted remote backend, with access restricted to the people who run deployments.
- **The web and monitoring servers are single VMs.** They are not zone-redundant.
- **The Ops Agent installs shortly after a new host boots,** so the first moments of that host's logs may be missing from Cloud Logging. This happens before the host takes calls.

## Deploying

Clone the [jambonz Terraform repository](https://github.com/jambonz-selfhosting/terraform), copy the example settings for your size and architecture, and fill in the required values: your project ID and region, an SSH public key, the portal's DNS name and `allowed_ssh_cidr`. The examples already point at the public 11.1.6 images, which are global, for amd64 and arm64.

```bash
cd terraform/gcp/provision-vm-large
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

The highly available defaults add cost: two SIP and two RTP servers (or two SBCs), two feature servers, a Cloud SQL standby and Standard Tier Memorystore. If you are updating an existing deployment, read the [11.1.6 release notes](https://docs.jambonz.org/changelog) first and review `terraform plan` carefully: spreading across zones replaces the VMs and instance groups, and moving Redis to the Standard Tier replaces the Redis instance. Before `terraform destroy`, set `mysql_deletion_protection = false` and apply.

## What Remains Yours

These controls sit at the project, organization or company level, and an auditor will ask about them too:

- **Human access through Cloud Identity or Google Workspace**, with 2-Step Verification, and IAM roles granted to groups rather than individuals.
- **Cloud Audit Logs** routed to a bucket you retain for as long as your policies require, ideally through an organization-level sink.
- **Security Command Center and Organization Policy**, if they are part of your security program; for example, a policy that blocks creating service account keys.
- **Change management:** how updates to the deployment are reviewed and approved.
- **Written policies:** access reviews, incident response, vendor management, backup testing.

## Get Started

jambonz 11.1.6 for Google Cloud is available now. Start with the [GCP self-hosting guide](https://docs.jambonz.org/self-hosting/hosting-providers/gcp), read the [AWS post](/blog/soc2-voice-ai-self-hosted-aws) for the application-level changes in this release, or [contact us](mailto:support@jambonz.org?subject=Questions%20about%20SOC%202%20on%20Google%20Cloud) about running jambonz in your environment.

## SOC 2 Criteria Referenced in This Post

The summaries below are our own wording. The official text is in the AICPA's [2017 Trust Services Criteria (With Revised Points of Focus – 2022)](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022).

- <a id="cc6-1"></a>**CC6.1** (Security): logical access controls, such as restricting and authenticating access and encrypting stored data, protect information assets.
- <a id="cc6-3"></a>**CC6.3** (Security): access to data and systems is granted, changed and removed according to people's roles, following least privilege and separation of duties.
- <a id="cc6-6"></a>**CC6.6** (Security): access controls protect the system from threats that originate outside its boundaries, for example by limiting which external sources can connect.
- <a id="cc7-2"></a>**CC7.2** (Security): system components are monitored for anomalies that could indicate attacks, errors or failures, and those anomalies are analyzed to find security events.
- <a id="a1-2"></a>**A1.2** (Availability): backups, recovery infrastructure and environmental protections are put in place, operated and monitored to meet availability commitments.
- <a id="c1-1"></a>**C1.1** (Confidentiality): confidential information is identified and kept protected to meet confidentiality commitments.
