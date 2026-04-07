# Microsoft Azure — Pricing & Account Options
# Source: azure.microsoft.com/en-in/pricing/purchase-options/azure-account/search/ (India SEM landing page)
# + azure.microsoft.com/en-us/pricing | Azure Free Account FAQ | March 2026
# ⚠️ Azure pricing pages block direct fetch (robots.txt). Data via official Microsoft docs + search index.

---

## Azure Account Types — Overview

| Account Type | Best For | Cost | Credit | Free Services |
|---|---|---|---|---|
| **Azure Free Account** | New users exploring Azure | $0 upfront | $200 for 30 days | 55+ always-free + popular 12-month free |
| **Pay-As-You-Go (PAYG)** | Flexible, no commitment | Pay per use | None | 55+ always-free monthly amounts |
| **Azure for Students** | Students w/ academic email | $0 | $100 (no credit card needed) | 65+ free always + 12-month popular |
| **Microsoft for Startups** | Eligible startups | $0 | Up to $150,000 | — |
| **Visual Studio Subscribers** | Developers w/ VS subscription | Subscription | $50–$150/month | — |
| **Enterprise Agreement (EA)** | Large enterprises (500+ seats) | Volume pricing | Negotiated | Negotiated |
| **Microsoft Customer Agreement** | Modern direct purchase | PAYG or committed | — | 55+ always-free |
| **Cloud Solution Provider (CSP)** | Buying through partners | Partner pricing | — | — |

---

## Azure Free Account — Full Detail

### What You Get
| Benefit | Duration | Detail |
|---|---|---|
| **$200 credit** | First 30 days | Spend on any Azure service |
| **Popular services free** | 12 months | Selected compute, storage, DB, AI |
| **55+ services always free** | Indefinite | Within monthly quota limits |
| Access to all Azure services | Immediate | No production blocking |

### ⚠️ India-Specific Restriction
> **12 months of popular services free is NOT available to customers who sign up directly for Pay-As-You-Go in China or India.**

**What this means for India:**
- Indian customers CAN still get the $200/30-day credit via the Free Account path
- Indian customers CAN access the 55+ always-free services
- The 12-month free tier on popular services (VMs, SQL DB, Blob Storage) is **not available** when signing up directly for PAYG in India
- Workaround: Sign up for the full **Azure Free Account** (not direct PAYG) to get the 12-month free services
- Students in India: Use **Azure for Students** ($100 credit, no card, academic email) — this IS available

### Free Account Sign-Up Requirements
- Phone number (identity verification)
- Credit card or debit card (non-prepaid) — for identity only, not charged
- Microsoft account OR GitHub account
- Note: Only credit cards accepted in Hong Kong and Brazil

### Free Account Flow
```
Create Free Account → $200 credit (30 days) → 
    ↓ Use credit or 30 days expires
    ↓ Decision point: Move to Pay-As-You-Go?
YES → Continue with 12-month popular free services + 55+ always-free
NO  → Account disabled
```

---

## 12-Month Free Popular Services (New Customers Only)

| Service | Free Tier | Notes |
|---|---|---|
| **Virtual Machines** | 750 hrs/mo of B1s, B2pts v2 (ARM), B2ats v2 (AMD) | Mix across VMs = 750 hrs total |
| **SQL Database** | 250 GB | S0 service tier |
| **Blob Storage** | 5 GB LRS hot block | 20K read + 10K write ops |
| **Azure Cosmos DB** | 1,000 RU/s + 25 GB | Provisioned throughput |
| **App Service** | 10 apps (1 GB storage each) | Web/mobile/API |
| **Azure Functions** | 1M requests + 400K GB-s | Serverless |
| **Azure Container Registry** | 1 basic registry | |
| **Azure AI Services** | 5,000 transactions/mo | Text Analytics, Speech, Translator |
| **Azure Kubernetes Service** | Free cluster management | Pay for nodes only |
| **Azure DevOps** | 5 users free | Basic plan |
| **Bandwidth (outbound)** | 15 GB/mo | Data egress |

