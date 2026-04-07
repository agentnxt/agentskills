# Microsoft Azure — Cloud Platform Deep Reference
# Sources: Wikipedia/Microsoft Azure | azurecharts.com/overview | azure.microsoft.com blogs
# + Synergy Research Group Q3 2025 | Omdia | Canalys | March 2026

---

## What Is Azure

**Microsoft Azure** (formerly Windows Azure) is Microsoft's cloud computing platform.
- **Launched:** October 27, 2008 (announced as "Project Red Dog" at PDC 2008)
- **General Availability:** February 1, 2010 (as Windows Azure)
- **Renamed:** March 25, 2014 → Microsoft Azure
- **Services:** 600+ cloud services
- **SLA:** 99.9% availability guarantee (service-specific terms apply)
- **License:** Proprietary platform; client SDKs = MIT License
- **Website:** azure.microsoft.com
- **Mobile apps:** iOS 8.1.0 (Jan 2026), Android 7.11.0 (Dec 2025)

---

## Azure by the Numbers (FY2025 / Q3 2025)

| Metric | Value |
|---|---|
| **Annual Revenue** | **$75+ billion** (FY2025, first time exceeding $75B) |
| **Revenue Growth** | **+34–40% YoY** (FY2025 — among fastest of any hyperscaler) |
| **Global Market Share** | **~20–22%** of global cloud infrastructure |
| **Datacenters** | **400+** datacenters globally |
| **Regions** | **70+ announced regions** (more than any other cloud provider) |
| **Services** | **600+** cloud services |
| **AI Foundry Customers** | **80,000+** |
| **AI Models Available** | **11,000+** (Azure AI Foundry model catalog) |
| **Copilot queries/day** | Approaching **1 billion** |
| **CapEx FY2025** | **$80 billion** (largest annual investment in Microsoft history) |
| **% of Microsoft Revenue** | ~27% of total Microsoft revenue |
| **Intelligent Cloud segment** | $29.9B quarterly revenue (Q4 FY2025) |

---

## Azure vs AWS vs Google Cloud — Competitive Position

### Market Share (Q3 2025, Synergy Research Group / Canalys)

| Provider | Market Share | Q3 2025 Revenue | YoY Growth |
|---|---|---|---|
| **AWS** | **32%** | $30.6B | +17–20% |
| **Microsoft Azure** | **22%** | $22.9B | **+39–40%** ← fastest growth |
| **Google Cloud** | **12–13%** | $12.5B | +30–32% |
| **Big 3 combined** | **~65%** | $66B+ | — |
| Global market Q2 2025 | — | **$99B** | +25% YoY |

**Full-year 2025 cloud market:** First time exceeding **$400 billion**.

### Azure's Competitive Advantages
1. **Enterprise ecosystem lock-in** — M365, Teams, Windows, Active Directory/Entra, Dynamics 365 all funnel into Azure
2. **OpenAI exclusive partnership** — Azure is the exclusive cloud provider for OpenAI workloads (extended through 2032, $250B compute commitment)
3. **Hybrid cloud dominance** — Azure Arc, Azure Local, Azure Stack Hub: no hyperscaler matches Microsoft's hybrid footprint
4. **AI momentum** — Azure's 39% growth in FY2025 vs AWS's 17% = Azure gaining ground fastest
5. **Government** — FedRAMP authorized; Azure Government; classified clouds (Secret/Top Secret)
6. **GPT-4o series natively integrated** — across the entire Azure portfolio

### Azure's Challenges
- AWS still commands 10pp more market share
- Google Cloud growing fast with TPU AI advantage
- Azure data center capacity constraints in Northern Virginia and Texas (expected through mid-2026)
- ~2 GW of leases canceled/deferred in 2025 (portfolio optimization, not retreat)

---

## Complete Azure Service Catalog (by Category)

Source: azurecharts.com/overview — all GA services as of March 2026

### 🤖 AI + Machine Learning
| Service | Description |
|---|---|
| **Azure AI Foundry** (formerly Azure AI Studio) | Build/deploy generative AI apps; 11,000+ models; Prompt flow; Fine-tuning |
| **Azure OpenAI Service** | GPT-4o, GPT-4 Turbo, o1, o3-mini, DALL-E, Whisper via Azure |
| **Azure AI Services** | Pre-built APIs: Speech, Vision, Language, Translator, Document Intelligence, Content Safety, Face API |
| **Azure AI Search** (formerly Cognitive Search) | Vector + hybrid search; RAG pattern backbone |
| **Azure Machine Learning** | MLOps platform; AutoML; Responsible AI dashboard; Managed endpoints |
| **AI Bot Service** | Build conversational bots; integrates with Copilot Studio |
| **Open Datasets** | Curated public datasets for ML training |
| **Planetary Computer** | Geospatial AI; satellite + earth observation data platform |
| **Azure Quantum** | Quantum hardware access (trapped ion, neutral atom, superconducting); Q# language; QDK |
| **Copilot in Azure** | AI assistant embedded in Azure portal (management + troubleshooting) |

