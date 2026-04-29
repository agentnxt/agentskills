---
did: skill:028
version: "1.0.0"
created: "2026-04-29"
name: skills-frameworks
description: >
  Shared vocabulary of professional skills frameworks used by Autonomyx skills. Contains the
  authoritative mapping of professions to their respective competency frameworks, skill codes,
  level definitions, and cross-framework equivalence tables. Use this skill whenever any
  Autonomyx skill needs to: map a skill to a professional framework, determine proficiency
  levels using a standardized competency model, select the correct framework for a given
  profession, or cross-reference skills across multiple frameworks. Covers IT (SFIA 9),
  cybersecurity (NICE/NIST), data science (EDISON), project management (PMI/IPMA), finance
  (CFA/ACCA), marketing (CIM), HR (SHRM/CIPD), design (UXPA), healthcare (AMIA), legal
  (SRA/ABA), supply chain (ASCM), engineering (UK-SPEC), education (UNESCO ICT), product
  management (Pragmatic), sales, and the European e-Competence Framework as a general fallback.
---

# Professional Skills Frameworks Vocabulary

Shared reference skill for mapping professional skills to internationally recognized
competency frameworks. Used by the `autonomyx-skill-score` skill and any future Autonomyx skill
that needs standardized skill classification.

Read the relevant section for your use case:
- **Framework selection** → Section 1 (how to choose the right framework for a profession)
- **SFIA 9 (IT/Digital)** → Section 2
- **NICE/NIST (Cybersecurity)** → Section 3
- **EDISON (Data Science/AI)** → Section 4
- **PMI / IPMA (Project Management)** → Section 5
- **CFA / ACCA (Finance)** → Section 6
- **SHRM / CIPD (Human Resources)** → Section 7
- **CIM (Marketing)** → Section 8
- **UXPA / IxDA (Design)** → Section 9
- **Other frameworks** → Section 10
- **Cross-framework level equivalence** → Section 11
- **Universal proficiency levels** → Section 12

---

## Section 1 — Framework Selection Logic

When mapping a person's skills to a framework, follow this order:

1. **Identify the primary profession** from the person's most recent/current job title
2. **Match to the framework table** below
3. If the person spans multiple domains (e.g., a "Data Science Manager" spans EDISON + PMI),
   apply multiple frameworks
4. If no specific framework matches, use the **European e-Competence Framework (e-CF 4.0)**
   as a general fallback for any technology-adjacent role
5. For completely non-technical roles with no applicable framework, use the **Universal
   Proficiency Levels** (Section 12) without a framework code

| Profession / Domain | Primary Framework | Levels | Reference URL |
|---|---|---|---|
| IT / Software / Digital | SFIA 9 | 1–7 | https://sfia-online.org/en/sfia-9/all-skills-a-z |
| Cybersecurity | NICE Workforce Framework (NIST SP 800-181r1) | Beginner–Expert | https://niccs.cisa.gov/workforce-development/nice-framework |
| Data Science / AI / ML | EDISON Data Science Framework (DS-BoK) | DSDA 1–6 | https://edison-project.eu |
| Project Management | PMI Talent Triangle + IPMA ICB4 | PMI: 3 domains; IPMA: A–D | https://www.pmi.org / https://www.ipma.world |
| Finance / Accounting | CFA Body of Knowledge / ACCA Competency Framework | CFA: 10 topics; ACCA: 5 levels | https://www.cfainstitute.org / https://www.accaglobal.com |
| Marketing / Digital Marketing | CIM Professional Marketing Competencies | Foundation–Expert | https://www.cim.co.uk |
| Human Resources | SHRM Competency Model / CIPD Profession Map | SHRM: 9 competencies; CIPD: 4 levels | https://www.shrm.org / https://www.cipd.org |
| Sales | MEDDIC/MEDDPICC + Sandler competencies | Custom levels | — |
| Design / UX / UI | UXPA Body of Knowledge / IxDA Competencies | Junior–Principal | https://uxpa.org |
| Healthcare IT / Informatics | AMIA Health Informatics Competencies | Foundational–Expert | https://amia.org |
| Legal | SRA Competence Statement (UK) / ABA Competencies (US) | Threshold–Advanced | https://www.sra.org.uk / https://www.americanbar.org |
| Supply Chain / Logistics | ASCM (APICS) Body of Knowledge | Associate–Master | https://www.ascm.org |
| Engineering (non-software) | UK-SPEC / EUR-ING Competence Standards | CEng/IEng/EngTech | https://www.engc.org.uk |
| Education / Training | UNESCO ICT Competency Framework for Teachers | Knowledge Acquisition–Creation | https://www.unesco.org |
| Product Management | Pragmatic Institute Framework | Foundational–Strategic | https://www.pragmaticinstitute.com |
| General / Cross-functional (technology-adjacent) | European e-Competence Framework (e-CF 4.0) | e-1 to e-5 | https://www.ecompetences.eu |

---

## Section 2 — SFIA 9 (IT / Software / Digital Professionals)

**Full reference:** https://sfia-online.org/en/sfia-9/all-skills-a-z

SFIA (Skills Framework for the Information Age) is the globally accepted framework for
describing skills and competencies in the digital world. It is used by organizations in
over 200 countries.

**SFIA is specifically for IT, software, and digital professionals.** Do not apply SFIA to
non-technology roles (use the appropriate profession-specific framework instead).

### SFIA Levels (1–7)

| Level | Name | Autonomy | Influence | Complexity | Resume equivalent |
|---|---|---|---|---|---|
| 1 | Follow | Close supervision | Minimal | Routine | Beginner |
| 2 | Assist | Routine supervision | Individual | Straightforward | Beginner |
| 3 | Apply | General guidance | Close colleagues | Moderately complex | Intermediate |
| 4 | Enable | Broad autonomy | Wide range of people | Complex, varied | Advanced |
| 5 | Ensure, Advise | Full accountability | Broad influence | Wide-ranging, complex | Expert |
| 6 | Initiate, Influence | Organizational authority | Strategic influence | Highly complex | Expert+ |
| 7 | Set strategy, Inspire | Industry authority | Industry-wide | Strategic, enterprise | Expert+ |

### Common SFIA Skill Codes

| Code | Skill Name | Typical resume skills |
|---|---|---|
| PROG | Programming/software development | Python, Java, JavaScript, React, Go, Rust, C++, TypeScript, Ruby, PHP, Swift, Kotlin |
| ARCH | Solution architecture | Cloud architecture, system design, microservices, enterprise architecture |
| DTAN | Data analysis | Data analytics, pandas, SQL analytics, Tableau, Power BI, data visualization |
| DBAD | Database administration | PostgreSQL, MySQL, MongoDB, Redis, DynamoDB, database design, data modeling |
| TEST | Testing | QA, test automation, Selenium, Cypress, Jest, unit testing, integration testing |
| ITOP | IT infrastructure | Kubernetes, Docker, Linux admin, networking, CI/CD, infrastructure management |
| SCTY | Information security | Security architecture, access control, encryption, security auditing |
| PENT | Penetration testing | Ethical hacking, vulnerability assessment, red teaming, OWASP |
| HSIN | AI / Machine Learning | TensorFlow, PyTorch, NLP, computer vision, MLOps, model training |
| SWDN | Software design | Design patterns, API design, DDD, system modeling |
| RELM | Release and deployment | CI/CD pipelines, GitOps, deployment automation, blue-green deploys |
| CFMG | Configuration management | Terraform, Ansible, Puppet, Chef, IaC |
| INCA | Information content authorship | Technical writing, documentation, API docs, content strategy |
| DESN | Systems design | UX/UI, wireframing, Figma, prototyping, design systems |
| BUAN | Business analysis | Requirements gathering, process modeling, user stories |
| DLMG | Development management | Engineering management, team leadership, tech lead |
| PRMG | Project management | Agile, Scrum, Kanban, sprint planning, Jira |
| EMRG | Emerging technology monitoring | AI adoption, blockchain evaluation, IoT, innovation scouting |
| DATM | Data management | Data governance, data quality, master data management, metadata |
| MLNG | Machine learning | ML model development, feature engineering, model evaluation |
| DENG | Data engineering | ETL/ELT, data pipelines, Spark, Airflow, Kafka, data warehousing |
| PORT | Portfolio management | Technology portfolio, investment prioritization, roadmap alignment |
| ITMG | IT management | IT strategy, governance, budgeting, vendor management |
| USUP | Service support | Incident management, service desk, problem resolution |
| CHMG | Change management | Change control, release management, impact assessment |