---

## 55+ Always-Free Services (Permanent, No Expiry)

Selected key always-free services (up to monthly limits):

| Service | Always-Free Limit |
|---|---|
| Azure Functions | 1M executions + 400K GB-s/mo |
| Azure App Service | 10 apps (shared compute) |
| Azure Cosmos DB | 1,000 RU/s + 25 GB |
| Azure DevOps | 5 users (Basic plan) |
| Azure Pipelines | 1,800 mins/mo (hosted) |
| Azure Repos | Unlimited private repos (5 users) |
| Azure Artifacts | 2 GB storage |
| Azure Boards | Unlimited |
| GitHub Actions | 2,000 mins/mo (free tier) |
| Azure IoT Hub | 8,000 msg/day (F1 tier) |
| Azure Event Grid | 100K ops/mo |
| Azure Logic Apps | 4,000 built-in actions/mo |
| Azure Notification Hubs | 1M pushes/mo (free tier) |
| Cognitive Services (limited) | Free tier per service |
| Azure API Management | Developer tier (no SLA) |
| Microsoft Entra ID (formerly AAD) | 50,000 MAU free (external identities) |
| Azure Arc | Free control plane (external resources) |
| AKS cluster management | Free (pay nodes only) |

---

## Pay-As-You-Go (PAYG) — Core Model

### How It Works
- Billed **per second** for most compute services
- No upfront commitment, no early termination fees
- List price (highest price tier — no discounts)
- Credit card on file billed monthly
- Access to 55+ always-free services within limits
- ⚠️ In India: No 12-month free popular services when signing up directly as PAYG

### PAYG Sample Prices (East US, March 2026 indicative)
| Resource | PAYG Rate |
|---|---|
| B1s VM (1 vCPU, 1 GB RAM) — Linux | ~$7.59/mo |
| B2s VM (2 vCPU, 4 GB RAM) — Linux | ~$35.04/mo |
| D4s_v3 VM (4 vCPU, 16 GB RAM) — Windows | ~$140.16/mo |
| Standard SSD E10 (128 GB) | ~$9.60/mo |
| Azure SQL DB (S0 — 10 DTU) | ~$15/mo |
| Azure OpenAI GPT-4o (1K input tokens) | ~$0.005 |
| Azure Blob Storage (LRS hot, per GB) | ~$0.018/mo |
| Outbound bandwidth (per GB, first 5 GB free) | ~$0.087/GB |

---

## Azure Pricing Models — Cost Optimization Stack

### 1. Pay-As-You-Go (PAYG) — Baseline
- No commitment, max flexibility
- Highest per-unit rate
- Good for: variable/unpredictable workloads, dev/test

### 2. Azure Savings Plan for Compute
- Commit to **hourly spend** for 1 or 3 years
- Applies across: VMs, App Service, Container Instances, Azure Functions (Premium), Azure Dedicated Host
- Savings: **up to 65%** vs PAYG
- Flexible: Works across VM sizes, regions, OS types
- Cannot be cancelled or exchanged for reservations
- Best for: dynamic workloads, organisations scaling or changing instance types

### 3. Azure Reserved VM Instances (RIs)
- Commit to **specific VM type + region** for 1 or 3 years
- Savings: **up to 72%** vs PAYG
- 3-year RI example: Standard_D4s_v3 Windows from $140.16/mo → $39.24/mo = 72% off
- Can be combined with Azure Hybrid Benefit → **up to 86% savings**
- Instance size flexibility available in some VM families
- Can exchange or cancel (up to $50K/rolling 12 months)
- Best for: stable, always-on production workloads (DBs, domain controllers, web servers)
- EA customers: uses Azure prepayment/credit first