### 📊 Analytics
| Service | Description |
|---|---|
| **Microsoft Fabric** | Unified analytics platform (OneLake, Spark, Notebooks, Real-Time Intelligence, Power BI) |
| **Azure Synapse Analytics** | Fully managed cloud data warehouse + analytics |
| **Power BI Embedded** | Embed Power BI dashboards into applications |
| **Azure Data Factory** | Data integration; ETL/ELT pipelines; 90+ connectors |
| **Azure Data Explorer** (Kusto) | Big data analytics; time-series; log analytics |
| **Azure Databricks** | Managed Apache Spark analytics platform |
| **Event Hubs** | Fully managed real-time data ingestion; Kafka-compatible |
| **Stream Analytics** | Serverless real-time stream processing |
| **HDInsight** | Managed Hadoop/Spark/Kafka/HBase clusters |
| **Analysis Services** | Enterprise-grade semantic data models (tabular) |
| **Graph Data Connect** | Bulk extract Microsoft Graph data into Azure for analytics |
| **Azure Purview** | Unified data governance; data catalog; data map |

### ⚙️ Compute
| Service | Description |
|---|---|
| **Virtual Machines (VMs)** | IaaS VMs — Windows, Linux, ARM (Ampere); 800+ VM sizes |
| **VM Scale Sets** | Autoscale groups of identical VMs |
| **Azure Kubernetes Service (AKS)** | Managed Kubernetes; free cluster management; pay for nodes |
| **Azure Functions** | Serverless FaaS; event-driven; 1M executions/mo free |
| **App Service** | PaaS for web apps; ASP.NET, Java, Node.js, PHP, Python, Ruby |
| **Container Apps** | Serverless container platform; built on Kubernetes + KEDA |
| **Container Instances** | Run containers without managing infrastructure (fastest startup) |
| **Container Registry** | Private Docker/OCI registry |
| **Azure Batch** | HPC job scheduling at scale |
| **Azure Red Hat OpenShift** | Managed OpenShift on Azure |
| **Service Fabric** | Microservices platform (stateful/stateless); .NET native |
| **Virtual Desktop (AVD)** | Azure Virtual Desktop; cloud-hosted Windows 10/11 |
| **Cloud Services (classic)** | Legacy PaaS (being deprecated) |
| **CycleCloud** | HPC cluster management; Slurm/PBS/Grid Engine |
| **Dedicated Host** | Single-tenant physical servers for VMs |
| **Compute Fleet** | Manage fleets of VMs across types and pricing models |
| **Azure VMware Solution** | Run VMware workloads natively on Azure |
| **Azure Spring Apps** | Managed Spring Boot/Steeltoe platform |

### 🗄️ Databases
| Service | Description |
|---|---|
| **Azure SQL Database** | Fully managed SQL Server; hyperscale option; serverless tier |
| **Azure SQL Managed Instance** | Full SQL Server compatibility; managed; no code changes |
| **Azure Cosmos DB** | Multi-model NoSQL; 5 APIs (Core SQL, MongoDB, Cassandra, Gremlin, Table); global distribution |
| **Azure Database for PostgreSQL** | Fully managed PostgreSQL; Flexible Server; Citus hyperscale |
| **Azure Database for MySQL** | Fully managed MySQL; Flexible Server |
| **Apache Cassandra Managed Instance** | Fully managed Cassandra |
| **Redis Cache** | Managed Redis; OSS + Enterprise tiers |
| **Managed Redis** | New generation managed Redis (2025) |
| **HorizonDB** | Newer managed DB offering |

### 👨‍💻 Development
| Service | Description |
|---|---|
| **Azure DevOps** | Boards, Repos, Pipelines, Test Plans, Artifacts |
| **GitHub** (Microsoft-owned) | 180M+ developers; Copilot; Actions; Advanced Security |
| **App Configuration** | Centralized feature flags + config management |
| **Azure Chaos Studio** | Fault injection for resilience engineering |
| **Deployment Environments** | Self-service dev environments with templates |
| **DevTest Labs** | Cost-controlled dev/test environments |
| **Lab Services** | Cloud-based labs for education/training |
| **Microsoft Dev Box** | Cloud developer workstations (Windows 365 for devs) |
| **App Testing** | Mobile and web app testing |
| **Azure Spring Apps** | Spring Boot microservices platform |
| **SignalR Service** | Real-time web functionality (WebSockets as a service) |