---

## Section 3 — NICE/NIST (Cybersecurity)

**Full reference:** https://niccs.cisa.gov/workforce-development/nice-framework

The NICE Workforce Framework (NIST SP 800-181 Rev. 1) categorizes cybersecurity work
into Work Roles, Competency Areas, and Task/Knowledge/Skill statements.

### NICE Work Role Categories

| Category | Code | Example work roles |
|---|---|---|
| Securely Provision | SP | Software Developer, Security Architect, Systems Developer |
| Operate and Maintain | OM | System Administrator, Network Operations, Data Administration |
| Oversee and Govern | OV | Cybersecurity Manager, Program Manager, IT Investment |
| Protect and Defend | PR | Incident Responder, Vulnerability Analyst, Cyber Defense Analyst |
| Analyze | AN | Threat Analyst, All-Source Analyst, Exploitation Analyst |
| Collect and Operate | CO | Cyber Operations Planner, Cyber Ops Specialist |
| Investigate | IN | Digital Forensics, Cyber Crime Investigator |

### NICE Proficiency Levels

| Level | Description | Resume equivalent |
|---|---|---|
| Entry | Foundational knowledge, works under supervision | Beginner |
| Intermediate | Applied knowledge, works independently on routine tasks | Intermediate |
| Advanced | Deep expertise, leads complex efforts | Advanced |
| Expert | Authoritative, shapes organizational/industry direction | Expert |

---

## Section 4 — EDISON (Data Science / AI)

**Full reference:** https://edison-project.eu

The EDISON Data Science Framework defines competency areas for data science professionals.

### EDISON Competency Groups

| Code | Competency Group | Typical skills |
|---|---|---|
| DSDA | Data Analytics | Statistical analysis, A/B testing, hypothesis testing, R, Python analytics |
| DSENG | Data Engineering | ETL, data pipelines, Spark, Kafka, Airflow, data warehousing |
| DSDM | Data Management | Data governance, quality, lineage, metadata management |
| DSRM | Research Methods | Experimental design, academic research, peer review, reproducibility |
| DSBA | Business Analytics | Business intelligence, KPI definition, dashboarding, decision modeling |
| DSML | Machine Learning | Supervised/unsupervised learning, deep learning, NLP, computer vision |
| DSAI | Artificial Intelligence | Generative AI, reinforcement learning, AI ethics, LLM fine-tuning |

### EDISON Proficiency Levels

| Level | Description | Resume equivalent |
|---|---|---|
| 1 — Awareness | Basic understanding | Beginner |
| 2 — Application | Can apply with guidance | Beginner–Intermediate |
| 3 — Working | Independent application | Intermediate |
| 4 — Practitioner | Deep expertise, mentors others | Advanced |
| 5 — Expert | Shapes practice, recognized authority | Expert |
| 6 — Thought Leader | Industry-wide influence | Expert+ |

---

## Section 5 — PMI / IPMA (Project Management)

### PMI Talent Triangle

| Domain | Description | Typical skills |
|---|---|---|
| Ways of Working | Technical project management methods | Agile, Scrum, Waterfall, Kanban, earned value, scheduling |
| Power Skills | Leadership and interpersonal | Communication, negotiation, conflict resolution, team building |
| Business Acumen | Strategic and business alignment | Benefits realization, ROI, strategic alignment, governance |

### IPMA ICB4 Levels

| Level | Title | Description | Resume equivalent |
|---|---|---|---|
| D | Certified Project Management Associate | Can apply knowledge in projects | Beginner–Intermediate |
| C | Certified Project Manager | Manages moderately complex projects | Intermediate–Advanced |
| B | Certified Senior Project Manager | Manages complex projects/programs | Advanced |
| A | Certified Projects Director | Manages portfolios, strategic level | Expert |

---

## Section 6 — CFA / ACCA (Finance)

### CFA Body of Knowledge Topics

| Topic | Typical skills |
|---|---|
| Ethical & Professional Standards | Compliance, fiduciary duty, ethics |
| Quantitative Methods | Financial modeling, statistics, econometrics |
| Economics | Macro/microeconomics, monetary policy |
| Financial Statement Analysis | GAAP/IFRS, ratio analysis, financial reporting |
| Corporate Issuers | Corporate governance, capital structure |
| Equity Investments | Valuation, fundamental analysis |
| Fixed Income | Bond pricing, yield analysis, credit analysis |
| Derivatives | Options, futures, swaps, risk management |
| Alternative Investments | PE, hedge funds, real estate, commodities |
| Portfolio Management | Asset allocation, portfolio construction, performance attribution |

### ACCA Competency Levels

| Level | Description | Resume equivalent |
|---|---|---|
| Foundational | Basic accounting knowledge | Beginner |
| Intermediate | Applied accounting skills | Intermediate |
| Advanced | Complex financial analysis | Advanced |
| Expert | Strategic financial leadership | Expert |
| Master | Thought leadership, industry shaping | Expert+ |

---

## Section 7 — SHRM / CIPD (Human Resources)

### SHRM Competency Model (9 Competencies)

| Competency | Description |
|---|---|
| HR Expertise (HR Knowledge) | Functional HR knowledge across all HR disciplines |
| Relationship Management | Managing interactions, providing service, and supporting the organization |
| Consultation | Providing guidance to organizational stakeholders |
| Leadership & Navigation | Directing and contributing to organizational initiatives |
| Communication | Effective exchange of information |
| Global & Cultural Effectiveness | Valuing and leveraging diverse perspectives |
| Ethical Practice | Integrity, professional accountability |
| Critical Evaluation | Interpreting data to make business decisions |
| Business Acumen | Understanding business operations and functions |

### CIPD Profession Map Levels

| Level | Title | Resume equivalent |
|---|---|---|
| Foundation | People practice support | Beginner |
| Associate | People practice delivery | Intermediate |
| Chartered Member | People practice leadership | Advanced |
| Chartered Fellow | Strategic people leadership | Expert |

---

## Section 8 — CIM (Marketing)

### CIM Professional Marketing Competencies

