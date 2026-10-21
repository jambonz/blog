---
title: "SOC 2 Hardening for Self-Hosted Voice AI on Azure"
subtitle: "What changed in the jambonz 11.1.6 Terraform modules for Azure, and why each change matters to an auditor"
date: 2026-10-21
description: "jambonz 11.1.6 brings the SOC 2 hardening from our AWS templates to Azure: no secrets in custom data, least-privilege identities, per-role network rules, private Redis, audited MySQL and zone redundancy."
author: "Dave Horton"
tags: ["soc2", "security", "compliance", "self-hosting", "azure", "terraform", "voice-ai"]
draft: true
faq:
  - question: "Does deploying jambonz on Azure with these Terraform modules make my company SOC 2 compliant?"
    answer: "No. SOC 2 is a report on your organization's controls, and no software can produce it for you. The 11.1.6 Azure modules take care of infrastructure controls an auditor will test on your voice platform, such as secrets handling, least-privilege access, network restrictions and log retention. Your identity and access management, your subscription-wide logging, your change management and your written policies are still yours."
  - question: "Where does call data live when I self-host jambonz on Azure?"
    answer: "In your own Azure subscription, in a resource group and virtual network you control. Recordings, call records, logs and secrets stay under your Entra ID access policies and your Azure Activity Log."
  - question: "Which Azure deployment sizes include the SOC 2 hardening?"
    answer: "All three Terraform modules (mini, medium and large) close SSH by default, keep secrets out of custom data and send logs to Log Analytics with a retention period. Medium and large also spread every tier across availability zones and add per-role network security groups, a private Redis endpoint and MySQL connection auditing."
---