### 🔐 Identity + Security
| Service | Description |
|---|---|
| **Microsoft Entra ID** (formerly Azure AD) | Cloud identity; SSO; MFA; B2B/B2C; Conditional Access |
| **Microsoft Entra ID External Identities** | Customer + partner identity (B2B/B2C) |
| **Microsoft Entra Domain Services** | Managed AD DS without domain controllers |
| **Microsoft Sentinel** | Cloud-native SIEM + SOAR; AI-driven threat detection |
| **Microsoft Defender for Cloud** | CSPM + CWPP; security posture management |
| **Defender for IoT** | OT/IoT asset security |
| **Defender EASM** | External Attack Surface Management |
| **Azure Key Vault** | Managed HSM; secrets, keys, certificates |
| **Dedicated HSM** | Single-tenant HSM; FIPS 140-2 Level 3 |
| **DDoS Protection** | Always-on DDoS mitigation |
| **Information Protection** | Classify/protect sensitive data (MIP) |
| **Copilot for Security** | AI-powered security analyst; threat investigation |
| **Trusted Signing** | Code signing service |
| **Azure AD EI** | External Identities |

### 🌐 IoT + Mixed Reality
| Service | Description |
|---|---|
| **Azure IoT Hub** | Connect, monitor, manage millions of IoT devices |
| **Azure IoT Central** | Fully managed IoT SaaS application platform |
| **Azure IoT Edge** | Run cloud intelligence on IoT edge devices |
| **Azure IoT Operations** | Industrial IoT data processing at the edge |
| **Azure Sphere** | End-to-end MCU security; Linux-based OS |
| **Azure Digital Twins** | IoT-based digital representations of real-world environments |
| **Azure Maps** | Enterprise maps, geospatial APIs, location intelligence |
| **Defender for IoT** | OT/IoT security |

### 🔗 Integration
| Service | Description |
|---|---|
| **Azure Service Bus** | Enterprise messaging; queues + topics + relay |
| **Azure Event Grid** | Event routing; 100K ops/mo free tier |
| **Azure Logic Apps** | Low-code workflow automation; 400+ connectors |
| **Azure API Management** | API gateway; publish, secure, transform APIs |
| **API Center** | Centralized API inventory + governance |
| **Azure Notification Hubs** | Push notifications to any platform (iOS, Android, Windows) |
| **Azure Health Data Services** | FHIR, DICOM, MedTech services |
| **Energy Data Manager** | Oil/gas/energy data management |
| **Web PubSub** | Real-time messaging; WebSocket as a service |

### 🏗️ Management + Governance
| Service | Description |
|---|---|
| **Azure Monitor** | Full-stack monitoring; metrics, logs, alerts, dashboards |
| **Azure Arc** | Extend Azure management to on-prem, multi-cloud, edge |
| **Azure Policy** | Enforce organizational standards; compliance at scale |
| **Azure Blueprints** | Repeatable environment definitions (moving to Deployment Stacks) |
| **Azure Automation** | Runbooks; DSC; process automation |
| **Azure Backup** | Backup for VMs, SQL, SAP HANA, blobs, disks |
| **Microsoft Cost Management** | Cloud spend analysis, budgets, alerts — free for Azure |
| **Azure Advisor** | Personalized best practice recommendations |
| **Azure Lighthouse** | Multi-tenant management for MSPs/partners |
| **Azure Automanage** | Automated machine management (patching, backup, monitoring) |
| **Azure Managed Applications** | ISV-managed Azure solutions in marketplace |
| **Azure Portal** | Web-based management UI |
| **Cloud Shell** | Browser-based CLI (Bash/PowerShell) with persistent storage |
| **Carbon Optimization** | Track and reduce Azure carbon footprint |
| **Copilot in Azure** | AI-assisted management + troubleshooting |
| **Update Manager** | Manage OS + application updates at scale |
| **SRE Agent** | AI agent for site reliability engineering (2025) |
| **Kubernetes Fleet Manager** | Multi-cluster Kubernetes management |

