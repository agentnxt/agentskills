# Autonomyx Master Feature Registry

This is the canonical, living feature list maintained across all Autonomyx skills.
It is organised by software category and structured to match Dimension 1 (Features)
of the SaaS Standardizer profile format.

**Maintained by:** saas-standardizer skill (writes) + feature-gap-analyzer skill (discovers)
**Referenced by:** feature-gap-analyzer (reads feature checklist per category)
**Vocabulary:** See autonomyx-vocabulary/SKILL.md for category resolution and badge definitions

When a skill discovers a new feature not listed here, it must append it to the correct
category block under the appropriate sub-section, with a source note and discovery date.

---

## How to Read This File

Each category block contains sub-sections matching the SaaS Standardizer Dimension 1 structure:
- **Core Capabilities** — primary features that define the category
- **AI / ML** — AI-specific features in this category
- **API & Developer** — API, webhook, SDK features
- **Data Ingestion** — import, ETL, streaming capabilities
- **Reporting & Analytics** — dashboards, exports, BI features
- **Integrations** — native connectors, marketplace, iPaaS
- **Security & Compliance** — auth, certifications, data governance
- **Mobile** — app and offline features
- **Automation & Customization** — workflow, rules, templating
- **Notable Gaps (Category-Wide)** — features commonly missing or immature across this category

Each feature entry format:
```
- Feature name: brief description [Source: <origin> | Added: <YYYY-MM>]
```

---

## CRM / Sales Force Automation

### Core Capabilities
- Contact & account management: 360-degree view of contacts and companies [Source: Gartner SFA definition | Added: 2026-03]
- Opportunity / deal pipeline: visual pipeline with stage management and probability scoring [Source: Gartner SFA definition | Added: 2026-03]
- Lead management: capture, scoring, assignment, and conversion tracking [Source: Gartner SFA definition | Added: 2026-03]
- Activity tracking: calls, emails, meetings, tasks logged against records [Source: Gartner SFA definition | Added: 2026-03]
- Sales forecasting: quota tracking and revenue prediction by rep, team, or period [Source: Gartner SFA definition | Added: 2026-03]
- Territory & quota management: geographic or segment-based assignment and targets [Source: Gartner SFA definition | Added: 2026-03]
- CPQ (Configure, Price, Quote): product catalog, pricing rules, discount approvals, quote generation [Source: Gartner CPQ definition | Added: 2026-03]
- Email / calendar sync: bidirectional sync with Gmail, Outlook, Exchange [Source: G2 CRM category | Added: 2026-03]
- Deal rooms / buyer portals: shared workspace for vendor and buyer during sales cycle [Source: G2 CRM category | Added: 2026-03]
- Sales playbooks: guided selling steps and talk tracks [Source: G2 Sales Engagement | Added: 2026-03]

### AI / ML
- AI-powered lead scoring: ML model scoring leads by conversion likelihood [Source: Gartner SFA definition | Added: 2026-03]
- Predictive sales forecasting: ML-driven revenue forecasting beyond rep-entered estimates [Source: Gartner SFA definition | Added: 2026-03]
- Conversation intelligence: call recording, transcription, and AI coaching [Source: G2 CRM category | Added: 2026-03]
- AI email assistant: AI-drafted follow-up emails and response suggestions [Source: G2 CRM category | Added: 2026-03]
- Next-best-action recommendations: AI surface suggested next steps per deal [Source: Gartner SFA definition | Added: 2026-03]
- AI copilot / assistant: natural language interface for querying CRM data [Source: G2 CRM category | Added: 2026-03]

### API & Developer
- REST API: full CRUD access to all CRM objects [Source: Gartner SFA definition | Added: 2026-03]
- Bulk API: high-volume data operations [Source: Salesforce API docs | Added: 2026-03]
- Streaming API / change events: real-time event notifications on record changes [Source: Salesforce API docs | Added: 2026-03]
- Webhooks: event-driven outbound notifications [Source: G2 CRM category | Added: 2026-03]
- Sandbox environment: isolated dev/test instance [Source: G2 CRM category | Added: 2026-03]
- CLI / developer tooling: command-line tools for deployment and scripting [Source: G2 CRM category | Added: 2026-03]

