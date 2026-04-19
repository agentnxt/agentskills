# Autonomyx Skill Evaluator: AI-Powered Professional Skills Assessment and Resume Generation

**White Paper v1.0 — March 2026**

**Authors:** Autonomyx Team

---

## Abstract

The professional resume remains the primary artifact in hiring, yet it is fundamentally broken. Resumes are self-reported, unverified, inconsistent in format, and disconnected from the professional standards that define competency. The Autonomyx Skill Evaluator addresses these problems by introducing an AI-driven system that aggregates professional data from multiple verified sources, maps every skill to internationally recognized competency frameworks, assigns credibility-tiered proof to each claim, and produces resumes optimized for 15 distinct target platforms. This white paper describes the architecture, methodology, and standards underpinning the system, and outlines a roadmap toward a future where professional credentials are portable, verifiable, and universally understood.

---

## 1. The Problem

### 1.1 Resumes Are Unverified

Over 78% of resumes contain some form of exaggeration or misrepresentation (HireRight, 2024). Employers have no standardized way to distinguish verified expertise from aspirational claims. Background checks verify employment dates and degree conferral but say nothing about actual skill proficiency.

### 1.2 Skills Lack a Common Language

When a candidate writes "proficient in Python," there is no shared understanding of what that means. Does it mean they completed a tutorial, or that they architect production ML pipelines? Without a common framework, skills claims are ambiguous and non-comparable across candidates.

### 1.3 Professional Data Is Fragmented and Ephemeral

A professional's evidence of competency is scattered across dozens of platforms — LinkedIn, GitHub, Stack Overflow, certification bodies, corporate Slack workspaces, email archives, patent databases, and publication indices. Worse, much of this data is locked inside corporate systems and becomes inaccessible when the individual changes jobs.

### 1.4 One Resume Does Not Fit All

A resume optimized for an Applicant Tracking System (ATS) differs fundamentally from a LinkedIn profile, a GitHub developer README, an academic CV, or a freelance platform overview. Professionals must maintain multiple versions manually, with no tooling to ensure consistency.

---

## 2. The Autonomyx Approach

The Autonomyx Skill Evaluator is a Claude Code skill — an AI-powered agent that operates within the Claude ecosystem — designed to solve each of these problems systematically.

### 2.1 Multi-Source Data Aggregation

Rather than relying on a single self-reported document, the system aggregates professional data from a comprehensive hierarchy of sources:

| Tier | Source Type | Examples | Data Quality |
|---|---|---|---|
| **Tier 1** | Identity & employment databases | Explorium prospect matching, LinkedIn | Structured employment history, education, demographics |
| **Tier 2** | Platform APIs | GitHub, Docker Hub, npm, PyPI, Stack Overflow, WordPress, Dev.to | Verified portfolio data, contribution metrics, community reputation |
| **Tier 3a** | Communication archives | Slack exports, email archives, Teams data, WhatsApp exports | Behavioral skill inference from interaction patterns |
| **Tier 3b** | Authored documents | Whitepapers, patents, research papers, blog posts, presentations | Domain expertise, technical depth, writing ability |
| **Tier 4** | Platforms without APIs | Google, Microsoft, Amazon certifications; screenshots; activity exports | Certification verification, achievement evidence |
| **Tier 5** | Web fallback | Any public profile page | Basic identity and portfolio extraction |

The system processes all provided sources, resolves identity across platforms, and merges the results into a unified professional profile. Conflicting data is resolved using a priority hierarchy: Verifiable Credentials > Platform API data > Explorium enrichment > Document inference > Communication inference > Self-reported data.

### 2.2 Professional Framework Mapping

Every skill identified is mapped to the internationally recognized competency framework appropriate to the individual's profession. The system currently supports 17 profession-specific frameworks:

| Domain | Framework | Governing Body |
|---|---|---|
| IT / Software / Digital | SFIA 9 | SFIA Foundation |
| Cybersecurity | NICE Workforce Framework (NIST SP 800-181r1) | NIST / CISA |
| Data Science / AI / ML | EDISON Data Science Framework (DS-BoK) | EDISON Project (EU) |
| Project Management | PMI Talent Triangle + IPMA ICB4 | PMI / IPMA |
| Finance / Accounting | CFA Body of Knowledge / ACCA Competency Framework | CFA Institute / ACCA |
| Marketing | CIM Professional Marketing Competencies | Chartered Institute of Marketing |
| Human Resources | SHRM Competency Model / CIPD Profession Map | SHRM / CIPD |
| Design / UX | UXPA Body of Knowledge / IxDA Competencies | UXPA / IxDA |
| Healthcare IT | AMIA Health Informatics Competencies | AMIA |
| Legal | SRA Competence Statement / ABA Competencies | SRA (UK) / ABA (US) |
| Supply Chain | ASCM (APICS) Body of Knowledge | ASCM |
| Engineering | UK-SPEC / EUR-ING Competence Standards | Engineering Council (UK) |
| Education | UNESCO ICT Competency Framework | UNESCO |
| Product Management | Pragmatic Institute Framework | Pragmatic Institute |
| Sales | MEDDIC/MEDDPICC + Sandler | Industry standard |
| General / Cross-functional | European e-Competence Framework (e-CF 4.0) | CEN |