### 4. Azure Spot VMs
- Use Azure's **unused capacity** at up to **90% discount** vs PAYG
- Trade-off: can be evicted with **30 seconds' notice**
- Bidding model: set max price, Azure terminates if capacity needed
- Best for: batch jobs, CI/CD pipelines, dev/test, rendering, HPC
- NOT for: production databases, domain controllers, critical services

### 5. Azure Hybrid Benefit (AHB)
- Apply **existing on-prem licenses** to Azure
- Eligible: Windows Server + SQL Server (with Software Assurance), RHEL/SLES subscriptions
- Savings: up to **85%** when combined with RIs and Extended Security Updates
- SQL Server Enterprise on VM: from ~$139/mo → ~$19/mo (example)
- Best for: customers with existing Microsoft EA + Software Assurance

### Combined Savings Example
```
Standard_D4s_v3 Windows VM, East US:
- PAYG:                     $140.16/mo  (baseline)
- 3-year RI only:           $39.24/mo   (72% off)
- 3-year RI + AHB:         $19.62/mo   (86% off)
```

### 6. Azure Reservations (Beyond VMs)
Available for many services beyond VMs:

| Service | Max Savings |
|---|---|
| Azure SQL Database | Up to 72% (1 or 3 year) |
| Azure Cosmos DB | Up to 65% |
| Azure Synapse Analytics | Up to 65% |
| Azure Blob Storage | Up to 38% |
| Azure Files | Up to 38% |
| Azure OpenAI GPT-4o (provisioned) | 70% off (1-year reservation at ~$0.3027/hr vs ~$1/hr PAYG) |
| Azure Fabric Capacity Units | 40.5% (1-year) |
| Azure Dedicated Host | Up to 72% |
| RedHat / SUSE software plans | Available |

---

## Purchase Channels

| Channel | Who It's For | Pricing | Notes |
|---|---|---|---|
| **Azure.com (web direct)** | Individuals, SMBs | List PAYG | Credit card; easiest onboarding |
| **Enterprise Agreement (EA)** | 500+ seat orgs | Negotiated volume discounts, 3-year | Centralised billing; Azure Prepayment |
| **Microsoft Customer Agreement (MCA)** | Modern direct/enterprise | PAYG or committed | Replaces EA for new modern customers |
| **Cloud Solution Provider (CSP)** | Via Microsoft partners | Partner-set pricing | Partner handles billing, support |
| **Azure Marketplace** | ISV products | Varies | Billed through Azure subscription |
| **ISV Success Program** | Startups building on Azure | Free credits + consulting | Up to 1:1 technical consultation |

---

## Azure for India — Key Context

### India Azure Regions
| Region Name | Location |
|---|---|
| Central India | Pune |
| South India | Chennai |
| West India | Mumbai |
| Jio India West | Jamnagar |
| Jio India Central | Nagpur |

**India data residency:** All 5 India regions support data residency for regulated workloads (BFSI, healthcare, government).

### Azure India Pricing Notes
- Prices displayed in INR (Indian Rupee) for India customers under Microsoft Customer Agreement
- Currency: First calculated in USD, converted at London closing spot rate (2 business days prior to month-end)
- Tax (GST): Applicable at 18% on Azure services for Indian customers
- Azure Marketplace products may be priced in USD or local currency (non-Microsoft products always USD)

### India-Specific Programs
- **Microsoft for Startups (India):** Active program with Indian startup ecosystem; up to $150K in Azure credits
- **Azure Dev Tools for Teaching:** Available for Indian universities via Academic email
- **Digital India Partnership:** Azure listed as preferred cloud for Digital India initiative
- **Azure Stack Hub:** Available for air-gapped/sovereign deployments (government, defence)

---

## Azure Cost Management Tools