| Competency Area | Typical skills |
|---|---|
| Insights | Market research, customer analytics, segmentation, data interpretation |
| Strategy | Brand strategy, positioning, go-to-market, competitive analysis |
| Planning | Marketing planning, campaign management, budget allocation |
| Digital | SEO, SEM, social media marketing, email marketing, marketing automation |
| Content | Content strategy, copywriting, storytelling, content marketing |
| Customer Experience | CX design, journey mapping, personalization |
| Measurement | Marketing ROI, attribution modeling, A/B testing, KPI tracking |

### CIM Levels

| Level | Resume equivalent |
|---|---|
| Foundation | Beginner |
| Professional | Intermediate |
| Strategic | Advanced |
| Expert / Fellow | Expert |

---

## Section 9 — UXPA / IxDA (Design)

### UX Competency Areas

| Area | Typical skills |
|---|---|
| User Research | Interviews, usability testing, surveys, personas, journey maps |
| Information Architecture | Sitemaps, taxonomies, navigation design, card sorting |
| Interaction Design | Wireframes, prototyping, micro-interactions, design patterns |
| Visual Design | Typography, color theory, layout, brand application |
| Content Strategy | UX writing, microcopy, content audit, voice & tone |
| Accessibility | WCAG, assistive technology, inclusive design |
| Design Systems | Component libraries, design tokens, style guides |
| Facilitation | Workshops, design sprints, stakeholder alignment |

### Design Seniority Levels

| Level | Description | Resume equivalent |
|---|---|---|
| Junior | Works under direction, executes defined tasks | Beginner |
| Mid-level | Works independently, owns design deliverables | Intermediate |
| Senior | Leads design work, mentors, influences strategy | Advanced |
| Staff / Principal | Shapes design direction org-wide, thought leader | Expert |

---

## Section 10 — Other Frameworks

### Sales (MEDDIC/MEDDPICC)
| Competency | Description |
|---|---|
| Metrics | Quantifying business impact for the buyer |
| Economic Buyer | Identifying and engaging the decision-maker |
| Decision Criteria | Understanding how the buyer evaluates options |
| Decision Process | Mapping the buyer's procurement process |
| Identify Pain | Uncovering the business problem |
| Champion | Building an internal advocate |
| Paper Process (MEDDPICC) | Navigating legal/procurement |
| Competition (MEDDPICC) | Competitive positioning |

### Supply Chain — ASCM (APICS) Levels
| Level | Resume equivalent |
|---|---|
| Associate | Beginner |
| Professional | Intermediate |
| Senior Professional | Advanced |
| Master | Expert |

### Education — UNESCO ICT Competency Framework
| Level | Description | Resume equivalent |
|---|---|---|
| Knowledge Acquisition | Basic ICT literacy for teaching | Beginner |
| Knowledge Deepening | Applying ICT to complex problems | Intermediate |
| Knowledge Creation | Innovating with ICT, creating new approaches | Advanced–Expert |

### Product Management — Pragmatic Institute
| Level | Focus | Resume equivalent |
|---|---|---|
| Foundational | Market problems, user needs | Beginner |
| Functional | Product planning, positioning | Intermediate |
| Strategic | Business model, portfolio, vision | Advanced–Expert |

---

## Section 11 — Cross-Framework Level Equivalence

Use this table when a person's skills span multiple professions and you need to
normalize levels across frameworks.

| Universal Level | SFIA | NICE | EDISON | IPMA | ACCA | CIPD | CIM | Design | e-CF |
|---|---|---|---|---|---|---|---|---|---|
| **Beginner** | 1–2 | Entry | 1–2 | D | Foundational | Foundation | Foundation | Junior | e-1 |
| **Intermediate** | 3 | Intermediate | 3 | C | Intermediate | Associate | Professional | Mid | e-2–e-3 |
| **Advanced** | 4 | Advanced | 4 | B | Advanced | Chartered Member | Strategic | Senior | e-4 |
| **Expert** | 5–7 | Expert | 5–6 | A | Expert–Master | Chartered Fellow | Expert | Staff/Principal | e-5 |

---

## Section 12 — Universal Proficiency Levels

When no specific framework applies (e.g., purely non-technical, non-professional skills),
use these universal levels:

| Level | Criteria |
|---|---|
| **Beginner** | Foundational understanding. Can contribute with guidance. <1 year of use. |
| **Intermediate** | Solid working knowledge. Can deliver independently. 1–3 years of use. |
| **Advanced** | Strong proficiency. Can architect, mentor, and handle complex problems. 3–5 years. |
| **Expert** | Deep, authoritative command. Recognized by others in the field. 5+ years of sustained use. |

---

## Section 13 — When No Framework Exists

If the person's industry or profession is not covered by any framework listed above, follow
this protocol:

### Step 1 — Inform the user
Clearly state:
> "I could not find a recognized professional skills framework for **[industry/profession]**.
> The skills in this resume will be evaluated using general proficiency levels (Beginner /
> Intermediate / Advanced / Expert) unless you provide a specific framework."

### Step 2 — Ask the user
> "Do you have a preferred competency framework for **[industry/profession]**?
> This could be:
> - An industry body's competency model (e.g., a professional association's framework)
> - Your company's internal skills matrix or career ladder
> - A government or regulatory competency standard
> - Any other structured skills taxonomy
>
> If you provide a framework (as a URL, document, or description), I will map all skills
> to that framework instead."

### Step 3 — If the user provides a framework
1. Parse the user-provided framework (document, URL, or description)
2. Extract: skill categories, level definitions, competency codes (if any)
3. Map all resume skills to the user-provided framework
4. **Clearly state in the resume:** "Skills evaluated per: [Framework Name] ([source])"

### Step 4 — If the user does not provide a framework
1. Use the Universal Proficiency Levels (Section 12) for all skills
2. **Clearly state in the resume:** "Skills evaluated per: Universal Proficiency Levels
   (no industry-specific framework applied)"

### Mandatory disclosure
Every resume MUST include a **Framework Attribution** line in the Skills section header:

```
**Skills evaluated per:** [Framework Name] ([reference URL or "provided by user" or
"universal proficiency levels"])
```

This ensures transparency — any reader of the resume knows exactly which standard was used
to assess skill levels.

---

## Section 14 — Public Review & Global Acceptance Roadmap

To gain global recognition and adoption, the Autonomyx Skills Framework mapping should be
published for public review across multiple channels — standards bodies, open-source
communities, professional associations, and academic/government institutions.

### Tier 1 — Standards Bodies & Formal Standardization

These organizations can formally adopt or endorse the framework as a standard.

| Organization | What to submit | URL | Why |
|---|---|---|---|
| **IEEE Standards Association** | Propose as an IEEE standard for cross-framework skill interoperability (IEEE-SA New Standards) | https://standards.ieee.org/develop/ | IEEE standards carry global weight in technology; path to ISO adoption |
| **ISO / IEC JTC 1 SC 36** (IT for Learning, Education, and Training) | Submit as a Technical Report or International Standard draft under SC 36 WG | https://www.iso.org/committee/45392.html | ISO standards are the gold standard for global acceptance; SC 36 covers competency frameworks |
| **W3C Credentials Community Group** | Propose as a companion spec to W3C Verifiable Credentials for skill representation | https://www.w3.org/community/credentials/ | Aligns with the VC-based resume approach; W3C specs become web standards |
| **IMS Global / 1EdTech** | Submit as an extension to Open Badges 3.0 / Comprehensive Learner Record (CLR) | https://www.1edtech.org/standards | 1EdTech standards are widely adopted in education and credentialing |
| **HR Open Standards Consortium** | Propose as a skill classification extension to HR-XML / HR Open | https://www.hropenstandards.org/ | HR Open standards are used by ATS systems, HRIS platforms, and job boards globally |
| **European Committee for Standardization (CEN)** | Submit as a European Norm (EN) via CEN Workshop Agreement (CWA) | https://www.cen.eu/ | Fast-track to EU-wide adoption; aligns with e-CF which is already a CEN standard |