### Data Ingestion
- CSV / Excel import: bulk record import via flat file [Source: G2 CRM category | Added: 2026-03]
- Data migration tools: wizard-based import from legacy CRM [Source: G2 CRM category | Added: 2026-03]
- ETL / pre-built connectors: native connectors to marketing, ERP, support tools [Source: G2 CRM category | Added: 2026-03]
- Real-time data sync: bidirectional live sync with external systems [Source: G2 CRM category | Added: 2026-03]
- Data deduplication: automatic detection and merging of duplicate records [Source: G2 CRM category | Added: 2026-03]

### Reporting & Analytics
- Pre-built sales dashboards: out-of-box pipeline, activity, and forecast reports [Source: Gartner SFA definition | Added: 2026-03]
- Custom report builder: drag-and-drop report creation on any CRM object [Source: Gartner SFA definition | Added: 2026-03]
- Pipeline analytics: stage-by-stage conversion rates and velocity metrics [Source: G2 CRM category | Added: 2026-03]
- Forecasting dashboards: real-time quota attainment and call views [Source: Gartner SFA definition | Added: 2026-03]
- Export to CSV / PDF: report export for offline sharing [Source: G2 CRM category | Added: 2026-03]
- Embedded BI / analytics platform: full BI layer built into CRM (beyond standard reports) [Source: Gartner SFA definition | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Deep CPQ: many CRMs have lightweight quoting but lack full CPQ logic [Source: Gartner CPQ MQ | Added: 2026-03]
- Revenue intelligence: separate from CRM in most vendors — requires add-on [Source: Gartner Revenue Intelligence Market Guide | Added: 2026-03]
- Advanced territory planning: commonly outsourced to specialist tools [Source: G2 CRM category | Added: 2026-03]

---

## Marketing Automation

### Core Capabilities
- Email campaign builder: drag-and-drop email creation with templates [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- Journey / campaign orchestration: multi-step, multi-channel campaign workflows [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- Lead capture: forms, landing pages, progressive profiling [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- Lead scoring & grading: demographic and behavioral scoring models [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- Lead routing & assignment: rules-based routing to sales reps or queues [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- A/B and multivariate testing: subject lines, content, send times [Source: G2 Marketing Automation | Added: 2026-03]
- Attribution modeling: first-touch, last-touch, multi-touch revenue attribution [Source: G2 Marketing Automation | Added: 2026-03]
- Account-based marketing (ABM): account targeting, engagement scoring, intent signals [Source: Gartner ABM Platforms definition | Added: 2026-03]
- Social media publishing: schedule and publish content to social channels [Source: G2 Marketing Automation | Added: 2026-03]
- SMS / push notifications: outbound channels beyond email [Source: G2 Marketing Automation | Added: 2026-03]

### AI / ML
- AI content generation: AI-drafted email copy, subject lines, and landing page content [Source: G2 Marketing Automation | Added: 2026-03]
- Predictive lead scoring: ML-based scoring beyond rule-based models [Source: Gartner B2B Marketing Automation definition | Added: 2026-03]
- Send-time optimization: ML-predicted optimal send time per contact [Source: G2 Marketing Automation | Added: 2026-03]
- AI audience segmentation: ML-driven dynamic segment creation [Source: G2 Marketing Automation | Added: 2026-03]
- Conversational marketing bot: AI chatbot for inbound lead qualification [Source: G2 Conversational Marketing | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Native CDP: most marketing automation tools require separate CDP integration [Source: Gartner CDP definition | Added: 2026-03]
- Advanced revenue attribution: multi-touch B2B attribution is commonly weak or add-on [Source: G2 Marketing Automation | Added: 2026-03]

---

## HR / Human Capital Management

### Core Capabilities
- Employee records management: central employee data store, org chart, job history [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Payroll processing: gross-to-net calculation, tax filing, pay slips [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Benefits administration: enrollment, eligibility, carrier connections [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Time & attendance: clock-in/out, shift scheduling, overtime rules [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Leave & absence management: PTO policies, leave requests, balance tracking [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Onboarding workflows: new hire checklist, document signing, task assignment [Source: G2 Core HR | Added: 2026-03]
- Performance management: goal setting (OKRs/KPIs), reviews, 360 feedback [Source: Gartner Talent Management Suites definition | Added: 2026-03]
- Learning management (LMS): course creation, assignment, completion tracking, certifications [Source: Gartner LMS definition | Added: 2026-03]
- Applicant tracking (ATS): job postings, pipeline, interview scheduling, offer management [Source: Gartner Talent Acquisition Suites definition | Added: 2026-03]
- Workforce planning: headcount modeling, scenario planning, skills gap analysis [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Compensation management: salary bands, merit cycles, equity planning [Source: G2 Compensation Management | Added: 2026-03]
- Compliance & labor law: jurisdiction-specific rules, audit trails, statutory reporting [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]

### AI / ML
- AI-assisted job description writing: AI draft JDs from role inputs [Source: G2 ATS category | Added: 2026-03]
- Predictive attrition / flight risk scoring: ML models for employee turnover risk [Source: Gartner Cloud HCM Suites definition | Added: 2026-03]
- Skills inference: auto-tagging employee skills from work history and activity [Source: Gartner Skills Management Platforms | Added: 2026-03]
- AI coaching recommendations: personalised development nudges [Source: G2 Core HR | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Global multi-country payroll: native global payroll is rare — most use partner networks [Source: Gartner Cloud HCM Suites MQ | Added: 2026-03]
- Advanced workforce planning: deep headcount modeling often requires add-on or specialist tool [Source: Gartner Cloud HCM Suites MQ | Added: 2026-03]

---

## Analytics & Business Intelligence

### Core Capabilities
- Interactive dashboards: drag-and-drop dashboard builder with charts and filters [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Self-service report builder: ad-hoc report creation by non-technical users [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Data modeling / semantic layer: business-friendly abstraction over raw data [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Direct query / live connection: query source databases without ETL [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Data extract / scheduled refresh: extract-based model with scheduled data loads [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Data catalog: searchable inventory of datasets, fields, and lineage [Source: Gartner Data Cataloging Tools definition | Added: 2026-03]
- Embedded analytics: white-label BI embeddable in third-party apps [Source: Gartner ABI Platforms definition | Added: 2026-03]
- Mobile analytics: iOS / Android app with interactive dashboards [Source: G2 Business Intelligence Platforms | Added: 2026-03]
- Alerting & subscriptions: threshold-based alerts and scheduled email/Slack reports [Source: G2 Business Intelligence Platforms | Added: 2026-03]
- Collaboration: comments, annotations, sharing within the BI tool [Source: G2 Business Intelligence Platforms | Added: 2026-03]
- Data governance & lineage: field-level lineage, certification, access controls [Source: Gartner ABI Platforms definition | Added: 2026-03]

### AI / ML
- Natural language query (NLQ): ask questions in plain English, get chart/table back [Source: Gartner Augmented Analytics definition | Added: 2026-03]
- AI-generated insights: automated narrative explanations of data trends [Source: Gartner Augmented Analytics definition | Added: 2026-03]
- Anomaly detection: ML-flagged unusual patterns in metrics [Source: Gartner ABI Platforms definition | Added: 2026-03]
- AI chart recommendation: suggests best chart type for selected data [Source: G2 Business Intelligence Platforms | Added: 2026-03]
- Predictive analytics: forecasting and regression built into the BI layer [Source: Gartner Augmented Analytics definition | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Advanced ML workbench: most BI tools lack in-product ML model training [Source: Gartner ABI Platforms MQ | Added: 2026-03]
- Real-time streaming analytics: live sub-second analytics commonly requires separate tool [Source: Gartner Streaming Analytics definition | Added: 2026-03]

---

## Project Management

### Core Capabilities
- Task & work item management: create, assign, prioritise, and track tasks [Source: Gartner Collaborative Work Management definition | Added: 2026-03]
- Gantt / timeline view: dependency-aware project timeline [Source: Gartner PPM definition | Added: 2026-03]
- Kanban / board view: visual card-based workflow management [Source: G2 Project Management | Added: 2026-03]
- Resource management: assign team members, manage capacity, view utilisation [Source: Gartner PPM definition | Added: 2026-03]
- Portfolio management: cross-project rollup, prioritisation, and reporting [Source: Gartner PPM definition | Added: 2026-03]
- Time tracking: log hours against tasks or projects [Source: G2 Project Management | Added: 2026-03]
- Budget management: track project costs and budget vs actuals [Source: Gartner PPM definition | Added: 2026-03]
- Risk management: risk register, impact/probability scoring [Source: Gartner PPM definition | Added: 2026-03]
- Dependencies: task-to-task and project-to-project dependency mapping [Source: G2 Project Management | Added: 2026-03]
- Custom fields & views: user-definable fields and configurable layouts [Source: G2 Project Management | Added: 2026-03]
- Workload view: per-person capacity and assignment overview [Source: G2 Project Management | Added: 2026-03]
- Goals / OKRs: team and company objective tracking linked to work [Source: G2 Project Management | Added: 2026-03]

### AI / ML
- AI task creation: generate subtasks or project plans from natural language prompts [Source: G2 Project Management | Added: 2026-03]
- AI workload balancing: suggest reassignments based on capacity data [Source: G2 Project Management | Added: 2026-03]
- Risk prediction: ML flags at-risk projects based on progress signals [Source: Gartner PPM definition | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Native financial project accounting: detailed cost accounting commonly requires ERP integration [Source: Gartner PPM MQ | Added: 2026-03]
- Advanced resource forecasting: long-range capacity planning is weak in most tools [Source: Gartner PPM MQ | Added: 2026-03]

---

## ITSM / IT Service Management

### Core Capabilities
- Incident management: log, classify, assign, and resolve IT incidents [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Problem management: root cause analysis, known error database [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Change management: change requests, CAB approvals, risk assessment, rollback [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Service catalog & request management: self-service catalog with fulfillment workflows [Source: Gartner ITSM Tools definition | Added: 2026-03]
- SLA management: SLA policies, breach alerting, reporting [Source: Gartner ITSM Tools definition | Added: 2026-03]
- CMDB / asset management: configuration items, relationships, dependency mapping [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Knowledge management: article authoring, search, feedback, version control [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Self-service portal: end-user ticket submission and status tracking [Source: Gartner ITSM Tools definition | Added: 2026-03]
- ITIL v4 alignment: support for ITIL practices including value streams [Source: G2 ITSM category | Added: 2026-03]
- Event management: alert ingestion, correlation, auto-ticket creation [Source: Gartner ITSM Tools definition | Added: 2026-03]

### AI / ML
- AI chatbot / virtual agent: conversational self-service for common IT requests [Source: Gartner ITSM Tools definition | Added: 2026-03]
- Intelligent ticket routing: ML-based assignment to correct team or individual [Source: G2 ITSM category | Added: 2026-03]
- AI-suggested resolutions: surface relevant KB articles during ticket creation [Source: G2 ITSM category | Added: 2026-03]
- Predictive incident prevention: ML flags services likely to generate incidents [Source: Gartner ITSM Tools definition | Added: 2026-03]
- AIOps integration: auto-correlation of monitoring alerts into ITSM tickets [Source: Gartner AIOps Platforms definition | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Native observability / APM: most ITSM tools rely on integrations for monitoring data [Source: Gartner ITSM Tools MQ | Added: 2026-03]
- Financial management for IT (ITFM): cost allocation and chargeback typically requires specialist tool [Source: Gartner ITSM Tools MQ | Added: 2026-03]

---

## Customer Success / Support

### Core Capabilities
- Customer health scoring: composite score from usage, support, NPS, contract signals [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- 360-degree customer view: unified timeline of all customer touchpoints [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- Playbook automation: trigger-based playbook steps (task creation, emails, alerts) [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- NPS / CSAT / CES surveys: in-app and email survey collection and reporting [Source: G2 Customer Success | Added: 2026-03]
- Renewal & expansion tracking: renewal date tracking, upsell/cross-sell opportunity management [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- Escalation workflows: automatic alert and handoff on at-risk accounts [Source: G2 Customer Success | Added: 2026-03]
- Customer segmentation: tier-based or rules-based customer portfolio management [Source: G2 Customer Success | Added: 2026-03]
- Usage data ingestion: product telemetry / event data ingestion for health scoring [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- Ticketing / case management: support ticket creation, SLA tracking, resolution [Source: Gartner Customer Service Management definition | Added: 2026-03]
- Knowledge base: customer-facing help center with article management [Source: G2 Customer Success | Added: 2026-03]

### AI / ML
- AI churn prediction: ML model scoring accounts by churn likelihood [Source: Gartner Customer Success Management Platforms definition | Added: 2026-03]
- AI-recommended next best action: surface suggested engagement steps per account [Source: G2 Customer Success | Added: 2026-03]
- Conversational AI / chatbot: AI self-service for support deflection [Source: Gartner AI-Augmented Customer Service Platforms definition | Added: 2026-03]
- Sentiment analysis: AI analysis of support tickets and survey responses [Source: G2 Customer Success | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Deep product analytics integration: most CS platforms require separate product analytics tool for usage data [Source: Gartner Customer Success Management Platforms MQ | Added: 2026-03]
- Native billing / subscription integration: contract and revenue data commonly sourced from external CRM or billing system [Source: Gartner Customer Success Management Platforms MQ | Added: 2026-03]

---

## ERP / Finance

### Core Capabilities
- General ledger (GL): chart of accounts, journal entries, period close [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Accounts payable (AP): invoice processing, approvals, payment runs [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Accounts receivable (AR): invoicing, collections, cash application [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Fixed assets: asset register, depreciation schedules [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Multi-entity / multi-currency: intercompany eliminations, FX revaluation [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Financial consolidation: group reporting, eliminations, minority interest [Source: Gartner Financial Consolidation & Close Solutions definition | Added: 2026-03]
- Revenue recognition: ASC 606 / IFRS 15 compliant revenue schedules [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- Budgeting & forecasting: budget creation, variance analysis, rolling forecasts [Source: Gartner FP&A Platforms definition | Added: 2026-03]
- Procurement / purchasing: purchase orders, vendor management, three-way match [Source: Gartner Source-to-Pay definition | Added: 2026-03]
- Expense management: employee expense submission, approval, reimbursement [Source: G2 ERP Systems | Added: 2026-03]
- Audit trail: immutable record of all financial transactions [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]
- SOX / IFRS compliance controls: segregation of duties, control documentation [Source: Gartner Cloud Core Financial Management Suites definition | Added: 2026-03]

### AI / ML
- AI-assisted invoice processing / AP automation: OCR and ML extraction of invoice data [Source: Gartner AP Invoice Automation definition | Added: 2026-03]
- Predictive cash flow forecasting: ML-based cash position forecasting [Source: Gartner FP&A Platforms definition | Added: 2026-03]
- Anomaly detection in transactions: AI flagging of unusual financial entries [Source: G2 ERP Systems | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Advanced FP&A: deep driver-based planning commonly requires specialist FP&A tool [Source: Gartner FP&A Platforms MQ | Added: 2026-03]
- Integrated tax management: complex tax compliance commonly outsourced to specialist [Source: Gartner Tax and Revenue Management Platforms definition | Added: 2026-03]

---

## DevOps / Engineering Tools

### Core Capabilities
- CI/CD pipelines: automated build, test, and deploy pipelines [Source: Gartner DevOps Platforms definition | Added: 2026-03]
- Source code management (SCM): Git repository hosting and management [Source: Gartner DevOps Platforms definition | Added: 2026-03]
- Infrastructure as Code (IaC): Terraform, Pulumi, CloudFormation support [Source: Gartner DevOps Platforms definition | Added: 2026-03]
- Container orchestration: Kubernetes deployment and management support [Source: G2 DevOps Platforms | Added: 2026-03]
- Secrets management: secure storage and injection of credentials [Source: G2 DevOps Platforms | Added: 2026-03]
- Observability / APM: application performance monitoring, tracing, logging [Source: Gartner APM definition | Added: 2026-03]
- GitOps workflows: declarative infrastructure management via Git [Source: G2 DevOps Platforms | Added: 2026-03]
- Security scanning (DevSecOps): SAST, DAST, dependency scanning in pipeline [Source: Gartner DevOps Platforms definition | Added: 2026-03]
- Artifact management: package registry and binary storage [Source: G2 DevOps Platforms | Added: 2026-03]
- Feature flags: controlled feature rollout and A/B testing for developers [Source: G2 DevOps Platforms | Added: 2026-03]

### AI / ML
- AI code review / suggestions: AI-powered PR review and code completion [Source: G2 DevOps Platforms | Added: 2026-03]
- AI-assisted root cause analysis: AI explanation of pipeline failures [Source: G2 DevOps Platforms | Added: 2026-03]
- Predictive test selection: ML selects minimal test suite based on code change [Source: G2 DevOps Platforms | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Unified platform depth: most tools excel in CI/CD or SCM but require integrations for full DevSecOps [Source: Gartner DevOps Platforms MQ | Added: 2026-03]
- Native cloud cost management: FinOps capabilities commonly require separate tool [Source: Gartner DevOps Platforms MQ | Added: 2026-03]

---

## Cybersecurity

### Core Capabilities
- Threat detection & response: real-time detection of malicious activity [Source: Gartner XDR definition | Added: 2026-03]
- SIEM: security event correlation, log management, alerting [Source: Gartner SIEM definition | Added: 2026-03]
- Endpoint protection: malware prevention, EDR, device control [Source: Gartner EPP definition | Added: 2026-03]
- Identity & access management (IAM): authentication, SSO, MFA, lifecycle management [Source: Gartner IAM definition | Added: 2026-03]
- Vulnerability management: scanning, prioritisation, remediation tracking [Source: Gartner Vulnerability Assessment definition | Added: 2026-03]
- SOAR: security orchestration, automation, and response playbooks [Source: Gartner SOAR definition | Added: 2026-03]
- Cloud security posture management (CSPM): misconfiguration detection in cloud environments [Source: Gartner CSPM definition | Added: 2026-03]
- Data loss prevention (DLP): monitor and prevent unauthorised data exfiltration [Source: Gartner DLP definition | Added: 2026-03]
- MITRE ATT&CK mapping: technique-level mapping of detections to ATT&CK framework [Source: G2 Cybersecurity | Added: 2026-03]
- Compliance reporting: pre-built reports for SOC 2, ISO 27001, NIST, PCI-DSS [Source: G2 Cybersecurity | Added: 2026-03]

### AI / ML
- AI-powered threat detection: ML anomaly detection beyond signature-based rules [Source: Gartner XDR definition | Added: 2026-03]
- Generative AI analyst assistant: AI-generated incident summaries and investigation guidance [Source: G2 Cybersecurity | Added: 2026-03]
- Automated triage: AI prioritisation and false positive reduction [Source: Gartner SIEM definition | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Unified platform coverage: most vendors are strong in one domain (endpoint, cloud, identity) but not all three [Source: Gartner XDR MQ | Added: 2026-03]

---

## Supply Chain & Procurement

### Core Capabilities
- Supplier management: supplier profiles, scorecards, onboarding, compliance [Source: Gartner Source-to-Pay definition | Added: 2026-03]
- Demand forecasting: statistical and ML-based demand planning [Source: Gartner Supply Chain Planning Solutions definition | Added: 2026-03]
- Inventory optimisation: safety stock, reorder points, multi-echelon planning [Source: Gartner Supply Chain Planning Solutions definition | Added: 2026-03]
- Purchase order management: PO creation, approval, tracking, and receipting [Source: Gartner Procure-to-Pay definition | Added: 2026-03]
- Contract lifecycle management: contract authoring, approval, obligation tracking [Source: Gartner Contract Lifecycle Management definition | Added: 2026-03]
- Multi-tier supply chain visibility: track goods across multiple tiers of suppliers [Source: Gartner Supply Chain Management definition | Added: 2026-03]
- Logistics / transportation management: carrier selection, shipment tracking, freight audit [Source: Gartner TMS definition | Added: 2026-03]
- Warehouse management: receiving, put-away, picking, packing, shipping [Source: Gartner WMS definition | Added: 2026-03]

### AI / ML
- AI demand sensing: short-range ML forecasting from POS and external signals [Source: Gartner Supply Chain Planning Solutions definition | Added: 2026-03]
- Supply risk prediction: ML flagging of at-risk suppliers or components [Source: G2 Supply Chain Management | Added: 2026-03]

### Notable Gaps (Category-Wide)
- End-to-end suite depth: most vendors strong in planning or execution but not both [Source: Gartner Supply Chain Management MQ | Added: 2026-03]

---

## Data Management & Integration

### Core Capabilities
- Master data management (MDM): golden record creation and governance for key entities [Source: Gartner MDM definition | Added: 2026-03]
- Data quality & cleansing: profiling, standardisation, deduplication, enrichment [Source: Gartner Data Quality Solutions definition | Added: 2026-03]
- ETL / ELT pipelines: extract, transform, load or extract, load, transform workflows [Source: Gartner Data Integration Tools definition | Added: 2026-03]
- Pre-built connector library: native connectors to SaaS apps, databases, cloud storage [Source: Gartner Data Integration Tools definition | Added: 2026-03]
- Real-time / streaming integration: event-driven or CDC-based real-time data movement [Source: Gartner Streaming Analytics definition | Added: 2026-03]
- Data lineage: field-level tracking of data origin, transformation, and consumption [Source: Gartner Metadata Management definition | Added: 2026-03]
- Data governance: policies, stewardship, access controls, compliance enforcement [Source: Gartner Metadata Management definition | Added: 2026-03]
- API management: design, publish, secure, and monitor APIs [Source: Gartner API Management definition | Added: 2026-03]
- iPaaS: no-code/low-code integration platform for business users [Source: Gartner iPaaS definition | Added: 2026-03]

### AI / ML
- AI-assisted data mapping: ML suggestions for field mappings between schemas [Source: Gartner Data Integration Tools definition | Added: 2026-03]
- AI data quality recommendations: ML flagging of quality issues and suggested fixes [Source: Gartner Data Quality Solutions definition | Added: 2026-03]
- Natural language data pipeline creation: AI-generated pipeline from plain-language description [Source: G2 Data Integration Tools | Added: 2026-03]

### Notable Gaps (Category-Wide)
- Unified governance + integration: data governance and integration capabilities rarely strong in same product [Source: Gartner Data Integration Tools MQ | Added: 2026-03]

---

## NEW FEATURES DISCOVERED (Pending Category Assignment)

> This section is a staging area. Features discovered by the feature-gap-analyzer or other
> Autonomyx skills that don't yet fit neatly into an existing category block are listed here
> temporarily. They should be reviewed and moved into the correct category block periodically.

<!-- Append new discoveries here in this format:
- Feature name: brief description [Discovered in: <product> | Source: <URL or analyst> | Added: <YYYY-MM>]
-->