| Tool | What It Does |
|---|---|
| **Azure Pricing Calculator** | Estimate monthly cost for any combination of services |
| **Azure Cost Management + Billing** | Track actual spend, set budgets, alerts |
| **Azure Advisor** | Personalised cost + performance recommendations (rightsizing, RI suggestions) |
| **Azure Migrate** | Estimate cost of moving on-prem workloads to Azure |
| **Total Cost of Ownership (TCO) Calculator** | Compare on-prem vs Azure costs |
| **Microsoft Cost Management (MCM)** | Available free for all Azure subscriptions |

### Cost Optimization Quick Wins
1. Use **Reserved Instances** for any VM running 24/7
2. Enable **Azure Hybrid Benefit** if you have SA licenses
3. Use **Spot VMs** for all dev/test environments → typical 60-80% savings
4. **Auto-shutdown** non-production VMs outside business hours
5. **Right-size** VMs using Azure Advisor (oversized VMs are #1 cost waste)
6. Use **Azure Savings Plans** for flexible compute commitment
7. Prefer **cheaper regions** for non-latency-sensitive workloads (East US ~20-40% cheaper than premium regions)
8. **Tag all resources** to track spend by team/project/environment
9. Review **outbound data transfer** — this is often a surprise cost
10. Use **Azure Reservations for OpenAI** — 70% off provisioned throughput

---

## SEM Landing Page Context (The URL Provided)

The URL provided was:
`azure.microsoft.com/en-in/pricing/purchase-options/azure-account/search/`

With UTM/GCLID parameters indicating:
- **Campaign:** `gad_campaignid=23650569745` → Google Ads campaign
- **Source:** `gad_source=1` → Google Ads (paid search)
- **Region:** `en-in` → India market
- **OCID:** `AIDcmmf1elj9v5_SEM` → Microsoft's internal SEM tracking code
- **GCLID:** Google Click Identifier → conversion tracking for Google Ads

**What this means:** Microsoft is actively running paid search campaigns in India for Azure account acquisition. The landing page is the Azure Free Account / PAYG purchase decision page, targeted at Indian cloud customers searching for Azure pricing.

**Key message on that page:** "Pay as you go or try Azure free for up to 30 days. No upfront commitment — cancel anytime."

---

## Azure OpenAI Specific Pricing (Popular for India AI workloads)

| Model | Input (per 1K tokens) | Output (per 1K tokens) | Notes |
|---|---|---|---|
| GPT-4o | $0.0025 | $0.010 | Standard global |
| GPT-4o mini | $0.000150 | $0.000600 | Most cost-efficient |
| GPT-4 Turbo | $0.010 | $0.030 | Legacy |
| GPT-3.5 Turbo | $0.0005 | $0.0015 | Budget option |
| o1 (reasoning) | $0.015 | $0.060 | Premium |
| o3-mini | $0.0011 | $0.0044 | Efficient reasoning |
| text-embedding-3-large | $0.000130/1K | — | Embeddings |
| DALL-E 3 (1024×1024) | $0.040/image | — | |
| Whisper (speech-to-text) | $0.006/minute | — | |

**Azure OpenAI Reservation (1-year):** GPT-4o provisioned: ~$0.3027/hr vs ~$1/hr PAYG = **70% savings** for consistent throughput workloads.

---

## MSFT-X: When to Load This File

Load `references/azure-pricing.md` for:
- Azure Free Account details ($200 credit, 30-day trial, 55+ always-free)
- ⚠️ India restriction: 12-month free popular services not available for direct PAYG India sign-ups
- All Azure pricing models: PAYG, Savings Plan, Reserved Instances, Spot VMs, Hybrid Benefit
- Savings percentages: up to 72% (RI), 65% (Savings Plan), 90% (Spot), 85% (RI+AHB)
- Azure India regions (5 regions: Pune, Chennai, Mumbai, Jamnagar, Nagpur)
- INR pricing + GST context for Indian customers
- Azure cost management tools (Pricing Calculator, Advisor, TCO, Cost Management)
- Azure OpenAI pricing and reservation discounts
- Purchase channels: web direct, EA, MCA, CSP
- SEM/Google Ads landing page context for India Azure campaigns