In our last post, [How to build a SOC-2 compliant Voice AI platform on AWS](/blog/soc2-voice-ai-self-hosted-aws), we described what we learned preparing jambonz.cloud for SOC 2, and how jambonz 11.1.6 builds that learning into our AWS CloudFormation templates. Many of our self-hosted customers run on Azure, so we have now done the same work on our [Azure Terraform modules](https://github.com/jambonz-selfhosting/terraform/tree/main/azure).

This post is the Azure follow-up. It doesn't repeat the background on SOC 2 or the application-level changes in 11.1.6. Those apply on every platform, and the AWS post covers them. Here we focus on what changed in the Azure modules, and why an auditor would care.

## Key Takeaways

- **Azure's defaults needed hardening.** Two Azure behaviors in particular undercut the old modules: network security groups allow all traffic inside a virtual network unless you deny it, and a VM's custom data is readable by anyone who can read its configuration.
- **The 11.1.6 modules fix both, and more:** secrets in Key Vault, managed identities that can only read secrets, a network security group per server role, private Redis, MySQL connection auditing, and zone redundancy.
- **Your SOC 2 program is still yours.** The modules harden the voice platform. Identity, subscription-wide logging, change management and policy remain your work.

## What We Changed, and Why It Matters

### Network rules that actually restrict traffic

Azure network security groups (NSGs) carry a built-in rule, `AllowVnetInBound`, that allows all traffic between resources in the same virtual network. Our older modules had rules that looked restrictive, but with that default in place, every VM could reach every port on every other VM. Several internal ports, including the API server's port 3000, were also open to the internet.

In 11.1.6, on medium and large, each server role has its own NSG. It lists only the ports that role serves and ends with an explicit rule that denies all other traffic from inside the virtual network. Internal ports are no longer reachable from the internet. On mini, port 3000 and Homer (9080) are closed.

**Why it matters:** an auditor will look at how you restrict access to your systems from outside your boundary ([CC6.6](#cc6-6)), and at whether access inside the network follows least privilege ([CC6.1](#cc6-1)). A rule that the platform silently overrides is hard to defend in an audit, and in an attack a compromised server can't reach ports that are not open to it.

### SSH closed by default

`allowed_ssh_cidr` no longer defaults to `0.0.0.0/0`. It has no default at all: you name your admin IP as a `/32`, or your VPN range.

**Why it matters:** limiting administrative access to known sources is one of the first network controls an auditor checks ([CC6.1](#cc6-1), [CC6.6](#cc6-6)).

### No secrets in custom data

The older modules passed the MySQL password, the Redis key, the encryption secret and any API keys to each VM in its `custom_data`. Anyone with read access to the VM's configuration in Azure could read them, as could any process on the VM through the instance metadata service. The setup scripts also ran with `bash -x`, which echoed every command, secrets included, into the setup log on disk.

In 11.1.6 the secrets live in Azure Key Vault. Each VM reads the ones it needs at boot with its managed identity, and the setup scripts no longer echo their commands. On mini, the MySQL password and the encryption secret are generated on the VM itself at first boot, so they never leave it. Any apiban or Krisp keys you supply go in a Key Vault that is created only when you set one.

**Why it matters:** secrets handling is a core part of logical access control ([CC6.1](#cc6-1)). A secret that sits in plain text in a VM's configuration or a log file is a finding, and a reasonable auditor will ask who could have read it.

### Least-privilege identities

The managed identity used by the VMs held the Network Contributor and Virtual Machine Contributor roles, and nothing in jambonz used them. A process on any VM could have used that identity to change the network or other VMs. In 11.1.6 the identity can read the deployment's secrets by name, and nothing else.

**Why it matters:** an auditor may ask you to show that no system holds more access than it needs ([CC6.3](#cc6-3)).

### Private Redis

Redis holds call state for the cluster, and in the older modules it was reachable from the public internet, protected only by its access key. In 11.1.6 on medium and large, public network access is disabled, and the virtual network reaches Redis through a private endpoint, over TLS.

**Why it matters:** this narrows your system boundary ([CC6.6](#cc6-6)) and protects data in transit ([CC6.7](#cc6-7)).

### A protected, audited database

On medium and large, MySQL (Azure Database for MySQL Flexible Server) is encrypted at rest, keeps 30 days of backups, logs every connection (logins, logouts and failed logins) to Log Analytics, and carries a `CanNotDelete` lock, so it can't be deleted by accident.

**Why it matters:** this is your evidence for protecting confidential data ([C1.1](#c1-1)), for backup and recovery ([A1.2](#a1-2)), and for monitoring access to the database ([CC7.2](#cc7-2)).

### Centralized logs with retention

A Log Analytics workspace keeps the system logs (including SSH logins) and the jambonz application logs from every VM and scale set for `log_retention_days`: 90 days by default, with 180 and 365 available. The Azure Monitor Agent on each VM collects them.

**Why it matters:** retained, centralized logs are what an auditor samples to confirm that you monitor your systems ([CC7.2](#cc7-2)).

### Surviving a zone failure

On medium and large, `zones` (by default `["1","2","3"]`) spreads the SIP and RTP servers (large) or SBCs (medium) across availability zones and balances the feature server and recording scale sets across them. The public IPs and the recording load balancer are zone-redundant, MySQL keeps a standby in a second zone with automatic failover, and Redis keeps a replica in another zone.

**Why it matters:** if your report includes the Availability category, an auditor will look at how you keep the service running and recover it ([A1.2](#a1-2)).

### Bugs found by testing

We deployed every module on the 11.1.6 images and ran our release test suite against it. That testing found two older bugs in the large module, both now fixed: the recording servers had no outbound internet access, so recordings couldn't be uploaded, and with more than one RTP server, every call failed.

## What These Modules Don't Do (Yet)

We'd rather tell you now than have your auditor find it:

- **MySQL still accepts unencrypted connections.** That traffic stays on a private, delegated subnet, and we will require TLS once we have confirmed every jambonz component works with it.
- **Terraform state contains every secret.** Keep it in an encrypted remote backend, with access restricted to the people who run deployments.
- **The web and monitoring servers are single VMs.** They are not zone-redundant.
- **A new host's first minute of logs is not collected.** The Azure Monitor Agent installs while the jambonz apps start, so expect about a minute's gap in Log Analytics for each new host. This happens before the host takes calls.

## Deploying

Clone the [jambonz Terraform repository](https://github.com/jambonz-selfhosting/terraform), copy the example settings for your size and architecture, and fill in the required values: your subscription and tenant IDs, an SSH public key, the portal's DNS name and `allowed_ssh_cidr`.

```bash
cd terraform/azure/provision-vm-large
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

The images are published in an Azure community gallery in 30 regions (amd64) and 29 regions (arm64). Note that the zone-redundant defaults add cost: two SIP and two RTP servers (or two SBCs), two feature servers, and a General Purpose MySQL SKU, because zone-redundant MySQL doesn't support Burstable SKUs. If you are updating an existing deployment, read the [11.1.6 release notes](https://docs.jambonz.org/changelog) first: moving to availability zones replaces the public IPs, so **the SBC addresses your carriers allow-list will change**.

## What Remains Yours

These controls sit at the subscription or company level, and an auditor will ask about them too:

- **Human access through Entra ID**, with MFA, and ideally Privileged Identity Management for administrative roles.
- **The Azure Activity Log**, exported to a workspace or storage account you retain, so every change in the subscription is recorded.
- **Microsoft Defender for Cloud and Azure Policy**, if they are part of your security program.
- **Change management:** how updates to the deployment are reviewed and approved.
- **Written policies:** access reviews, incident response, vendor management, backup testing.

## Get Started

jambonz 11.1.6 for Azure is available now. Start with the [Azure self-hosting guide](https://docs.jambonz.org/self-hosting/hosting-providers/azure), read the [AWS post](/blog/soc2-voice-ai-self-hosted-aws) for the application-level changes in this release, or [contact us](mailto:support@jambonz.org?subject=Questions%20about%20SOC%202%20on%20Azure) about running jambonz in your environment.

## SOC 2 Criteria Referenced in This Post

The summaries below are our own wording. The official text is in the AICPA's [2017 Trust Services Criteria (With Revised Points of Focus – 2022)](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022).

- <a id="cc6-1"></a>**CC6.1** (Security): logical access controls, such as restricting and authenticating access and encrypting stored data, protect information assets.
- <a id="cc6-3"></a>**CC6.3** (Security): access to data and systems is granted, changed and removed according to people's roles, following least privilege and separation of duties.
- <a id="cc6-6"></a>**CC6.6** (Security): access controls protect the system from threats that originate outside its boundaries, for example by limiting which external sources can connect.
- <a id="cc6-7"></a>**CC6.7** (Security): moving and transmitting information is limited to authorized users and processes, and information is protected in transit.
- <a id="cc7-2"></a>**CC7.2** (Security): system components are monitored for anomalies that could indicate attacks, errors or failures, and those anomalies are analyzed to find security events.
- <a id="a1-2"></a>**A1.2** (Availability): backups, recovery infrastructure and environmental protections are put in place, operated and monitored to meet availability commitments.
- <a id="c1-1"></a>**C1.1** (Confidentiality): confidential information is identified and kept protected to meet confidentiality commitments.