### Tier 2 — Open Source & Developer Community

These platforms reach practitioners, tool builders, and the open-source community.

| Platform | What to publish | URL | Why |
|---|---|---|---|
| **GitHub (public repo)** | Open-source the full framework as a versioned specification with JSON-LD schema, contribution guidelines, and RFC process | https://github.com | De facto standard for open-source collaboration; enables community PRs, issues, and forks |
| **Schema.org** | Propose extensions to `schema.org/Occupation`, `schema.org/EducationalOccupationalCredential` for framework-mapped skills | https://schema.org/docs/extension.html | Schema.org markup is used by Google, LinkedIn, and job platforms for structured data |
| **JSON-LD / Linked Open Data** | Publish the framework as a linked data vocabulary (JSON-LD context file) at a persistent URI | https://json-ld.org | Makes the framework machine-readable and linkable; enables semantic web interoperability |
| **ESCO (European Skills, Competences, Qualifications, and Occupations)** | Submit cross-walk mappings between Autonomyx framework codes and ESCO skills taxonomy | https://esco.ec.europa.eu/ | ESCO is the EU's multilingual skills classification; mapping to it enables EU-wide adoption |
| **O*NET (US Department of Labor)** | Submit cross-walk mappings to O*NET-SOC occupations and skills | https://www.onetonline.org/ | O*NET is the US standard for occupational information; used by job boards and government |

### Tier 3 — Professional Associations & Industry Bodies

These organizations represent the professions whose frameworks we reference. Engagement
ensures accuracy and endorsement.

| Organization | Action | URL |
|---|---|---|
| **SFIA Foundation** | Request formal partnership/endorsement; contribute cross-framework mapping back to SFIA ecosystem | https://sfia-online.org/en/about-sfia/sfia-foundation |
| **PMI (Project Management Institute)** | Submit framework mapping for PMI Talent Triangle alignment review | https://www.pmi.org |
| **ISACA** | Align with COBIT/CISA/CRISC competency models; submit for ISACA review | https://www.isaca.org |
| **CFA Institute** | Request review of CFA BoK mapping accuracy | https://www.cfainstitute.org |
| **SHRM** | Submit for SHRM competency model alignment review | https://www.shrm.org |
| **CIPD** | Submit for Profession Map alignment review | https://www.cipd.org |
| **CNCF / Linux Foundation** | Propose as a skills taxonomy for cloud-native certifications | https://www.cncf.io |
| **World Economic Forum (WEF)** | Submit for inclusion in WEF's "Future of Jobs" skills taxonomy and reskilling initiatives | https://www.weforum.org/communities/future-of-jobs/ |

### Tier 4 — Academic & Research Community

Peer-reviewed publication establishes academic credibility.

| Venue | What to submit | Why |
|---|---|---|
| **arXiv (cs.CY / cs.SE)** | Preprint paper describing the framework, cross-walk methodology, and validation | Immediate open-access visibility in the CS research community |
| **ACM Computing Surveys** | Survey paper on professional skills framework interoperability | High-impact journal; positions the work as a scholarly contribution |
| **IEEE Access** | Open-access journal paper on cross-framework skill mapping with VC integration | IEEE journal with global reach; fast review process |
| **European Conference on Technology Enhanced Learning (EC-TEL)** | Conference paper on competency framework harmonization | Leading European conference on education technology |
| **OECD Skills Studies** | Policy brief on standardized skills classification for international labor mobility | OECD publications influence national education and employment policies |

### Tier 5 — Government & Policy

Government adoption drives legal weight and institutional use.

| Body | Action | Why |
|---|---|---|
| **European Commission (DG EMPL)** | Submit as input to Europass Digital Credentials framework and European Digital Identity Wallet | EU policy mandates interoperable digital credentials by 2026; framework mapping is directly relevant |
| **US Department of Labor (ETA)** | Submit as companion to O*NET and Registered Apprenticeship skills standards | DOL adoption would embed the framework in US workforce development |
| **UK Government (Department for Education)** | Submit as alignment resource for UK's Skills Framework for the Digital Economy | UK actively developing digital skills standards post-SFIA |
| **Singapore SkillsFuture** | Submit cross-walk to Singapore's Skills Framework | Singapore is a global leader in national skills frameworks |
| **India NSQF (National Skills Qualifications Framework)** | Submit mapping to NSQF levels | India's massive workforce development programs need interoperable frameworks |
| **Australia AQF (Australian Qualifications Framework)** | Submit mapping to AQF levels | Aligns with Australia's vocational and higher education system |

### Tier 6 — Industry Platforms & Job Boards

These platforms reach employers and job seekers directly.

| Platform | Integration opportunity | Why |
|---|---|---|
| **LinkedIn** | Propose as skills taxonomy partner; integrate framework codes into LinkedIn Skills endorsements | 900M+ users; LinkedIn skill endorsements could map to framework levels |
| **Indeed / Glassdoor** | Submit framework for structured job posting skill requirements | Largest job boards; structured skills improve matching |
| **Workday / SAP SuccessFactors** | Partner for HRIS skills module integration | Enterprise HR platforms define how skills are managed at scale |
| **Credly / Acclaim** | Map Credly badges to framework codes and levels | Credly is the leading digital credentialing platform |
| **Coursera / edX / Udacity** | Map course completions to framework skill codes and levels | Learning platforms can issue framework-aligned credentials |

### Tier 7 — Top Educational Institutions (Academic Review Panel)

Engage top global universities and research institutes to **review, validate, and endorse**
the framework. Academic endorsement provides intellectual credibility and research rigor.

| Institution | Department / Lab | Why | Role |
|---|---|---|---|
| **MIT** (CSAIL / Media Lab / Sloan) | US | Leading in AI, skills tech, future of work research | Framework review + CS/AI skill taxonomy validation |
| **Harvard** (HBS / Kennedy School / SEAS) | US | Leadership in management, public policy, and education research | Business/management skill framework review |
| **Stanford** (HAI / GSB / CS) | US | AI ethics, human-centered AI, entrepreneurship | AI/ML skill taxonomy + ethics framework review |
| **Carnegie Mellon** (SCS / Heinz) | US | CS education research, skills assessment, HCI | Technical skills assessment methodology review |
| **IIT Bombay** (CS / IDC / SOM) | India | India's premier engineering institute; bridges India's massive talent ecosystem | Engineering + design skill framework review; India regional validation |
| **IIT Delhi** (CS / AI) | India | Strong AI/ML research; policy influence in India | AI skill taxonomy review; Indian IT workforce alignment |
| **IIT Madras** (CS / Data Science) | India | Pioneer in online degrees (BS Data Science); NPTEL leader | Data science framework review; online credential validation |
| **IIM Ahmedabad** | India | Top management research; shapes Indian business education | Management/leadership skill framework review |
| **IIM Bangalore** | India | Analytics and IT management focus; edX partnership | Business analytics framework review |
| **IIM Calcutta** | India | Finance and economics research leadership | Finance skill framework review |
| **ISB** (Indian School of Business) | India | Bridges global and Indian management practice | Cross-cultural management skills review |
| **University of Oxford** (CS / Said / Blavatnik) | UK | Policy, AI ethics, governance research | Public policy + ethics review |
| **University of Cambridge** (CS / Judge) | UK | Engineering, business, interdisciplinary research | Cross-domain framework validation |
| **LSE** (London School of Economics) | UK | Economics, social sciences, labor markets | Economics/social science framework review |
| **ETH Zurich** | Switzerland | Engineering, CS, precision sciences | Engineering skill taxonomy review |
| **NUS** (National University of Singapore) | Singapore | Asian skills ecosystem, future workforce research | Asia-Pacific regional validation |
| **Tsinghua University** | China | Engineering, AI, China's tech ecosystem | China regional validation |
| **University of Toronto** (Vector Institute) | Canada | Deep learning research | ML/AI skill taxonomy review |
| **INSEAD** | France/Singapore | International business, cross-cultural management | Global management skills review |
| **Max Planck Institutes** | Germany | ML, cognitive science, fundamental research | Research methodology review |