For professionals who span multiple domains (e.g., a "Data Science Manager" who combines EDISON for data science skills and PMI for project management skills), the system applies multiple frameworks simultaneously.

A cross-framework level equivalence table ensures that proficiency levels are comparable across frameworks — a SFIA Level 5 maps to an IPMA Level B, a CFA Advanced, and a NICE Expert level.

### 2.3 Evidence-Based Proficiency Assessment

Skill levels are not self-reported. They are determined by the weight of evidence available from the aggregated data sources. The system uses a four-level proficiency scale (Expert, Advanced, Intermediate, Beginner) with explicit evidence thresholds:

**Expert** — Deep, authoritative command. Recognized by others in the field. 5+ years of sustained primary use. Evidence: top 1% Stack Overflow tag scores, 10+ major repositories, patents, published research, senior/lead role titles.

**Advanced** — Strong proficiency. Can architect, mentor, and handle complex problems. 3-5 years of regular use. Evidence: professional certifications (CKA, AWS SA Professional), 5+ repositories with significant commits, top 10% community tag scores.

**Intermediate** — Solid working knowledge. Can deliver independently. 1-3 years of use. Evidence: foundational certifications, 2+ repositories, articles authored on the topic.

**Beginner** — Foundational understanding. Can contribute with guidance. Evidence: 1-2 repository mentions, coursework, self-reported claims without corroboration.

The system always uses the highest level supported by available evidence and never over-claims.

### 2.4 Credibility-Tiered Proof

Each skill claim in the generated resume carries a credibility tier prefix, creating transparency about the strength of evidence behind every claim:

| Tier | Label | Source Type | Example |
|---|---|---|---|
| **[S]** | Self-evident | Publicly verifiable record (GitHub, patents, published articles) | `[S] GitHub: 15 repos, 2,400 commits` |
| **[A]** | Accredited institution | University, government body | `[A] Verified by MIT (MS Computer Science, 2020)` |
| **[B]** | Employer-verified | HR department, manager attestation | `[B] Verified by Acme Corp HR (Employment VC)` |
| **[C]** | Certified | Industry body, cryptographic VC | `[C] Certified by CNCF (CKA, Jan 2025)` |
| **[D]** | Assessed | Assessment platform score | `[D] Assessed by HackerRank (Score: 95/100)` |
| **[E]** | Endorsed | Named peer endorsement | `[E] Endorsed by Jane Doe, CTO at Beta Inc` |
| **[F]** | Inferred | Community signal, role inference, communication analysis | `[F] Inferred from role: "Engineering Manager" (3 years)` |
| **[G]** | Self-reported | User's own claim without corroboration | `[G] Self-reported (unverified)` |

A key design principle: **publicly verifiable information is Tier [S] and requires no further verification.** If anyone can confirm a claim by visiting a public URL, it is self-evident truth.

### 2.5 Behavioral and Soft Skills Assessment

Unlike traditional resume builders that focus exclusively on technical skills, the Autonomyx Skill Evaluator treats behavioral competencies with equal rigor. Leadership, communication, collaboration, mentoring, conflict resolution, and other interpersonal skills are identified from multiple evidence sources:

- **Role titles and tenure**: "Director" implies leadership scope; team size implies delegation
- **Communication archives** (with full anonymization): Language patterns in Slack, email, and meeting transcripts reveal collaboration styles, mentoring behavior, and decision-making patterns
- **Code review activity**: GitHub PR reviews demonstrate mentoring and knowledge sharing
- **Published writing**: Articles and talks demonstrate written communication
- **Career transitions**: Multiple industries or role types indicate adaptability

All communication analysis follows strict privacy protocols. Third-party PII is stripped. Names are replaced with anonymized labels. Only behavioral patterns are retained — never specific conversation content.

### 2.6 Platform-Specific Output Formatting

The system generates resumes optimized for 15 distinct target platforms:

1. **LinkedIn** — First-person, section-by-section, keyword-optimized for recruiter search
2. **Job boards** (Indeed, Glassdoor, Monster) — Plain text, keyword-dense, 1-2 pages
3. **ATS** (Workday, Greenhouse, Lever) — Single-column, no tables, standard headers, parseable
4. **PDF / Print** — Full-format with framework mapping and verification status
5. **Personal website** — HTML-ready with JSON-LD structured data (schema.org/Person)
6. **GitHub README** — Shield.io badges, contribution stats, repo-focused
7. **Behance / Dribbble** — Case study format, design process narrative
8. **Credly / credential wallet** — Skills-first, verification-focused
9. **Email to recruiter** — Cover note + ATS-optimized attachment
10. **Freelance platforms** (Upwork, Toptal) — Client-focused, outcome-oriented
11. **Academic CV** — Full citation format, publications-first, no page limit
12. **Government / public sector** — Detailed, competency-aligned, extended format
13. **Internal promotion** — Achievement-focused, growth-oriented, company-aligned
14. **Networking / conferences** — Concise, conversational, highlight-driven
15. **Multiple platforms** — Generates several versions simultaneously with comparison

Each format adapts not just the layout, but the tone, emphasis, content selection, and keyword strategy for the target context.

---

## 3. Verifiable Credentials: The Future of Professional Identity

### 3.1 The Data Portability Problem

When a professional leaves an employer, they lose access to the corporate systems that contain evidence of their work: Slack workspaces, internal Git repositories, Jira boards, email archives, CRM data, and performance reviews. This creates a "dark period" where substantial professional contributions become unprovable.

### 3.2 Verifiable Credentials as the Solution

Verifiable Credentials (VCs), as defined by the W3C standard, solve this problem by making professional data portable, tamper-proof, and individually owned. The Autonomyx Skill Evaluator natively supports:

- **W3C Verifiable Credentials** (JSON-LD)
- **JWT-encoded VCs**
- **SD-JWT** (Selective Disclosure JWT) — respecting holder disclosure choices
- **Open Badges v3** (aligned with W3C VC data model)
- **VC wallet integration** via DIDComm, OpenID4VP, and CHAPI protocols

The system maps VC types to resume sections:

| VC Type | Resume Section |
|---|---|
| EmploymentCredential | Experience |
| EducationCredential | Education |
| CertificationCredential | Certifications |
| SkillCredential / EndorsementCredential | Skills |
| AchievementCredential | Experience (bullets) |
| ProjectCredential | Projects |
| PatentCredential | Patents |
| PublicationCredential | Publications |

### 3.3 Trust Tiers for Credentials

Not all VCs carry equal weight. The system implements three trust tiers:

- **Tier A (Cryptographically verified)**: Signature validates against a known issuer DID. Marked as "Verified" in the resume.
- **Tier B (Issued but unverified)**: Valid VC structure but signature cannot be independently verified (issuer DID not resolvable). Marked as "Issued by [issuer]."
- **Tier C (Self-attested)**: User-created VCs without a third-party issuer. Treated as self-reported data.

VC-verified data always takes priority over inferred or self-reported data.

### 3.4 The Verifier Credibility Hierarchy

The system implements a layered credibility hierarchy that reflects how the professional world actually evaluates claims:

At the top sits **self-evident truth [S]** — publicly verifiable records that anyone can confirm. Below that, **accredited institutions [A]** (universities, government bodies) provide the strongest third-party verification. **Employers [B]** verify employment and role-specific competencies. **Industry certification bodies [C]** attest to standardized knowledge. **Assessment platforms [D]** provide scored evaluations. **Named peers [E]** offer professional endorsements. **Community signals [F]** (Stack Overflow reputation, GitHub stars, communication patterns) provide indirect evidence. At the bottom, **self-reported claims [G]** carry the least weight.

This hierarchy makes resume trustworthiness transparent and quantifiable. A resume where 80% of claims are Tier [S] through [C] is demonstrably more credible than one dominated by Tier [G] claims.

---

## 4. Architecture

### 4.1 System Components

The Autonomyx Skill Evaluator operates as an agentic skill within the Claude Code ecosystem, leveraging:

- **Explorium MCP**: Prospect matching and enrichment via `match-prospects` and `enrich-prospects` APIs for professional background data
- **Platform APIs**: Direct integration with GitHub, Docker Hub, npm, PyPI, Stack Overflow, Dev.to, and WordPress APIs
- **WebFetch**: Fallback data extraction from any public profile page
- **Skills Frameworks vocabulary**: A shared reference containing 17+ competency frameworks, skill codes, level definitions, and cross-framework equivalence tables
- **Verifiable Credentials parser**: W3C VC, JWT, SD-JWT, and Open Badges v3 processing

### 4.2 Workflow