### 📡 Networking
| Service | Description |
|---|---|
| **Azure Virtual Network (VNet)** | Private network in Azure; free to 1,000 VNets |
| **Azure VPN Gateway** | Site-to-site, point-to-site, VNet-to-VNet VPN |
| **ExpressRoute** | Dedicated private connectivity from on-prem to Azure |
| **Azure Firewall** | Managed, cloud-native network firewall |
| **Azure Front Door** | Global CDN + WAF + load balancer |
| **Azure CDN** | Content delivery; 118 PoP locations in 100 cities |
| **Application Gateway** | L7 load balancer + WAF |
| **Load Balancer** | L4 load balancing |
| **Traffic Manager** | DNS-based global load balancing |
| **Azure DNS** | Host DNS domains in Azure |
| **Private Link** | Private access to Azure services over VNet |
| **Azure Bastion** | Secure, browser-based RDP/SSH without public IP |
| **Network Watcher** | Network monitoring and diagnostics |
| **Virtual WAN** | Unified networking hub (SD-WAN integration) |
| **Route Server** | BGP route exchange between NVAs and VNet |
| **VNet Manager** | Centralized VNet management |
| **Private 5G Core** | Deploy private 5G/LTE networks on Azure |
| **Azure Orbital** | Ground station as a service; satellite data ingestion |

### 💾 Storage
| Service | Description |
|---|---|
| **Azure Storage** (Blob, Queue, Table, File) | Core object, queue, NoSQL table, file share storage |
| **Azure Blob Storage** | Object storage; hot/cool/cold/archive tiers |
| **Azure Files** | Fully managed SMB/NFS file shares |
| **Azure Data Lake Storage** | Hadoop-compatible analytics storage; hierarchical namespace |
| **Azure Managed Disks** | Block storage for VMs; Standard HDD/SSD, Premium SSD, Ultra Disk |
| **Azure NetApp Files** | Enterprise NFS/SMB; high performance; SAP-certified |
| **Azure Elastic SAN** | Cloud-native SAN (Storage Area Network) |
| **Container Storage** | Platform-managed container-native storage (Aug 2024 — industry first) |
| **Azure Managed Lustre** | High-performance parallel file system for HPC |
| **Storage Discovery** | Inventory and classify storage assets |
| **Storage Actions** | Automated storage management operations |
| **Data Share** | Simple/safe share of data with external organizations |
| **Confidential Ledger** | Tamper-proof record keeping; blockchain-backed |
| **Azure Backup** | see Management |
| **Site Recovery (BCDR)** | Disaster recovery for VMs and physical servers |

### 🔄 Migration
| Service | Description |
|---|---|
| **Azure Migrate** | Discover, assess, migrate on-prem workloads |
| **Azure Data Box** | Offline data transfer (80 TB/device) |
| **Database Migration Service** | Migrate databases to Azure with minimal downtime |
| **Resource Mover** | Move resources between regions/subscriptions |

---

## Azure Global Infrastructure

### Key Stats
- **70+ announced regions** — more than any other cloud provider
- **400+ datacenters** globally (FY2025)
- **118 CDN PoP locations** in 100 cities (Edge locations)
- **$80B CapEx FY2025** — largest in company history; >50% in US
- **$35B in 14 countries** committed over 3 years (Brad Smith, Jan 2025)

### Availability Zones (AZs)
Azure has 3+ physically separate datacenters per AZ-enabled region.
US AZ expansion in progress:
- North Central US → AZ by end of 2026
- West Central US → AZ in early 2027
- US Gov Arizona → AZ in early 2026
- East US 2 (Virginia) + South Central US (Texas) → additional AZs in 2026

### Regional Expansion (2025–2026)
| Region | Status |
|---|---|
| Malaysia | Launched 2025 |
| Indonesia | Launched 2025 |
| India South Central (Hyderabad) | Launching 2026 |
| Taiwan | Launching 2026 |
| Austria | Expanding |
| Chile | Expanding |
| Spain | Expanding |
| Kuwait | AI-powered region announced (March 2025) |
| Malaysia Southeast Asia 3 | Announced |

### India Investment
**$3 billion over 2 years** in India cloud + AI infrastructure (announced 2025).
Current India regions: Central India (Pune), South India (Chennai), West India (Mumbai), Jio India West, Jio India Central.
New: India South Central (Hyderabad) → 2026.

### Capacity Constraints (as of early 2026)
- Northern Virginia (East US) and Texas (South Central US) remain under capacity restrictions through mid-2026 — demand exceeds supply
- Azure canceled/deferred ~2 GW of leases in 2025 (portfolio optimization — moving to AI-dense campuses)
- Globally, data center electricity demand expected to hit 130 GW by 2028

---

## Azure Infrastructure Technology

### Hardware & Silicon
- **Ampere Cloud-native processors** — ARM-based VMs since 2022
- **Custom AI chips (MAI series)** — Microsoft's own AI processors; expected to replace 25% of NVIDIA dependency over 3 years
- **NVIDIA partnership** — Vera Rubin NVL72 (Microsoft was first cloud to validate); A100, H100, H200 GPU clusters
- **Azure Boost** — custom hardware offload card (networking + storage acceleration)
- **Maia 100** — Microsoft's AI accelerator chip (custom ASIC for LLM inference)