### Tier 8 — Top Companies (Industry Review Panel)

Engage leading global companies to **review and validate** the framework against real-world
hiring practices, internal competency models, and workforce planning needs.

#### Technology
| Company | Why | Review focus |
|---|---|---|
| **Google** | Defines hiring bars for engineering globally; internal skills framework (L3–L11) | Engineering levels, AI/ML skills, SWE competencies |
| **Microsoft** | Career framework used by 200K+ employees; Azure certifications ecosystem | Engineering career ladder validation; certification alignment |
| **Amazon / AWS** | Leadership Principles + technical bar; AWS certification ecosystem | Leadership competency validation; cloud skills taxonomy |
| **Apple** | Hardware + software + design integration; secretive but influential | Design + engineering cross-domain skills |
| **Meta** | Engineering levels, AI research, VR/AR skills | AI/ML skills, engineering levels validation |
| **Netflix** | Culture-driven competency model; no formal levels | Behavioral/culture-fit skill validation |
| **Salesforce** | Trailhead credentials ecosystem; admin/developer certification paths | CRM/SaaS skill taxonomy; gamified credential validation |
| **NVIDIA** | GPU/AI infrastructure; defines AI hardware skills | AI infrastructure skill taxonomy |
| **Infosys** | 300K+ employees; large-scale skills transformation programs | IT services skill framework; India workforce validation |
| **TCS** (Tata Consultancy Services) | 600K+ employees; internal competency frameworks | Large-scale IT workforce skills validation |
| **Wipro** | Digital transformation skills programs | IT consulting skill taxonomy |
| **HCLTech** | Engineering and IT services; Mode 1/2/3 framework | Engineering services skill validation |

#### Finance
| Company | Why | Review focus |
|---|---|---|
| **Goldman Sachs** | Defines finance hiring standards globally | Finance/quant skill taxonomy |
| **JPMorgan Chase** | Massive tech + finance workforce; internal academy | Fintech + banking skill framework |
| **BlackRock** | Investment management + Aladdin platform | Investment/risk management skills |
| **HDFC Bank / ICICI Bank** | India's leading private banks; large talent pools | Banking/finance skills; India regional validation |

#### Consulting
| Company | Why | Review focus |
|---|---|---|
| **McKinsey & Company** | Defines consulting competency standards | Strategy/consulting skill taxonomy |
| **BCG** (Boston Consulting Group) | Strategy + digital transformation | Digital transformation skills |
| **Deloitte** | Audit, consulting, tech advisory; internal competency models | Cross-functional professional skills |
| **Accenture** | 700K+ employees; massive skills transformation investment | IT/consulting skill framework at scale |

#### Design & Creative
| Company | Why | Review focus |
|---|---|---|
| **IDEO** | Defines design thinking methodology globally | Design/innovation skill taxonomy |
| **Figma / Adobe** | Design tools that shape the profession | Design tool proficiency standards |
| **Frog Design** | Strategic design consulting | Design strategy skills |

#### Healthcare & Pharma
| Company | Why | Review focus |
|---|---|---|
| **Johnson & Johnson** | Global healthcare leader; R&D competency models | Healthcare/pharma skill taxonomy |
| **Pfizer** | Biotech/pharma R&D and commercialization | Biotech skill framework |
| **Apollo Hospitals / Fortis** | India's largest hospital networks | Healthcare skills; India regional validation |

#### Manufacturing & Engineering
| Company | Why | Review focus |
|---|---|---|
| **Siemens** | Industry 4.0 skills pioneer; Siemens Xcelerator | Industrial/manufacturing skill taxonomy |
| **Bosch** | Engineering + IoT; strong competency frameworks | Engineering skill validation |
| **Tata Group** | India's largest conglomerate; multi-industry | Cross-industry skills; India regional validation |
| **Reliance Industries** | India's largest company; digital + energy + retail | Diversified skill taxonomy; India validation |

### Recommended Adoption Sequence

1. **Immediate (Month 1–2):**
   - Open-source on GitHub with RFC process and contribution guidelines
   - Publish JSON-LD vocabulary at persistent URI
   - Submit **arXiv preprint** (self-publish, live in 24 hours, no review gate)
   - Submit **IEEE Access paper** (open-access journal, fast peer review ~4–8 weeks)
   - Reach out to SFIA Foundation for partnership discussion
   - **Invite 3–5 academic reviewers** from Tier 7 institutions (start with MIT, IIT Bombay,
     Oxford, IIM Ahmedabad) to review the preprint and provide feedback

2. **Short-term (Month 3–6):**
   - Submit Schema.org extension proposal
   - Engage W3C Credentials Community Group
   - Submit cross-walks to ESCO and O*NET
   - Present at 1–2 industry conferences (EC-TEL, SkillsX)
   - Engage WEF Future of Jobs initiative
   - Submit to **ACM Computing Surveys** (longer review cycle but high-impact)
   - **Form Academic Advisory Board** from Tier 7 institutions (target 10–15 faculty members
     across CS, business, design, healthcare, social sciences)
   - **Engage 5–10 companies** from Tier 8 for industry validation (start with Google,
     Microsoft, Infosys, McKinsey, Deloitte — they have public competency frameworks to
     cross-reference)

3. **Medium-term (Month 6–12):**
   - Submit **CEN Workshop Agreement** proposal (fast-track European norm)
   - Submit **IEEE-SA new standard proposal** (begins the formal standards process —
     this is the multi-year standardization track, distinct from IEEE Access journal
     publication which is already done in Step 1)
   - Engage professional associations (SFIA, PMI, ISACA) for endorsement
   - Partner with 1–2 credentialing platforms (Credly, Open Badges)
   - **Publish joint papers** with academic review board members
   - **Pilot with 2–3 companies** from Tier 8 — validate framework against their
     internal competency models and hiring rubrics

4. **Long-term (Year 1–3):**
   - **IEEE-SA standard ratification** (working group ballots, public comment, revision)
   - **ISO/IEC JTC 1 SC 36** standard submission (builds on IEEE-SA and CEN groundwork)
   - Government submissions (EU, US DOL, UK DfE, Singapore, India, Australia)
   - Enterprise HRIS integrations (Workday, SAP)
   - Job board integrations (LinkedIn, Indeed)
   - **Establish permanent Academic + Industry Review Council** with rotating membership
     from Tier 7 and Tier 8 organizations