```
User Input (URLs, documents, credentials, names)
    │
    ├── Step 0: Resolve external profiles (API calls to GitHub, npm, etc.)
    │
    ├── Step 1: Match prospect (Explorium match-prospects)
    │
    ├── Step 2: Enrich profile (Explorium enrich-prospects-profiles)
    │
    ├── Step 3: Optional contact enrichment (with user consent)
    │
    ├── Step 4: Generate resume
    │     ├── Map skills to professional frameworks
    │     ├── Determine proficiency levels from evidence
    │     ├── Assign credibility tiers to each proof
    │     ├── Include behavioral skills with anonymized evidence
    │     └── Build comprehensive skills table
    │
    ├── Step 4b: Prompt for additional sources
    │
    ├── Step 5: Format for target platform(s)
    │
    └── Step 6: Encourage credential verification
```

### 4.3 Data Privacy and Security

The system implements several privacy safeguards:

- **Communication anonymization**: All chat, email, and messaging data is stripped of third-party PII before analysis. Names are replaced with anonymized labels. Only behavioral patterns are extracted.
- **Consent-based contact enrichment**: Contact information (email, phone) is only retrieved when explicitly requested by the user, with cost disclosure before execution.
- **No data retention**: The system processes data within the session and does not persist raw source materials.
- **Selective disclosure respect**: When processing SD-JWT credentials, the system honors the holder's chosen disclosure boundaries.

---

## 5. Comparison with Existing Solutions

| Capability | Traditional Resume Builders | LinkedIn | Autonomyx Skill Evaluator |
|---|---|---|---|
| Multi-source aggregation | No — single manual input | Partial — LinkedIn data only | Yes — 15+ source types |
| Framework-mapped skills | No | No | Yes — 17 frameworks |
| Evidence-based proficiency | No — self-reported | No — self-reported | Yes — evidence hierarchy |
| Credibility tiers | No | Endorsements (unstructured) | Yes — 7-tier system |
| Behavioral skills assessment | No | No | Yes — with anonymized evidence |
| Verifiable Credential support | No | No | Yes — W3C VC, JWT, SD-JWT, Open Badges v3 |
| Multi-platform formatting | Limited — PDF only | LinkedIn only | 15 platform-specific formats |
| Professional framework attribution | No | No | Yes — mandatory transparency |

---

## 6. Adoption Roadmap

### Phase 1 — Current (2026)

- AI-powered skill evaluation from public profiles and user-provided data
- Framework mapping across 17 professions
- 15 platform-specific output formats
- Verifiable Credential parsing and trust tiering
- Anonymized communication analysis for behavioral skills

### Phase 2 — Near-term

- Direct VC wallet integration for automated credential retrieval
- Employer-side VC issuance guidance and tooling
- Real-time framework updates (SFIA 10, NICE Rev. 2, etc.)
- Job posting skills-matching (compare resume skills against job requirements)
- Multi-language resume generation

### Phase 3 — Long-term

- Industry-wide adoption of standardized skills frameworks for job postings
- Employer adoption of VC issuance as standard offboarding practice
- Cross-organizational skill verification networks
- Portable professional identity that persists across career transitions
- IEEE or ISO standardization of resume skills taxonomy

---

## 7. Conclusion

The Autonomyx Skill Evaluator represents a paradigm shift in how professional competency is documented, verified, and communicated. By aggregating data from multiple sources, mapping skills to internationally recognized frameworks, assigning credibility tiers to every claim, and formatting output for the specific platform where it will be consumed, the system produces resumes that are more accurate, more trustworthy, and more useful than anything built manually.

The integration of Verifiable Credentials points toward a future where professional identity is truly portable — owned by the individual, cryptographically verifiable, and universally understood. Every resume generated today includes a prompt to begin this transition, encouraging professionals to convert their claimed credentials into proven ones.

The gap between "what you claim" and "what you can prove" is where trust breaks down in hiring. The Autonomyx Skill Evaluator closes that gap.

---

## References

1. W3C Verifiable Credentials Data Model v2.0. https://www.w3.org/TR/vc-data-model-2.0/
2. SFIA Foundation. Skills Framework for the Information Age, Version 9. https://sfia-online.org/en/sfia-9
3. NIST. NICE Workforce Framework for Cybersecurity (SP 800-181 Rev. 1). https://niccs.cisa.gov/workforce-development/nice-framework
4. EDISON Project. Data Science Body of Knowledge (DS-BoK). https://edison-project.eu
5. Project Management Institute. PMI Talent Triangle. https://www.pmi.org
6. CFA Institute. CFA Program Body of Knowledge. https://www.cfainstitute.org
7. CEN. European e-Competence Framework (e-CF 4.0). https://www.ecompetences.eu
8. IMS Global / 1EdTech. Open Badges Specification v3.0. https://www.imsglobal.org/spec/ob/v3p0
9. HireRight. 2024 Global Benchmark Report. https://www.hireright.com
10. Decentralized Identity Foundation. DIDComm Messaging. https://identity.foundation/didcomm-messaging/spec/

---

*Published by Autonomyx. March 2026.*