### Software Layer
- **Azure OS** — Specialized hypervisor/OS powering the "fabric layer" across all datacenters
- **Azure Resource Manager (ARM)** — Declarative deployment; ARM templates; Bicep
- **Azure Service Fabric** — Underlying microservices OS for many Azure services
- **Azure Arc** — Extends ARM to anywhere (on-prem, other clouds, edge)

### Service Levels
- **IaaS:** VMs, Storage, Networking — customer manages OS + above
- **PaaS:** App Service, AKS, Functions — Microsoft manages runtime + below
- **SaaS:** Microsoft 365, Dynamics 365, Power Platform — fully managed

---

## Azure AI Infrastructure (2025)

The $80B CapEx is primarily for **AI infrastructure**:
- AI supercomputing clusters for LLM training (OpenAI partnership: models trained exclusively on Azure)
- Inference infrastructure for 1B+ Copilot queries/day
- Azure AI Foundry: 80,000+ customers, 11,000+ models
- OpenAI partnership renewed October 2025 — extends through 2032
- $250B compute purchase commitment from OpenAI
- Anthropic models available: Claude Opus 4.5, Claude Sonnet 4.5, Haiku 4.5 on Azure AI Foundry
- Microsoft Agent Framework launched October 2025 — multi-agent orchestration

---

## Azure Energy & Sustainability

- **Carbon-negative by 2030** (including Scope 3 emissions)
- **Water-positive by 2030**
- **Zero waste by 2030**
- **$10B Brookfield deal** — renewable energy partnership
- **BlackRock + MGX + Global Infrastructure Partners** — $100B data center + power infrastructure fund (Sept 2025)
- Azure data centers powered by solar, wind, nuclear (Three Mile Island restart partnership with Constellation Energy)
- Liquid cooling and advanced thermal management for GPU clusters

---

## Azure Compliance & Security Posture

- **FedRAMP JAB Provisional ATO** (US federal government authorized)
- **Azure Government** — dedicated sovereign cloud for US government
- **Azure Government Secret/Top Secret** — classified workloads
- **ISO 27001:2005** certified
- **HIPAA** compliant
- **SOC 1/2/3**
- **PCI DSS Level 1**
- **GDPR** compliant (EU Data Boundary available)
- **India** — MeitY empanelled; RBI compliance; SEBI compliance
- **Australia** — IRAP assessed; AU data sovereignty
- **Sovereign Clouds** — Azure China (21Vianet), Azure Germany (deprecated), national clouds
- **Microsoft Patriot Act note:** Per US law, Microsoft has acknowledged US government can potentially access data regardless of hosting location — addressed via Azure Trust Center

---

## Azure Key Differentiators vs AWS vs GCP

| Dimension | Azure Advantage |
|---|---|
| **Enterprise integration** | M365, Teams, Windows, Active Directory → natural Azure pull |
| **Hybrid cloud** | Azure Arc + Azure Local: manage on-prem + cloud uniformly |
| **AI/OpenAI** | Exclusive OpenAI partner; GPT-4o native across all services |
| **Identity** | Microsoft Entra ID = most-used enterprise identity globally |
| **Developer tooling** | GitHub + VS Code + Azure DevOps = full DevSecOps stack |
| **Compliance** | 100+ compliance certifications; most government certifications |
| **SaaS tie-in** | Only hyperscaler with M365 + Dynamics 365 on same platform |

---

## MSFT-X: When to Load This File

Load `references/azure-platform.md` for:
- Azure's complete service catalog (13 categories, 100+ named services)
- Azure financial metrics: $75B+ revenue, 22% market share, 39% YoY growth
- Competitive comparison: Azure vs AWS (32%) vs GCP (13%)
- $80B CapEx FY2025 — what it's funding (AI infra, silicon, regions)
- Global regions (70+), datacenters (400+), AZ expansion plans
- India $3B investment, Hyderabad region 2026
- Custom AI chips (Maia 100), Ampere ARM VMs, NVIDIA Vera Rubin
- Azure sustainability (carbon-negative 2030, Brookfield deal)
- Compliance: FedRAMP, HIPAA, ISO, SOC, GDPR, India MeitY
- Azure capacity constraints (Northern Virginia, Texas through mid-2026)
- OpenAI partnership renewal (2025, through 2032, $250B compute)
- Anthropic models (Claude) available on Azure AI Foundry