**Note on IEEE — two distinct tracks:**
- **IEEE Access (journal)** = publish a peer-reviewed paper. Fast (~2 months). Done in Step 1.
- **IEEE-SA (standards body)** = get the framework adopted as a formal IEEE standard (like
  IEEE 802.11 for WiFi). Requires working group formation, drafting, balloting, and public
  comment. Takes 1–3 years. Starts in Step 3, ratified in Step 4.

Both are IEEE, but journal publication is academic visibility while standards adoption is
industry-binding authority.

---

## Section 15 — Verifier Credibility Hierarchy

Skills can be verified by **anyone** — but the credibility of the verification depends on
**who** verifies it. This section defines the trust hierarchy for skill verification sources.

### The Fundamental Rule: Publicly Verifiable = No Verification Needed

**Publicly verifiable information holds the utmost authority and requires NO third-party
verification.** If anyone can independently confirm a claim by visiting a public URL or
querying a public database, the claim is self-evident.

| Publicly verifiable source | What it proves | Why no verification needed |
|---|---|---|
| **Public GitHub repos** | Code authored, languages used, contribution history | Anyone can view the code, commits, and authorship |
| **Published papers** (Google Scholar, arXiv, IEEE Xplore, PubMed) | Research authored, expertise demonstrated | Papers are publicly indexed with author attribution |
| **Granted patents** (Google Patents, USPTO, EPO) | Inventions, technical innovation | Patent databases are public records |
| **Published npm / PyPI packages** | Open-source authorship, package usage stats | Package registries are public with download counts |
| **Stack Overflow profile** | Community reputation, expertise areas | Reputation scores and answers are publicly visible |
| **Docker Hub images** | Container authorship, pull counts | Public registry with usage stats |
| **Published articles** (Dev.to, Medium, personal blog) | Writing ability, domain knowledge | Articles are publicly accessible |
| **Credly badges (public profile)** | Certification status | Credly profiles are publicly verifiable |
| **Open-source contributions** (merged PRs, issues) | Collaboration, technical skill | Git history is immutable and public |
| **Public speaking** (YouTube, conference sites) | Presentation skills, thought leadership | Videos and speaker listings are public |
| **Published books** (ISBN records) | Authorship, expertise | ISBN databases are public |

**Rule:** When a skill claim is backed by publicly verifiable evidence, mark it in the
resume Proof column as the direct source (e.g., "GitHub: 15 repos") — NOT as "Verified by"
anyone. The public record IS the verification.

### Verifier Credibility Tiers

For skills that are NOT publicly verifiable (e.g., internal project work, team leadership,
soft skills, proprietary domain expertise), the credibility of verification depends on the
verifier. Anyone can verify a skill, but the weight differs:

| Tier | Verifier type | Credibility | Example | Resume label |
|---|---|---|---|---|
| **S — Self-Evident** | Public record (no verifier needed) | Absolute | GitHub repo, published paper, granted patent | `GitHub: 15 repos` / `Patent US12345` |
| **A — Institutional** | Accredited university, government body, standards organization | Highest | MIT degree, CFA Institute certification, government license | `Verified by [Institution]` |
| **B — Employer** | Current or former employer (HR department, manager with authority) | Very High | Employment VC from Acme Corp HR, signed reference letter | `Verified by [Company] HR` |
| **C — Industry Certification Body** | Recognized certification authority (not the employer) | High | AWS (Amazon), CNCF, PMI, Cisco, Microsoft | `Certified by [Body]` |
| **D — Assessment Platform** | Independent testing/assessment service | Medium-High | HackerRank, Pluralsight IQ, Codility, StrengthsFinder | `Assessed by [Platform] (Score: X)` |
| **E — Professional Peer** | Named colleague, manager, or client with verifiable identity | Medium | LinkedIn recommendation, signed peer endorsement, VC from named individual | `Endorsed by [Name, Title at Company]` |
| **F — Community** | Aggregated community signal (not a single named individual) | Medium-Low | Stack Overflow reputation, GitHub stars, social proof at scale | `Community: [metric]` |
| **G — Self-Reported** | The individual themselves (no external verification) | Lowest | User's own description of skills and experience | `Self-reported (unverified)` |

### Credibility Combinatorics

Multiple lower-tier verifications can strengthen credibility:
- **E + E + F** (2 peer endorsements + community signal) ≈ **C** (certification-level credibility)
- **D + F** (assessment score + community reputation) ≈ **C**
- **G alone** (self-reported only) = always remains **G** — no number of self-reports increases credibility
- **S** (self-evident) always supersedes all other tiers — it cannot be questioned

### How Credibility Affects the Resume

In the Skills table Proof column, always include the verifier tier:

```
| Python | SFIA:PROG — Level 5 | Expert | [S] GitHub: 15 repos, 2K+ commits; [C] Certified by AWS (Developer Associate) |
| Leadership | — | Advanced | [B] Verified by Acme Corp HR (EmploymentCredential VC); [E] Endorsed by Jane Doe, VP Engineering |
| React | SFIA:PROG — Level 4 | Advanced | [S] GitHub: 8 repos; [F] Stack Overflow: top 5% tag; [D] HackerRank 95/100 |
| Project Management | IPMA:ICB4 — C | Intermediate | [C] Certified by PMI (PMP); [G] Self-reported: led 5 projects |
| Negotiation | — | Intermediate | [G] Self-reported (unverified) |
```

The tier label `[S]`, `[A]`, `[B]`, etc. immediately tells the reader how trustworthy each
proof point is.

---

## Section 16 — Top Educational Institutions Directory

A reference directory of globally recognized educational institutions organized by discipline.
Used by the `autonomyx-skill-score` skill to:
1. **Assess credential weight** — degrees from top-tier institutions carry stronger signal
2. **Guide verification** — identify which institutions offer digital/verifiable credentials
3. **Enrich the Education section** — add institutional reputation context when relevant

### How to use this directory

When generating a resume:
- If a person's degree is from a listed institution, the Education section MAY note the
  institution's global standing (e.g., "IIT Bombay — India's premier engineering institute")
  only if the user requests it or if the resume targets international audiences who may not
  recognize the institution
- When encouraging credential verification (Step 6), reference whether the institution
  offers digital credentials
- Never rank or compare institutions in the resume itself — simply present the degree factually

### Institution Tier Definitions

| Tier | Criteria |
|---|---|
| **Tier 1 — Global Elite** | Consistently ranked in top 10–20 globally across multiple ranking systems (QS, THE, ARWU, US News). Universally recognized by name. |
| **Tier 2 — World-Class** | Ranked in top 50–100 globally. Widely recognized internationally in their domain. |
| **Tier 3 — Nationally Premier** | Top institution(s) in their country for a specific discipline. May not be globally ranked but carry enormous weight domestically and regionally. |

---

### Technology & Engineering

#### Tier 1 — Global Elite
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **MIT** (Massachusetts Institute of Technology) | US | CS, AI, Engineering, Robotics | MIT Digital Diplomas (blockchain-based); MITx certificates via edX |
| **Stanford University** | US | CS, AI, Entrepreneurship, Engineering | Stanford Online certificates; Coursera partnership |
| **Caltech** (California Institute of Technology) | US | Engineering, Physics, Space Science | — |
| **Carnegie Mellon University** | US | CS, AI, Robotics, HCI | CMU digital certificates |
| **ETH Zurich** | Switzerland | Engineering, CS, Physics | ETH digital credentials |
| **University of Cambridge** | UK | Engineering, CS, Mathematics | Cambridge digital verification |
| **University of Oxford** | UK | CS, Engineering, Mathematics | Oxford digital certificates |
| **Imperial College London** | UK | Engineering, CS, Data Science | Imperial digital credentials |
| **NUS** (National University of Singapore) | Singapore | CS, Engineering, AI | NUS digital certificates via OpenCerts |
| **Tsinghua University** | China | Engineering, CS, AI | — |

#### Tier 2 — World-Class
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **UC Berkeley** | US | CS, AI, EECS | Berkeley digital certificates |
| **Georgia Tech** | US | CS, Engineering, Cybersecurity | GT digital badges via Credly |
| **University of Toronto** | Canada | AI/ML (deep learning pioneer), CS | UofT certificates |
| **TU Munich** | Germany | Engineering, CS, Automotive | — |
| **EPFL** (Swiss Federal Institute of Technology) | Switzerland | Engineering, CS, Robotics | EPFL digital certificates via edX |
| **University of Tokyo** | Japan | Engineering, Robotics, Materials | — |
| **KAIST** | South Korea | Engineering, AI, Semiconductors | — |
| **Technion** | Israel | Engineering, CS, Cybersecurity | — |
| **University of Waterloo** | Canada | CS, Engineering, Co-op | — |
| **TU Delft** | Netherlands | Engineering, Aerospace, Data Science | TU Delft certificates via edX |

#### Tier 3 — Nationally Premier (India)
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **IIT Bombay** | India | CS, Engineering, Entrepreneurship | IIT Bombay digital certificates via NPTEL/Swayam |
| **IIT Delhi** | India | CS, Engineering, AI | NPTEL/Swayam certificates |
| **IIT Madras** | India | CS, Data Science, Engineering | IIT Madras Online Degree (BS in Data Science); NPTEL |
| **IIT Kanpur** | India | CS, Engineering, Mathematics | NPTEL certificates |
| **IIT Kharagpur** | India | Engineering, CS, Management | NPTEL certificates |
| **IIT Roorkee** | India | Civil, Engineering, CS | NPTEL certificates |
| **IIT Hyderabad** | India | AI/ML, Engineering, Biomedical | NPTEL certificates |
| **IIT Guwahati** | India | Engineering, Design, CS | NPTEL certificates |
| **IIIT Hyderabad** | India | CS, AI, NLP, Data Science | — |
| **BITS Pilani** | India | Engineering, CS, Pharmacy | BITS online degrees |
| **NIT Trichy** | India | Engineering, CS | — |
| **ISI Kolkata** (Indian Statistical Institute) | India | Statistics, Data Science, Mathematics | — |

---

### Business & Management

#### Tier 1 — Global Elite
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Harvard Business School** | US | MBA, General Management, Leadership | HBS Online certificates; Harvard digital credentials |
| **Stanford GSB** (Graduate School of Business) | US | MBA, Entrepreneurship, Innovation | Stanford Online certificates |
| **Wharton** (University of Pennsylvania) | US | MBA, Finance, Analytics | Wharton Online certificates via Coursera |
| **INSEAD** | France/Singapore | MBA, International Business | INSEAD certificates |
| **London Business School** | UK | MBA, Finance, Strategy | LBS digital certificates |
| **MIT Sloan** | US | MBA, Technology Management, Analytics | MIT Sloan Executive Education certificates |
| **Columbia Business School** | US | MBA, Finance, Value Investing | Columbia digital certificates |
| **Chicago Booth** | US | MBA, Finance, Economics | Booth digital certificates |
| **Kellogg** (Northwestern) | US | MBA, Marketing, Management | Kellogg certificates |
| **HEC Paris** | France | MBA, Strategy, Luxury Management | HEC certificates via Coursera |

#### Tier 2 — World-Class
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Yale SOM** | US | MBA, Social Enterprise, Leadership | — |
| **NYU Stern** | US | MBA, Finance, Fintech | — |
| **Berkeley Haas** | US | MBA, Entrepreneurship, Social Impact | — |
| **IE Business School** | Spain | MBA, Entrepreneurship, Digital | IE certificates |
| **Cambridge Judge** | UK | MBA, Entrepreneurship | — |
| **Oxford Said** | UK | MBA, Finance, Social Enterprise | — |
| **NUS Business School** | Singapore | MBA, Asian Business | — |
| **Melbourne Business School** | Australia | MBA, General Management | — |
| **Rotman** (University of Toronto) | Canada | MBA, Finance, Design Thinking | — |
| **CEIBS** (China Europe International Business School) | China | MBA, China Business | — |

#### Tier 3 — Nationally Premier (India)
| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **IIM Ahmedabad** | India | MBA (PGDM), Strategy, Entrepreneurship | IIM-A executive education certificates |
| **IIM Bangalore** | India | MBA (PGDM), Analytics, IT Management | IIM-B certificates via edX |
| **IIM Calcutta** | India | MBA (PGDM), Finance, Economics | IIM-C certificates |
| **IIM Lucknow** | India | MBA (PGDM), Operations, HR | — |
| **IIM Kozhikode** | India | MBA (PGDM), Marketing, Finance | — |
| **IIM Indore** | India | MBA (PGDM), HR, Marketing | — |
| **ISB** (Indian School of Business) | India | MBA (PGP), Finance, Analytics, Entrepreneurship | ISB certificates via Coursera |
| **XLRI Jamshedpur** | India | MBA, HR, Industrial Relations | — |
| **FMS Delhi** | India | MBA, Finance, Marketing | — |
| **SP Jain** (SPJIMR Mumbai) | India | MBA, General Management, Family Business | — |

---

### Computer Science & AI (Specialized)

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **MIT CSAIL** | US | AI, Robotics, Systems, Theory | MITx certificates |
| **Stanford AI Lab (SAIL)** | US | Deep Learning, NLP, Computer Vision | Stanford Online |
| **CMU School of Computer Science** | US | ML, Robotics, HCI, Security | CMU certificates |
| **UC Berkeley EECS** | US | AI, Systems, Theory | Berkeley certificates |
| **University of Washington** | US | NLP, Systems, HCI | — |
| **University of Montreal / Mila** | Canada | Deep Learning (Bengio), Reinforcement Learning | — |
| **University of Toronto / Vector Institute** | Canada | Deep Learning (Hinton), ML | — |
| **University of Edinburgh** | UK | NLP, AI, Informatics | Edinburgh certificates |
| **Max Planck Institutes** | Germany | ML, Computer Vision, Robotics | — |
| **IIT Bombay (CS Department)** | India | Systems, AI, Theory | NPTEL |
| **IIT Delhi (CS Department)** | India | AI, Data Science, Networks | NPTEL |
| **IIIT Hyderabad** | India | NLP, Computer Vision, AI | — |

---

### Finance & Economics

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Wharton** (UPenn) | US | Finance, Accounting, Real Estate | Wharton Online via Coursera |
| **Chicago Booth** | US | Finance, Economics, Quantitative Methods | — |
| **London School of Economics (LSE)** | UK | Economics, Finance, Public Policy | LSE Online certificates |
| **MIT Sloan** | US | Financial Engineering, Fintech | MITx certificates |
| **Columbia Business School** | US | Value Investing, Financial Economics | — |
| **NYU Stern** | US | Finance, Fintech, Risk Management | — |
| **London Business School** | UK | Finance, Private Equity | — |
| **Bocconi University** | Italy | Finance, Economics, Management | Bocconi certificates via Coursera |
| **IIM Ahmedabad** | India | Finance, Capital Markets | — |
| **IIM Calcutta** | India | Finance, Economics | — |

---

### Data Science & Analytics

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **MIT** | US | Data Science, Statistics, ML | MITx MicroMasters in Statistics & Data Science |
| **Stanford** | US | ML, AI, Statistical Learning | Stanford Online certificates |
| **CMU** | US | ML, Statistics, Computational Methods | CMU certificates |
| **UC Berkeley** | US | Data Science, Statistics | Berkeley MicroMasters via edX |
| **Harvard** | US | Biostatistics, Data Science | HarvardX certificates |
| **University of Michigan** | US | Data Science, Applied Statistics | UMich certificates via Coursera |
| **Imperial College London** | UK | Data Science, Machine Learning | Imperial certificates via Coursera |
| **ETH Zurich** | Switzerland | Statistics, Data Science | — |
| **ISI Kolkata** | India | Statistics, Data Science, Mathematics | — |
| **IIT Madras** | India | Online BS in Data Science (pioneering) | IIT-M Online Degree credentials |
| **IIM Bangalore** | India | Business Analytics | IIM-B certificates via edX |

---

### Design & Creative

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Rhode Island School of Design (RISD)** | US | Industrial Design, Graphic Design | — |
| **Parsons School of Design** | US | Fashion, Digital Design | — |
| **Royal College of Art** | UK | Design, Innovation | — |
| **ArtCenter College of Design** | US | Product Design, Transportation Design | — |
| **Aalto University** | Finland | Design, Architecture, Arts + Technology | — |
| **MIT Media Lab** | US | Interaction Design, Creative Technology | — |
| **IIT Bombay (IDC School of Design)** | India | Industrial Design, UX, Interaction Design | — |
| **NID Ahmedabad** (National Institute of Design) | India | Product Design, Communication Design | — |
| **Srishti Manipal** | India | Design, Art, Technology | — |
| **Copenhagen Institute of Interaction Design (CIID)** | Denmark | Interaction Design, Service Design | — |

---

### Medicine & Healthcare

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Harvard Medical School** | US | Medicine, Biomedical Research | HarvardX health certificates |
| **Johns Hopkins University** | US | Public Health, Medicine, Biomedical Engineering | JHU certificates via Coursera |
| **Stanford Medicine** | US | Biomedical Informatics, AI in Healthcare | — |
| **University of Oxford (Medical Sciences)** | UK | Clinical Medicine, Genomics | — |
| **Karolinska Institute** | Sweden | Medicine, Biomedical Research (Nobel) | — |
| **AIIMS Delhi** | India | Medicine, Medical Research | — |
| **CMC Vellore** | India | Medicine, Community Health | — |
| **JIPMER Puducherry** | India | Medicine, Research | — |
| **University of Tokyo (Medicine)** | Japan | Medicine, Biomedical Engineering | — |
| **NUS Yong Loo Lin School of Medicine** | Singapore | Medicine, Translational Research | — |

---

### Law

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Harvard Law School** | US | Corporate Law, Constitutional Law | HarvardX certificates |
| **Yale Law School** | US | Constitutional Law, Public Interest | — |
| **Stanford Law School** | US | Technology Law, IP, Entrepreneurship | — |
| **University of Oxford (Law)** | UK | International Law, Jurisprudence | — |
| **University of Cambridge (Law)** | UK | Commercial Law, International Law | — |
| **Columbia Law School** | US | Corporate Law, International Law | — |
| **NYU School of Law** | US | Tax Law, International Law | — |
| **NLS Bangalore** (National Law School) | India | Constitutional Law, Corporate Law | — |
| **NALSAR Hyderabad** | India | IP Law, International Law | — |
| **NLU Delhi** | India | Corporate Law, Policy | — |

---

### Public Policy & Social Sciences

| Institution | Country | Known for | Digital credentials |
|---|---|---|---|
| **Harvard Kennedy School** | US | Public Policy, Governance, Leadership | HKS Executive Education certificates |
| **LSE** (London School of Economics) | UK | Economics, Political Science, Sociology | LSE Online certificates |
| **Sciences Po** | France | Political Science, International Relations | Sciences Po certificates via Coursera |
| **Princeton (Woodrow Wilson School)** | US | Public Policy, Economics | — |
| **Georgetown SFS** | US | International Relations, Diplomacy | — |
| **University of Chicago (Harris School)** | US | Public Policy, Data Analytics | — |
| **TISS Mumbai** (Tata Institute of Social Sciences) | India | Social Work, Public Policy, HR | — |
| **JNU** (Jawaharlal Nehru University) | India | Social Sciences, International Relations | — |
| **Ashoka University** | India | Liberal Arts, Social Sciences, Economics | — |
| **NUS Lee Kuan Yew School** | Singapore | Public Policy, Asian Governance | — |

---

### Online Education Platforms (Cross-Discipline)

These platforms partner with top institutions to issue verifiable credentials at scale.

| Platform | Credential type | Institutional partners | Verification |
|---|---|---|---|
| **Coursera** | Certificates, Professional Certificates, Degrees | Stanford, Wharton, Google, IBM, IIMs, ISB | Coursera verified certificates; shareable on LinkedIn |
| **edX** | MicroMasters, Professional Certificates, Degrees | MIT, Harvard, Berkeley, IIM-B, TU Delft | edX verified certificates |
| **Udacity** | Nanodegrees | Industry partners (Google, AWS, Mercedes) | Udacity certificates |
| **NPTEL / Swayam** | Certificates, Online Degrees | IITs, IIMs, IISc, NITs (India) | NPTEL certificates with proctored exams |
| **FutureLearn** | Certificates, Microcredentials, Degrees | King's College, Monash, Deakin | FutureLearn certificates |
| **Simplilearn / UpGrad / Great Learning** | PG Programs, Certificates | IIT, IIIT, IIM partners (India) | Platform-issued certificates |
| **LinkedIn Learning** | Certificates | LinkedIn in-house content | LinkedIn profile badges |
| **Google Career Certificates** | Professional Certificates | Google | Credly badges |
| **AWS Training & Certification** | Certifications | Amazon | Credly badges; AWS verification |
| **Microsoft Learn** | Certifications | Microsoft | Credly badges; MS Learn verification |

---

### Using Institutional Data in Resumes

**Rules:**
1. **Never rank institutions** in the resume — present degrees factually
2. **Add context for international audiences** only when requested:
   - "IIT Bombay (India's premier engineering institute, <1% acceptance rate)"
   - "IIM Ahmedabad (India's top-ranked business school)"
3. **Credential verification guidance**: When encouraging VC verification in Step 6, check
   if the institution offers digital credentials (marked in the tables above) and provide
   specific instructions:
   - "IIT Madras offers digital degree verification via NPTEL — check your alumni portal"
   - "Harvard offers digital diplomas — visit Harvard's credential verification page"
4. **Online credentials matter**: Courses and certificates from top platforms (Coursera/MIT,
   edX/Harvard, NPTEL/IIT) carry real weight and should be included in the Education or
   Certifications section, not dismissed as informal learning

---

Maintained by Autonomyx. Last updated: March 2026.
