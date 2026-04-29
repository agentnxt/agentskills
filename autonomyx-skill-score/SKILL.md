---
did: skill:009
version: "1.0.0"
created: "2026-04-29"
name: autonomyx-skill-score
description: >
  Evaluates professional skills from any source and generates a verified, framework-mapped
  resume. Trigger this skill when a user asks to create, build, or generate a resume, evaluate
  skills, or assess professional competencies. Accepts any input: profile URLs (LinkedIn, GitHub,
  Docker Hub, Stack Overflow, npm, PyPI, Dev.to, Medium, Behance, Dribbble, Kaggle, WordPress,
  or any platform), Verifiable Credentials, chat/email exports, authored documents, patents,
  certifications, or self-reported data. Evaluates each skill against profession-specific
  competency frameworks (SFIA, NICE, EDISON, PMI, CFA, SHRM, CIM, etc.) with proficiency levels
  and credibility-tiered proof ([S] self-evident through [G] self-reported). Uses Explorium
  prospect matching and enrichment for professional background. Outputs a structured, ATS-friendly
  resume in Markdown with a comprehensive skills table, verification status, and credential
  verification encouragement.
---

# Autonomyx Skill Score for Professionals

Evaluates professional skills from any source — profiles, credentials, documents, and
communications — and generates a verified, framework-mapped resume.

## When to Use

Trigger this skill when the user:
- Asks to create/build/generate a resume from any online profile (LinkedIn, GitHub, etc.)
- Provides any profile URL and asks for a resume
- Provides a person's name (and optionally company) and asks for a resume
- Provides documents, chat exports, patents, or other content and asks for a resume
- Asks to convert any profile or professional data into resume format
- Asks to combine multiple sources into a resume

## Inputs

The user must provide **at least one** of the following:

**Identity sources (for prospect matching):**
- **Any profile URL** from a supported or unsupported platform
- **Full name + company name** (e.g., "John Doe at Acme Corp")
- **Email address** of the person
- **Multiple profile URLs** from different platforms (combined into one resume)

**Supplementary sources (for enriching the resume):**
- **Verifiable Credentials (VCs)** — JSON-LD, JWT, or SD-JWT files; VC wallet URL; Open Badges v3 (highest trust source)
- **Chat/message exports** — Slack archives, WhatsApp exports, Teams data, email `.mbox`/`.eml` files
- **Authored documents** — whitepapers, research papers, blog posts, presentations, proposals, PRDs
- **Patent numbers or inventor name** — for patent lookup
- **Blog or personal website URL** — for publication extraction
- **Certification URLs or badge links** — Credly, Google Cloud, AWS, Microsoft Learn
- **Screenshots** of profiles, dashboards, or achievement pages from any platform
- **Self-reported data** — user describes roles, projects, achievements from memory (structured Q&A)

The skill combines all provided sources into a single comprehensive resume. If the input
is ambiguous, ask the user to clarify before proceeding.

---

## Supported Platforms

### Tier 1 — Direct Prospect Match (richest data)
These platforms are natively supported by Explorium `match-prospects`:

| Platform | URL pattern | match-prospects field |
|---|---|---|
| **LinkedIn** | `linkedin.com/in/<username>` | `linkedin` (direct) |

### Tier 2 — Public API Resolution (portfolio + identity)
These platforms have public APIs to extract identity info and portfolio data:

| Platform | URL pattern | API endpoint | Resume section |
|---|---|---|---|
| **GitHub** | `github.com/<user>` | `api.github.com/users/<user>` | Technical Profile |
| **Docker Hub** | `hub.docker.com/u/<user>` | `hub.docker.com/v2/users/<user>` | Container & DevOps Profile |
| **WordPress.com** | `<site>.wordpress.com` or profile URL | WP MCP tools | Publishing & Content Profile |
| **npm** | `npmjs.com/~<user>` | `registry.npmjs.org/-/user/org.couchdb.user:<user>` | Open Source Packages |
| **PyPI** | `pypi.org/user/<user>` | `pypi.org/user/<user>` (web) | Open Source Packages |
| **Stack Overflow** | `stackoverflow.com/users/<id>/<name>` | `api.stackexchange.com/2.3/users/<id>` | Developer Community Profile |
| **Dev.to** | `dev.to/<user>` | `dev.to/api/users/by_username?url=<user>` | Technical Writing Profile |
| **Medium** | `medium.com/@<user>` | `medium.com/@<user>` (web) | Publishing & Content Profile |
| **Behance** | `behance.net/<user>` | `behance.net/<user>` (web) | Design Portfolio |
| **Dribbble** | `dribbble.com/<user>` | `dribbble.com/<user>` (web) | Design Portfolio |
| **Kaggle** | `kaggle.com/<user>` | `kaggle.com/<user>` (web) | Data Science Profile |

### Tier 3 — Chat & Messaging Platforms (skill inference from conversations)
These platforms don't expose public profile APIs, but if the user provides exported chat logs,
message archives, or grants access via MCP/API integrations, the skill can **infer professional
skills, expertise areas, and communication style** from conversation content.

| Platform | Input type | What can be inferred |
|---|---|---|
| **Slack** | Exported workspace data, channel archives, or MCP integration | Technical discussions, domain expertise, tools mentioned, leadership signals, collaboration patterns |
| **WhatsApp** | Exported chat `.txt` files | Professional discussions, industry knowledge, client interactions |
| **Microsoft Teams** | Exported chat/channel data | Technical expertise, project involvement, cross-functional skills |
| **Discord** | Exported server data or public server profiles | Community involvement, technical support, domain expertise |
| **Telegram** | Exported chat data | Professional discussions, technical knowledge |
| **Email (Gmail, Outlook, etc.)** | Exported `.mbox`, `.eml`, or `.pst` files, or user-provided email excerpts | Professional correspondence, client relationships, project coordination, industry terminology, role scope |

### Tier 3b — Documents Authored (skill inference from written work)
If the user provides documents they have authored, the skill can infer expertise, writing
ability, domain knowledge, and technical depth from the content.

| Document type | What can be inferred |
|---|---|
| **Technical documents** (whitepapers, RFCs, architecture docs) | Technical depth, system design skills, domain expertise |
| **Research papers / publications** | Academic expertise, research methodology, subject matter authority |
| **Blog posts / articles** | Communication skills, thought leadership, domain knowledge |
| **Presentations / slide decks** | Presentation skills, strategic thinking, audience awareness |
| **Reports / analyses** | Analytical skills, data interpretation, business acumen |
| **Code documentation / READMEs** | Technical writing, developer experience focus |
| **Proposals / RFPs** | Business development, solution architecture, client management |
| **Project plans / PRDs** | Project management, product thinking, requirements analysis |
| **Patents** | Innovation, technical invention, R&D leadership |

**Patent lookup:**
If the user provides their name or a patent number, search for patents via:
- Google Patents: `https://patents.google.com/?inventor=<name>` (WebFetch)
- USPTO: `https://patft.uspto.gov/` (WebFetch)
Extract: patent title, patent number, filing date, grant date, co-inventors, abstract.
Build a **Patents** section in the resume.

**Blog & publication lookup:**
If the user provides a blog URL or personal website, fetch the site via WebFetch and extract:
- Article titles, dates, and topics
- Recurring themes and expertise areas
- Authorship evidence

**How document inference works:**
1. Read the provided documents (PDF, DOCX, TXT, MD, or other supported formats)
2. Analyze content for:
   - **Subject matter expertise**: topics, technologies, methodologies discussed with authority
   - **Writing quality**: clarity, structure, persuasiveness (useful for summary tone)
   - **Technical depth**: complexity of concepts explained, tools and frameworks referenced
   - **Role indicators**: authorship context (individual contributor vs. lead vs. executive perspective)
   - **Publications list**: titles, dates, venues for a Publications section
3. Build a **Publications & Authored Work** section if formal publications are found
4. Merge inferred skills into the main Skills section (tagged as "inferred from authored work")

**Important:** Clearly distinguish between verified credentials (from platform APIs) and
inferred skills (from documents and chat). Use the label "(inferred)" next to skills
derived from unstructured content.

**How skill inference works:**
1. Parse the provided chat export or connected message source
2. Identify professional signals:
   - **Technical skills**: programming languages, tools, frameworks, platforms mentioned in context
   - **Domain expertise**: recurring topics, industry terminology, problem-solving patterns
   - **Soft skills**: leadership language ("I'll handle", "let's coordinate"), mentoring patterns,
     cross-team collaboration
   - **Projects & deliverables**: references to specific projects, launches, milestones
   - **Role indicators**: decision-making patterns, scope of responsibility
3. Build a **Communication & Collaboration Profile** section for the resume
4. Merge inferred skills into the main Skills section (tagged as "inferred from communications")

**Important:** Always inform the user that skills inferred from chat data are contextual
estimates, not verified credentials. Mark them distinctly in the resume.

### Tier 4 — Platforms Without Public APIs (context derivation)
For platforms that lack public APIs (Google, Microsoft, Amazon, ChatGPT, Claude, etc.),
the skill can still derive useful context from:

| Source | How to use |
|---|---|
| **User-provided activity exports** | Most platforms offer data export (Google Takeout, Microsoft account data, Amazon order history). If the user provides exported data files, parse them for professional signals. |
| **User-provided screenshots** | Read screenshots of profile pages, dashboards, certifications, or activity feeds using the image reading capability. Extract text, achievements, and activity data. |
| **User-described context** | Ask the user to describe their usage, certifications, or achievements on the platform. Incorporate their self-reported data (clearly marked as self-reported). |
| **Certification URLs** | Many platforms issue verifiable certifications (Google Cloud certs, AWS certs, Microsoft certs, Azure certs). If the user provides a certification verification URL, fetch and validate it. |
| **Public certification directories** | Some platforms have public cert verification pages (e.g., Credly badges, AWS Certification verification). If the user provides a badge URL, fetch it. |

**Certification platforms with public verification:**
- **Credly** (`credly.com/users/<user>`) — badges from AWS, Google, Microsoft, Cisco, etc.
- **Acclaim/Credly badges** — direct badge URLs are publicly fetchable
- **Google Cloud Skills Boost** (`cloudskillsboost.google/public_profiles/<id>`)
- **Microsoft Learn** (`learn.microsoft.com/en-us/users/<user>`)
- **AWS Certification** (verification requires cert number from user)

### Tier 5 — Web Fetch Fallback (any other platform)
Any other platform URL not covered above. The skill fetches the public page and attempts
to extract:
- Display name
- Bio / about text
- Company or organization
- Email (if publicly visible)
- Portfolio items or activity
- Certification badges or achievements

---

## Data Accessibility Reality

**Critical constraint:** Users typically lose access to corporate accounts and data after
leaving a company. The skill must acknowledge this and guide users toward **currently
accessible sources** rather than asking for data they can no longer reach.

### What users typically lose access to after leaving a company

| Lost source | Why | Alternative |
|---|---|---|
| Corporate email (Outlook, Gmail workspace) | Account deactivated on exit | Personal email archives (if forwarded before leaving), personal Gmail/Outlook with work-related threads |
| Slack workspace | Removed from org on exit | Personal Slack exports (if downloaded before leaving), screenshots of key conversations |
| Microsoft Teams | Tied to corporate M365 license | Personal copies of documents shared via Teams |
| Jira / Confluence / internal wikis | Corporate SSO revoked | Screenshots, exported PDFs, personal notes about projects |
| Internal Git repos (GitHub Enterprise, GitLab self-hosted) | Access revoked | Personal GitHub/GitLab with open-source contributions; forked repos; commit history in public mirrors |
| Google Drive / SharePoint | Corporate account disabled | Personal copies of authored documents saved before leaving |
| CRM data (Salesforce, HubSpot) | Account deactivated | Personal notes, deal summaries, client lists (non-confidential) |
| Internal dashboards / analytics | SSO revoked | Screenshots taken during employment, exported reports |

### What users typically retain after leaving

| Retained source | Accessibility | Value for resume |
|---|---|---|
| **LinkedIn profile** | Always accessible (personal account) | Primary identity + work history |
| **GitHub personal account** | Always accessible | Open-source contributions, personal projects, languages |
| **Personal blog / website** | Always accessible | Authored content, thought leadership |
| **Stack Overflow** | Always accessible (personal account) | Community reputation, expertise areas |
| **Published papers / patents** | Publicly indexed | Academic and innovation credentials |
| **Certification badges (Credly, etc.)** | Always accessible (personal account) | Verified credentials |
| **npm / PyPI packages** | Always accessible (personal account) | Published open-source work |
| **Docker Hub** | Always accessible (personal account) | Published container images |
| **Dev.to / Medium articles** | Always accessible (personal account) | Published writing |
| **Behance / Dribbble** | Always accessible (personal account) | Design portfolio |
| **Personal copies of documents** | If saved before leaving | Authored work evidence |
| **Personal chat exports** | If exported before leaving | Skill inference |
| **Screenshots** | If captured during employment | Visual evidence of achievements, dashboards |
| **Personal email archives** | Personal email accounts retained | Work-related correspondence (if any was via personal email) |
| **Award / recognition emails** | If forwarded to personal email | Achievement evidence |
| **Performance review excerpts** | If personally saved | Self-assessment content, manager feedback |
| **Recommendation letters / references** | If personally saved | Third-party endorsements |

### Guidance for the skill

1. **Never ask for data the user likely cannot access.** If the user mentions they have left
   a company or are job-seeking, do NOT ask for corporate Slack exports, work email archives,
   or internal documents. Instead, focus on currently accessible sources.

2. **Prioritize persistent personal accounts.** LinkedIn, GitHub, Stack Overflow, personal
   blogs, published work, and certifications survive job transitions. Lead with these.

3. **Ask about pre-departure exports.** Some users export data before leaving. It's OK to ask:
   "Did you happen to save any documents, chat exports, or screenshots from your previous
   role?" — but frame it as optional, not expected.

4. **Leverage Explorium as the backbone.** Explorium's `enrich-prospects-profiles` provides
   work history and education regardless of whether the user still has corporate access.
   This is the primary source for the Experience section.

5. **Self-reported data is valid.** If the user describes their responsibilities, projects,
   or achievements from memory, incorporate this data clearly marked as "self-reported."
   Ask structured questions to help them recall:
   - "What were your 3 biggest projects or accomplishments at [company]?"
   - "What tools and technologies did you use daily?"
   - "Did you manage a team? How large?"
   - "What metrics or outcomes can you quantify?"

6. **Present tense vs. past tense.** Detect whether the user is currently employed or
   job-seeking (from context or by asking). Tailor the resume accordingly:
   - **Currently employed:** Focus on present-role data; corporate sources may be accessible
   - **Job-seeking / between roles:** Focus on persistent personal accounts + self-reported data

### The Verifiable Credentials Solution

The data accessibility gap described above is being solved by **Verifiable Credentials (VCs)**.
With VCs, professional data becomes portable, tamper-proof, and owned by the individual —
not locked inside corporate systems.

**How VCs change resume generation:**

| Traditional problem | VC solution |
|---|---|
| Work history locked in corporate HR systems | Employer issues a VC for each role (title, dates, responsibilities) — employee owns it forever |
| Skills claimed but unverified | Skills endorsed via VCs by employers, peers, or assessment platforms |
| Certifications expire or verification links break | Certification VCs are cryptographically signed and permanently verifiable |
| Education credentials require manual verification | Universities issue degree VCs directly to graduates |
| Project contributions lost when leaving | Project VCs issued during employment capture deliverables and impact |
| Performance data inaccessible after exit | Achievement VCs (awards, promotions, metrics) portable with the employee |
| Chat/email evidence of skills disappears | Skill attestation VCs replace the need to mine raw communications |

**VC-aware resume generation workflow:**

If the user provides Verifiable Credentials (as JSON-LD, JWT, or via a VC wallet URL):

1. **Parse the VC payload** — extract claims (issuer, subject, credential type, issuance date,
   expiration, evidence)
2. **Verify the credential** — check the cryptographic signature against the issuer's DID
   (Decentralized Identifier) or public key. If verification fails, mark the credential as
   "unverified" and inform the user.
3. **Map VC types to resume sections:**

| VC credential type | Resume section | Data extracted |
|---|---|---|
| `EmploymentCredential` | Experience | Job title, company, dates, responsibilities, department |
| `EducationCredential` | Education | Degree, institution, field, dates, honors |
| `CertificationCredential` | Certifications | Cert name, issuer, date, expiry, verification |
| `SkillCredential` / `EndorsementCredential` | Skills | Skill name, proficiency level, endorser |
| `AchievementCredential` | Experience (bullets) | Award name, description, date, issuer |
| `ProjectCredential` | Experience (bullets) or Projects section | Project name, role, outcomes, technologies |
| `PatentCredential` | Patents | Patent number, title, dates, co-inventors |
| `PublicationCredential` | Publications | Title, venue, date, co-authors |
| `MembershipCredential` | Professional Affiliations | Organization, role, dates |
| `VolunteerCredential` | Volunteer Experience | Organization, role, dates, impact |

4. **Trust tiers for VCs:**
   - **Tier A (cryptographically verified):** Signature validates against known issuer DID.
     Mark in resume as "Verified" with issuer name.
   - **Tier B (issued but unverified):** VC structure is valid but signature cannot be
     independently verified (e.g., issuer DID not resolvable). Mark as "Issued by [issuer]."
   - **Tier C (self-attested):** User-created VCs without third-party issuer. Treat same as
     self-reported data.

5. **VC data takes priority** over inferred/self-reported data. When a VC confirms a skill
   or role, it supersedes and replaces any "(inferred)" tag on that item.

6. **Display verification status** in the resume:
   - Skills from VCs: `Python (verified by Acme Corp)` instead of `Python (inferred)`
   - Roles from VCs: show a small "Verified" indicator next to the role
   - Certs from VCs: include "Cryptographically verified" note

**Supported VC formats:**
- W3C Verifiable Credentials (JSON-LD with `@context: "https://www.w3.org/2018/credentials/v1"`)
- JWT-encoded VCs (decoded and parsed)
- SD-JWT (Selective Disclosure JWT) — respect holder's disclosure choices
- VC wallet URLs (fetch VCs from the user's digital wallet if they provide access)
- Open Badges v3 (which align with the W3C VC data model)

**VC wallet integration:**
If the user provides a wallet URL or DID, attempt to fetch their public credential
presentations. Common wallet protocols:
- **DIDComm** — message-based credential exchange
- **OpenID4VP** — presentation over OpenID Connect
- **CHAPI** — Credential Handler API (browser-based)

For this skill, the simplest path is asking the user to **export their VCs as JSON files**
and provide them as input.

---

## Workflow

### Step 0 — Resolve External Profiles

For each non-LinkedIn URL provided, resolve it to identity information and portfolio data.

#### GitHub (`github.com/<username>`)
1. Fetch `https://api.github.com/users/<username>` via WebFetch
2. Extract: `name`, `email`, `company`, `bio`, `public_repos`, `followers`, `blog`
3. Fetch `https://api.github.com/users/<username>/repos?sort=stars&per_page=5` for top repos
4. Fetch `https://api.github.com/users/<username>/events/public` for recent activity & languages
5. Store as **GitHub Portfolio** data

#### Docker Hub (`hub.docker.com/u/<username>`)
1. Fetch `https://hub.docker.com/v2/users/<username>` via WebFetch
2. Fetch `https://hub.docker.com/v2/repositories/<username>/?page_size=5&ordering=-star_count`
   for top images
3. Extract: username, full name (if available), top images with pull counts and stars
4. Store as **Docker Portfolio** data

#### WordPress.com (site URL or profile)
1. Use the WordPress MCP tools (`wpcom-mcp-user-profile`, `wpcom-mcp-user-sites`) if the user
   is authenticated, OR fetch the public site via WebFetch
2. Extract: display name, site URL, site description, recent posts, content themes
3. Store as **WordPress Portfolio** data

#### Stack Overflow (`stackoverflow.com/users/<id>/<name>`)
1. Extract user ID from URL
2. Fetch `https://api.stackexchange.com/2.3/users/<id>?site=stackoverflow` via WebFetch
3. Extract: `display_name`, `reputation`, `badge_counts`, `about_me`, `website_url`, `location`
4. Fetch `https://api.stackexchange.com/2.3/users/<id>/top-tags?site=stackoverflow&pagesize=10`
   for expertise areas
5. Store as **Stack Overflow Profile** data

#### npm (`npmjs.com/~<username>`)
1. Fetch `https://registry.npmjs.org/-/v1/search?text=maintainer:<username>&size=10` via WebFetch
2. Extract: package names, descriptions, download counts
3. Store as **npm Portfolio** data

#### PyPI (`pypi.org/user/<username>`)
1. Fetch `https://pypi.org/user/<username>/` via WebFetch
2. Extract: list of maintained packages
3. For top packages, fetch `https://pypi.org/pypi/<package>/json` for details
4. Store as **PyPI Portfolio** data

#### Dev.to (`dev.to/<username>`)
1. Fetch `https://dev.to/api/users/by_username?url=<username>` via WebFetch
2. Extract: `name`, `username`, `summary`, `github_username`, `website_url`, `joined_at`
3. Fetch `https://dev.to/api/articles?username=<username>&per_page=5` for top articles
4. Store as **Dev.to Portfolio** data

#### Medium, Behance, Dribbble, Kaggle, or any other platform
1. Fetch the public profile page via WebFetch
2. Parse the page content to extract: display name, bio, location, portfolio items,
   follower counts, or any other publicly visible information
3. Store as **[Platform] Portfolio** data

**Identity resolution priority (for prospect matching):**
After resolving all profiles, combine extracted identifiers in this priority:
1. `email` (most reliable for matching)
2. `full_name` + `company_name` (good for matching)
3. `full_name` alone (may produce multiple matches — will require user disambiguation)

If no identifiers can be extracted from any provided profile, inform the user and ask for
a LinkedIn URL, email, or full name + company.

### Step 1 — Match the Prospect

Use `match-prospects` to identify the person in Explorium's database.

**Input mapping:**
| User provides | match-prospects field |
|---|---|
| LinkedIn URL | `linkedin` (direct) |
| Other platform URL | Resolved via Step 0 → `full_name` + `company_name` and/or `email` |
| Full name + company | `full_name` + `company_name` |
| Email address | `email` |

**Matching strategy for non-LinkedIn inputs:**
- Try the most specific identifiers first (email > name+company > name alone)
- If `match-prospects` returns no results with name+company, retry with email if available
- If multiple matches are returned, present them to the user and ask which person to use

**If no match is found:**
- If portfolio data was collected in Step 0, offer to generate a **portfolio-only resume**
  using just the platform data (no Explorium enrichment). This resume will have portfolio
  sections but limited work history.
- Otherwise, inform the user and suggest they provide a LinkedIn URL or additional identifiers.

### Step 2 — Enrich the Prospect Profile

Once matched, call `enrich-prospects` with:
- `enrichments`: `["enrich-prospects-profiles"]`
- The `session_id` and `table_name` from the match-prospects result

This retrieves:
- Full name and demographics
- Current and past job titles, companies, and durations
- Education history (schools, degrees, fields of study)
- Location information
- Role details and seniority

### Step 3 — Optionally Enrich Contact Information

If the user explicitly requests contact details on the resume, also call `enrich-prospects` with:
- `enrichments`: `["enrich-prospects-contacts"]`
- `parameters`: `{"contact_types": ["email", "phone"]}` (or whichever the user requests)

**Important:** Only include contact information if the user specifically asks for it. Contact
enrichment has a credit cost — always show the cost estimate and get user confirmation before
proceeding.

### Step 4 — Generate the Resume

Using all retrieved data (Explorium enrichment + platform portfolio data), generate a
professional resume following the format in the **Resume Template** section below.

**Data mapping rules:**
- **Name**: Use the full name from the enriched profile (Explorium takes priority over platform data)
- **Title**: Use the current job title; if unavailable, derive from most recent role
- **Location**: Use city/state/country from the profile
- **Contact**: Only include if Step 3 was performed and user requested it
- **Profile Links**: Include all platform URLs the user provided in the header
- **Summary**: Synthesize a 2–3 sentence professional summary from role history, seniority,
  industry, and skills. If platform portfolio data is available, weave in relevant highlights
  (e.g., "active open-source contributor with 50+ GitHub repos"). Do NOT fabricate achievements
  or metrics not present in the data.
- **Experience**: List all roles in reverse chronological order. Include company name, title,
  date range, and location where available.
- **Education**: List degrees in reverse chronological order. Include institution, degree,
  field of study, and dates where available.
- **Skills**: Build a detailed skills table with three columns: **Skill**, **Level**, and
  **Proof**. Extract skills from job titles, role descriptions, industry context, AND platform
  data (GitHub languages, Stack Overflow top tags, npm/PyPI package domains). For each skill:
  - **Determine the proficiency level** using the evidence-based level framework (see below)
  - **Identify the proof source** — what evidence supports this skill and at what level
  - **Mark verification status** — if a VC or platform credential verifies the skill, show
    "Verified by [issuer]"; otherwise show the evidence source
- **Platform Portfolio Sections**: Append platform-specific sections after Skills. Only include
  sections for platforms where data was collected. See template below.

### Step 4b — Prompt for Additional Sources

Before generating the final resume, **proactively ask the user** if they can provide
additional sources to strengthen the resume. Present a checklist of potential sources
based on what's missing:

> **To build the strongest possible resume, consider sharing any of these additional sources:**
>
> **Profile URLs** (the more, the better):
> - [ ] LinkedIn profile
> - [ ] GitHub profile
> - [ ] Stack Overflow profile
> - [ ] Docker Hub profile
> - [ ] npm / PyPI author page
> - [ ] Dev.to / Medium / blog URL
> - [ ] Behance / Dribbble portfolio
> - [ ] Kaggle profile
> - [ ] Personal website or blog
> - [ ] Any other professional profile
>
> **Documents & work samples:**
> - [ ] Published papers, whitepapers, or articles
> - [ ] Patent numbers (or name for patent search)
> - [ ] Presentations or slide decks
> - [ ] Technical documentation you've authored
>
> **Communications (for skill inference):**
> - [ ] Slack workspace export
> - [ ] Email archives (`.mbox` or sample emails)
> - [ ] Chat exports (WhatsApp, Teams, Discord)
>
> **Certifications:**
> - [ ] Credly badge URLs
> - [ ] Cloud certification links (AWS, GCP, Azure)
> - [ ] Any certification verification URLs
>
> **Other:**
> - [ ] Screenshots of profiles or achievements
> - [ ] Activity exports from any platform (Google Takeout, etc.)
>
> **Verifiable Credentials (strongest proof):**
> - [ ] Employment VCs from current/past employers
> - [ ] Education VCs from universities
> - [ ] Skill endorsement VCs
> - [ ] Project or achievement VCs
> - [ ] VC wallet URL or exported VC JSON files
>
> *You can skip any of these — I'll build the best resume possible with whatever you provide.
> Just say "go ahead" to proceed with what we have, or share additional sources.*

Only show items that haven't already been provided. Skip the prompt entirely if the user
has explicitly said they want a quick/simple resume or to proceed with what they have.

### Step 5 — Format for Target Platform

Before presenting the resume, ask the user **where they intend to publish or use it**.
The output format, content emphasis, tone, and structure change significantly depending on
the target platform.

> "Where will you be using this resume? I'll optimize the format accordingly."
>
> - [ ] **LinkedIn** — Profile optimization
> - [ ] **Job board** (Indeed, Glassdoor, Monster, Naukri, etc.)
> - [ ] **ATS submission** (Applicant Tracking System — Workday, Greenhouse, Lever, etc.)
> - [ ] **Company career page** (direct application)
> - [ ] **PDF / Print** — Traditional resume document
> - [ ] **Personal website / Portfolio**
> - [ ] **GitHub README** (developer profile)
> - [ ] **Behance / Dribbble** (design portfolio)
> - [ ] **Credly / credential wallet** (skills-focused)
> - [ ] **Email to recruiter**
> - [ ] **Networking / conferences**
> - [ ] **Internal promotion** (within current company)
> - [ ] **Freelance platforms** (Upwork, Toptal, Fiverr)
> - [ ] **Academic** (CV for faculty/research positions)
> - [ ] **Government / public sector** application
> - [ ] **Multiple platforms** (I need several versions)

If the user skips this step or says "just a resume", default to **ATS-optimized Markdown**.

#### Platform-Specific Output Formats

##### LinkedIn Profile Optimization
| Aspect | LinkedIn format |
|---|---|
| **Output type** | Section-by-section text blocks ready to paste into LinkedIn fields |
| **Headline** | 120 chars max. Format: `[Title] | [Specialty] | [Key differentiator]` |
| **About section** | 2,600 chars max. First-person voice. Hook in first 3 lines (visible before "see more"). Story-driven, not list-driven. |
| **Experience** | Each role: title, company, date range, 3–5 bullet points. Use LinkedIn's character limits. Focus on impact and outcomes. |
| **Skills** | Top 50 skills (LinkedIn allows 50). Order by endorsement potential. No framework codes — LinkedIn doesn't support them. |
| **Education** | Institution, degree, field, dates, activities/societies |
| **Featured section** | Suggest 3–5 items to feature: top articles, repos, certifications, presentations |
| **Recommendations** | Draft 2–3 recommendation request templates the user can send to colleagues |
| **Tone** | Conversational, first-person, achievement-oriented. Avoid jargon-heavy buzzwords. |
| **Keywords** | Embed industry keywords naturally for LinkedIn search algorithm (recruiter search SEO) |
| **What to omit** | Framework codes, credibility tiers, verification status table (not supported by LinkedIn) |

##### Job Boards (Indeed, Glassdoor, Monster, Naukri)
| Aspect | Job board format |
|---|---|
| **Output type** | Plain text or simple HTML (most job boards strip formatting) |
| **Length** | 1–2 pages max. Concise. No tables or complex formatting. |
| **Structure** | Contact → Summary → Skills (keyword list) → Experience → Education → Certifications |
| **Skills** | Flat comma-separated keyword list (optimized for job board search matching) |
| **Tone** | Professional, third-person or implied first-person. Action verbs. Quantified achievements. |
| **Keywords** | Heavy keyword optimization — match common job posting language |
| **What to omit** | Portfolio sections, framework codes, verification tiers, lengthy project descriptions |

##### ATS (Applicant Tracking Systems — Workday, Greenhouse, Lever, Taleo)
| Aspect | ATS format |
|---|---|
| **Output type** | Clean, single-column Markdown or plain text. NO tables, columns, headers with special characters, or graphics. |
| **File format** | `.docx` (preferred by most ATS) or `.pdf` (if ATS supports it). Offer both. |
| **Structure** | Contact → Summary → Experience → Education → Skills → Certifications. Strict reverse chronological. |
| **Skills** | Keyword-dense section. Include both acronyms and full terms (`AWS (Amazon Web Services)`). Match job posting language exactly. |
| **Formatting rules** | Standard section headers (`Experience`, `Education`, `Skills` — not creative alternatives). No text boxes, no columns, no images. Standard fonts. |
| **Dates** | Use standard format: `Jan 2020 – Present` or `01/2020 – Present`. Avoid ambiguous formats. |
| **Tone** | Achievement-focused. Start bullets with action verbs. Quantify where possible. |
| **What to omit** | Framework codes, verification tiers, portfolio sections, GitHub stats. Keep it clean and parseable. |
| **ATS test** | After generating, offer to check if the resume is ATS-friendly (no parsing-breaking elements) |

##### PDF / Print (Traditional Resume)
| Aspect | PDF format |
|---|---|
| **Output type** | Well-formatted Markdown (for PDF rendering) or LaTeX source |
| **Layout** | Professional typography. Clear section dividers. Appropriate white space. 1–2 pages (3+ only for 15+ years experience). |
| **Structure** | Full template with all earned sections. Include skills table with framework mapping and proof. |
| **Skills** | Full skills table with Framework Mapping, Level, and Proof columns (the complete format) |
| **Verification** | Include Credential Verification Status table |
| **Tone** | Formal, professional, third-person implied |
| **What to include** | Everything — this is the comprehensive version |

##### Personal Website / Portfolio
| Aspect | Website format |
|---|---|
| **Output type** | HTML-ready Markdown or structured JSON (for static site generators like Jekyll, Hugo, Gatsby) |
| **Layout** | Sections designed for web layout: hero header, cards for experience, grid for skills, embedded links |
| **Skills** | Visual skill bars or badges. Include framework codes as tooltips/metadata. Link to proof sources (GitHub, SO, etc.) |
| **Portfolio sections** | Full platform portfolio sections with live links to repos, articles, packages, designs |
| **Interactivity** | Suggest adding: filterable skills by category, expandable experience cards, live GitHub contribution graph embed |
| **SEO** | Include JSON-LD structured data (`schema.org/Person`, `schema.org/Occupation`) for search engine visibility |
| **Tone** | Personable, first-person, showcasing personality alongside credentials |

##### GitHub README (Developer Profile)
| Aspect | GitHub format |
|---|---|
| **Output type** | GitHub-flavored Markdown for `README.md` in a profile repository (`username/username`) |
| **Layout** | Badges at top (tech stack, certifications), brief bio, pinned repos section, skills with shield.io badges, contribution stats |
| **Skills** | Shield.io badge format: `![Python](https://img.shields.io/badge/Python-Expert-blue)` |
| **Stats** | Include GitHub stats card embed: `github-readme-stats` |
| **Tone** | Developer-friendly, concise, badge-heavy, link-rich |
| **What to emphasize** | Open source contributions, tech stack, top repos, contribution streaks |
| **What to omit** | Detailed work history (link to LinkedIn instead), formal education details |

##### Behance / Dribbble (Design Portfolio)
| Aspect | Design portfolio format |
|---|---|
| **Output type** | Project-centric narrative. Each project as a case study outline. |
| **Structure** | Bio → Design philosophy → Featured projects (problem → process → outcome) → Skills → Tools |
| **Skills** | Visual/design tool proficiency: Figma, Sketch, Adobe CC, prototyping, design systems |
| **Tone** | Creative, visual-thinking, process-oriented |
| **What to emphasize** | Design process, user impact, visual problem-solving, collaboration with engineering |

##### Credly / Credential Wallet (Skills-Focused)
| Aspect | Credential format |
|---|---|
| **Output type** | Skills-first format. Structured list of verified credentials and skill claims. |
| **Structure** | Verified credentials (with proof links) → Skills table (framework-mapped) → Supporting experience |
| **Skills** | Full framework-mapped table with credibility tiers. This IS the primary content. |
| **Emphasis** | Verification status of every claim. Link every credential to its verification URL. |
| **Tone** | Factual, evidence-based, minimal narrative |

##### Email to Recruiter
| Aspect | Email format |
|---|---|
| **Output type** | Email body text + attached resume (PDF). Generate both. |
| **Email body** | 150–200 word cover note: who you are, what you're looking for, 2–3 key highlights, call to action |
| **Attached resume** | ATS-optimized PDF (see ATS format above) |
| **Tone** | Professional but warm. Not robotic. Show genuine interest. |
| **Personalization** | If user specifies the company/role, tailor the email and resume keywords to match |

##### Freelance Platforms (Upwork, Toptal, Fiverr)
| Aspect | Freelance format |
|---|---|
| **Output type** | Platform-specific profile sections (title, overview, skills, portfolio items) |
| **Title** | `[Specialty] | [Key tool/tech] | [Years] years experience` |
| **Overview** | 500–1000 chars. Problem-solver framing: what client problems you solve. Social proof (stats, notable clients). |
| **Skills** | Platform tag format. Match platform's skill taxonomy. |
| **Portfolio** | 3–5 best projects framed as client outcomes |
| **Hourly rate context** | Suggest positioning based on skill level and market rates (if user asks) |
| **Tone** | Client-focused, outcome-oriented. "I help [audience] achieve [outcome] by [method]." |

##### Academic CV (Faculty / Research)
| Aspect | Academic CV format |
|---|---|
| **Output type** | Full academic CV (no page limit — can be 5–20+ pages) |
| **Structure** | Contact → Education → Research Interests → Publications → Grants/Funding → Teaching → Conferences/Talks → Awards → Service → References |
| **Publications** | Full citation format (APA/IEEE/ACM depending on field). Separate: journal articles, conference papers, book chapters, preprints, patents |
| **Skills** | NOT a primary section. Academic CVs emphasize research output, not skills lists. Include technical competencies only in a brief "Technical Skills" subsection. |
| **Tone** | Formal academic. Third person. Factual. |
| **What to emphasize** | Publications, h-index, citations, grants won, students supervised, editorial board service |
| **What to omit** | Skill framework mapping, verification tiers, portfolio sections (unless relevant to research) |

##### Government / Public Sector Application
| Aspect | Government format |
|---|---|
| **Output type** | Detailed, structured resume following government application standards |
| **Structure** | Varies by country. For US federal: follow USAJOBS resume format. For UK: Civil Service competency framework. For India: UPSC/govt format. |
| **Length** | Often 3–5+ pages (government resumes are typically longer than private sector) |
| **Skills** | Map to the specific government competency framework if known. Include clearance level if applicable. |
| **Experience** | Detailed: include hours/week, supervisor name (if required), salary grade, exact duties |
| **Tone** | Formal, detailed, competency-aligned |
| **Keywords** | Match the specific job announcement/vacancy language exactly |

##### Internal Promotion (Within Current Company)
| Aspect | Internal format |
|---|---|
| **Output type** | Achievement-focused document emphasizing growth and impact within the organization |
| **Structure** | Current role impact → Key achievements → Skills growth → Cross-functional contributions → Career trajectory → Development goals |
| **Skills** | Emphasize skills gained/grown during tenure. Show progression. Framework mapping useful here for career ladder alignment. |
| **Tone** | Forward-looking, growth-oriented, aligned with company values/competency framework |
| **What to emphasize** | Internal impact, revenue/efficiency gains, team building, culture contributions, cross-team work |
| **What to omit** | External job history details (keep brief). Focus on current company tenure. |

#### Multi-Platform Output

If the user selects **multiple platforms**, generate each version separately with a clear
label. Highlight the key differences between versions:

> "I've generated 3 versions of your resume:
> 1. **LinkedIn** — Optimized for profile sections, first-person voice, keyword-rich
> 2. **ATS (PDF)** — Clean single-column, action verbs, keyword-matched to [target role]
> 3. **GitHub README** — Badge-heavy, repo-focused, developer community style
>
> Key differences: [brief comparison of what's included/excluded in each]"

### Step 5b — Present and Refine

- Present the resume in the selected platform format
- Offer to adjust formatting, add/remove sections, or regenerate with different emphasis
- Offer to generate additional platform versions from the same data
- If the user wants to export, offer to save in the appropriate file format

### Step 6 — Encourage Credential Verification

After presenting the resume, **proactively encourage the user to get their credentials
verified** as Verifiable Credentials. This strengthens the resume's trustworthiness and
makes their professional data permanently portable.

Present a tailored recommendation based on what's in the resume:

> **Strengthen your resume with Verified Credentials**
>
> Your resume currently contains [X] unverified items that could be upgraded to
> cryptographically verified credentials. Verified credentials make your resume
> tamper-proof and instantly trustworthy to employers.
>
> **Recommended verifications:**
> [For each unverified experience entry:]
> - [ ] **[Job Title] at [Company]** — Request an Employment VC from [Company]'s HR
>       department. Many companies now issue employment verification credentials through
>       platforms like Workday, BambooHR, or dedicated VC issuers.
>
> [For each unverified education entry:]
> - [ ] **[Degree] from [University]** — Check if [University] offers digital credential
>       issuance (many now do via Credly, Parchment, or direct VC issuance).
>
> [For each unverified certification:]
> - [ ] **[Cert Name]** — Link your certification to a Credly badge or request a VC from
>       the issuing organization.
>
> [For inferred skills:]
> - [ ] **Skills verification** — Get skill assessments from platforms like LinkedIn Skill
>       Assessments, Pluralsight IQ, or HackerRank, which can issue verifiable badges.
>
> [For unverified projects/achievements:]
> - [ ] **Project credentials** — Ask your manager or project lead to issue a Project VC
>       attesting to your role and contributions.
>
> **Important: Past credentials can be verified too!**
> You don't need to be currently employed or enrolled to get credentials verified.
> Former employers, past universities, and previous certification bodies can all issue
> retroactive Verifiable Credentials for your historical roles, degrees, and certifications.
>
> **How to get started:**
> 1. **Past employers:** Contact the HR department of any former employer and request an
>    employment verification credential. Many HR platforms (Workday, ADP, BambooHR) now
>    support digital credential issuance even for former employees. Some employers also
>    use third-party verification services (The Work Number, Truework) that can issue VCs.
> 2. **Past universities:** Check your alma mater's alumni portal or registrar's office.
>    Many universities now issue digital diplomas and transcript VCs retroactively through
>    services like Parchment, National Student Clearinghouse, Credly, or Hyland Credentials.
> 3. **Expired or past certifications:** Contact the certification body (e.g., AWS, Google,
>    Microsoft, PMI, Cisco). Even expired certifications can be verified — they can issue a
>    VC confirming you held the certification during a specific period.
> 4. **Past project work:** Ask former managers, clients, or collaborators to provide a
>    signed attestation or Project VC for specific deliverables you completed.
> 5. **Create a VC wallet** (e.g., Microsoft Entra Verified ID, Dock.io, Trinsic, or
>    Spruce ID) to store, manage, and present all your credentials in one place.
>
> *Every credential you verify — past or present — upgrades that resume item from
> "claimed" to "proven." Employers increasingly prefer candidates with verifiable
> professional histories.*

**Rules for the encouragement prompt:**
- Only suggest verifications for items actually present in the resume
- Be specific: reference the actual company names, universities, and certifications
- Don't be pushy — frame it as a value-add recommendation, not a requirement
- If the user already provided VCs, acknowledge and praise the verified items, then only
  suggest verification for remaining unverified items
- If all items are already verified, congratulate the user and skip this step

---

## Resume Template

```markdown
# [FULL NAME]

**[CURRENT TITLE]** | [LOCATION]
[Email — only if enriched] | [Phone — only if enriched]
[LinkedIn URL] | [GitHub URL] | [Other platform URLs — as applicable]

---

## Professional Summary

[2–3 sentences synthesized from career trajectory, industry, seniority level, expertise areas,
and platform highlights. Ground every claim in the retrieved data. Never fabricate metrics,
awards, or achievements.]

---

## Experience

### [JOB TITLE]
**[COMPANY NAME]** | [LOCATION] | [START DATE] – [END DATE or Present]

[If role description or responsibilities are available from enrichment, include 2–4 bullet
points. If not available, omit bullets rather than fabricating content.]

### [JOB TITLE]
**[COMPANY NAME]** | [LOCATION] | [START DATE] – [END DATE]

[Repeat for each role in reverse chronological order]

---

## Education

### [DEGREE] in [FIELD OF STUDY]
**[INSTITUTION NAME]** | [START YEAR] – [END YEAR]

[Repeat for each education entry]

---

## Skills

**Skills evaluated per:** [Framework Name] ([reference URL])

| Skill | Framework Mapping | Level | Proof |
|---|---|---|---|
| [Skill Name] | [Code — Level] | [Expert / Advanced / Intermediate / Beginner] | [Verification or evidence source] |
| Python | SFIA:PROG — Level 5 | Expert | Verified by HackerRank (Score: 95/100, Nov 2025) |
| Kubernetes | SFIA:ITOP — Level 4 | Advanced | Verified by CNCF (CKA Certification, Jan 2025) |
| React | SFIA:PROG — Level 4 | Advanced | GitHub: 12 repos, 850+ commits; Stack Overflow: top 5% tag score |
| Project Management | IPMA:ICB4 — Level C | Intermediate | Verified by PMI (PMP Certification, Mar 2024) |
| AWS Cloud Architecture | SFIA:ARCH — Level 5 | Advanced | Verified by Amazon (AWS SA Professional, Jun 2024) |
| Technical Writing | SFIA:INCA — Level 3 | Intermediate | Dev.to: 25 articles, 3,200+ reactions |
| Machine Learning | EDISON:DSML — Level 3 | Intermediate | Kaggle: 3 competitions, silver medal; PyPI: 2 ML packages |
| Team Leadership | SFIA:DLMG — Level 5 | Advanced | Inferred from role: "Engineering Manager" at Acme Corp (3 years) |
| Docker | SFIA:ITOP — Level 3 | Intermediate | Docker Hub: 8 images, 15K+ pulls |
| GraphQL | SFIA:PROG — Level 2 | Beginner | GitHub: 2 repos with GraphQL usage |
| Financial Modeling | CFA:Quant — Advanced | Advanced | Verified by CFA Institute (CFA Charterholder, 2023) |
| Market Research | CIM:Insights — Professional | Intermediate | Self-reported (unverified) |
| **--- Behavioral & Soft Skills ---** | | | |
| Leadership | — | Advanced | Inferred from role: managed 12-person team at Acme Corp (3 yrs); Slack: decision-making patterns |
| Cross-functional Collaboration | — | Advanced | Inferred from comms: coordinated across 4 departments; 3 cross-team projects |
| Mentoring | — | Intermediate | GitHub: 15 PRs reviewed for junior devs; Slack: mentoring conversations identified |
| Communication (Written) | — | Expert | Dev.to: 25 articles; 3 whitepapers authored; clear technical documentation |
| Communication (Verbal) | — | Intermediate | Self-reported: conference talks, client presentations |
| Problem Solving | — | Advanced | Stack Overflow: 200+ answers; GitHub: complex issue resolutions |
| Adaptability | — | Advanced | Inferred from role: 3 industry transitions across career; multi-stack proficiency |
| Stakeholder Management | — | Intermediate | Inferred from role: "Product Manager" at Beta Inc; email: client correspondence |
| Conflict Resolution | — | Intermediate | Inferred from comms: mediation patterns in team discussions |
| Time Management | — | Advanced | Inferred from role: concurrent project delivery across 2 teams |

[Replace the above examples with actual data. Include ALL skills identified from every
source. Order by level (Expert → Beginner), then alphabetically within each level.]

### Professional Skills Framework Mapping

Every skill in the resume MUST be mapped to the appropriate **professional skills framework**
based on the person's profession/industry. The framework is selected automatically based on
the person's job title, industry, and role history. If a person spans multiple domains, use
multiple frameworks.

**Framework selection is defined in the `skills-frameworks` vocabulary** (see
`skills-frameworks/SKILL.md`). Consult that vocabulary for the full framework reference,
skill codes, level definitions, and mapping rules.

**Framework selection logic:**

| Profession / Domain | Primary Framework | Reference |
|---|---|---|
| IT / Software / Digital | **SFIA 9** (Skills Framework for the Information Age) | sfia-online.org |
| Project Management | **PMI Talent Triangle** + **IPMA ICB4** | pmi.org / ipma.world |
| Finance / Accounting | **CFA Body of Knowledge** + **ACCA Competency Framework** | cfainstitute.org / accaglobal.com |
| Marketing / Digital Marketing | **CIM Professional Marketing Competencies** | cim.co.uk |
| Human Resources | **SHRM Competency Model** + **CIPD Profession Map** | shrm.org / cipd.org |
| Sales | **MEDDIC/MEDDPICC** competencies + **Sandler Selling System** | — |
| Data Science / AI | **EDISON Data Science Framework (DS-BoK)** | edison-project.eu |
| Cybersecurity | **NICE Workforce Framework (NIST SP 800-181r1)** | niccs.cisa.gov |
| Cloud / DevOps | **SFIA 9** (primary) + cloud provider skill frameworks | sfia-online.org |
| Design / UX | **UXPA Body of Knowledge** + **IxDA Competencies** | uxpa.org |
| Healthcare IT | **AMIA Health Informatics Competencies** | amia.org |
| Legal | **SRA Competence Statement** (UK) / **ABA Competencies** (US) | sra.org.uk / americanbar.org |
| Supply Chain / Logistics | **ASCM (APICS) Body of Knowledge** | ascm.org |
| Engineering (non-software) | **UK-SPEC / EUR-ING Competence Standards** | engc.org.uk |
| Education / Training | **UNESCO ICT Competency Framework for Teachers** | unesco.org |
| Product Management | **Product Management Competency Framework (Pragmatic Institute)** | pragmaticinstitute.com |
| General / Cross-functional | **European e-Competence Framework (e-CF 4.0)** | ecompetences.eu |

**How the framework column works in the skills table:**
- The **SFIA Mapping** column header adapts to the selected framework:
  `SFIA Mapping` → `Framework Mapping` (generic) or the specific framework name
- Format: `[FRAMEWORK_CODE] — Level [N]` (e.g., `SFIA:PROG — Level 5` or `NICE:SP-DEV-001 — Advanced`)
- If a skill maps to multiple frameworks (e.g., a data scientist who also does project management),
  list both: `SFIA:DTAN — Level 4; EDISON:DA — Level 3`
- If no framework applies to a particular skill, use `—` in the column

**How to determine the framework mapping:**
1. Detect the person's primary profession from their job title and role history
2. Select the appropriate framework(s) from `skills-frameworks/SKILL.md`
3. For each skill, find the closest code/competency in the selected framework
4. Map the proficiency level to the framework's level system using evidence
5. If the person spans multiple professions, apply multiple frameworks as needed
6. **If no framework exists for the person's industry**, follow the protocol in
   `skills-frameworks/SKILL.md` Section 13: inform the user, ask if they have a preferred
   framework, and use Universal Proficiency Levels as fallback

**Mandatory framework attribution:** The Skills section MUST always include:
```
**Skills evaluated per:** [Framework Name] ([reference URL or source])
```
This makes it transparent to any resume reader which standard was used for skill assessment.
If multiple frameworks are used, list all of them.

### Skill Categories

The skills table MUST include **both technical and behavioral skills**. Group them clearly:

**Technical Skills** — tools, technologies, programming languages, methodologies, domain-specific
knowledge (e.g., Python, Kubernetes, Financial Modeling, Machine Learning)

**Behavioral & Soft Skills** — interpersonal, leadership, cognitive, and professional competencies.
These are equally important to employers and must be included with the same rigor of evidence.

Common behavioral skills to look for and include:
| Category | Skills to identify |
|---|---|
| **Leadership** | Team leadership, people management, vision-setting, decision-making, delegation |
| **Communication** | Written communication, verbal communication, presentation, public speaking, active listening |
| **Collaboration** | Cross-functional collaboration, teamwork, stakeholder management, partnership building |
| **Problem Solving** | Analytical thinking, critical thinking, creative problem solving, root cause analysis |
| **Mentoring & Coaching** | Peer mentoring, junior developer coaching, knowledge sharing, onboarding |
| **Adaptability** | Learning agility, career transitions, multi-domain proficiency, change management |
| **Conflict Resolution** | Negotiation, mediation, de-escalation, consensus building |
| **Time & Project Management** | Prioritization, deadline management, multitasking, planning |
| **Client & Stakeholder Relations** | Client management, expectation setting, relationship building, account management |
| **Emotional Intelligence** | Empathy, self-awareness, social awareness, relationship management |
| **Innovation & Creativity** | Ideation, design thinking, experimentation, prototyping |
| **Ethics & Integrity** | Professional ethics, compliance awareness, responsible AI, data privacy |

**The soft skills evidence challenge:**

Unlike technical skills (which have clear proof: repos, certs, packages), soft/behavioral
skills are inherently difficult to prove. They live primarily in **interpersonal interactions**
— chats, emails, phone calls, meetings, and day-to-day collaboration. This data is:
- Often locked in corporate systems (Slack, Teams, email) — inaccessible after leaving
- Inherently personal and privacy-sensitive
- Rarely captured in structured, verifiable formats

**Solution: Anonymized communication analysis.**

When users provide communication data (chat exports, emails, call transcripts), the skill
MUST **anonymize all non-personal content** before analysis. This means:

1. **Strip all PII** from the communication data before processing:
   - Replace names of other people with anonymized labels (`[Colleague-1]`, `[Client-A]`)
   - Remove email addresses, phone numbers, and identifying details of third parties
   - Redact company-confidential information (revenue figures, unreleased product names, etc.)
   - Preserve ONLY the behavioral patterns, language style, and professional signals

2. **What to analyze (anonymized behavioral signals):**
   - **Leadership language**: "I'll take ownership of...", "Let me coordinate with...",
     "I've decided we should..." → Leadership, Decision-Making
   - **Mentoring patterns**: "Here's how this works...", "Let me walk you through...",
     code review feedback → Mentoring, Knowledge Sharing
   - **Conflict resolution**: "I understand your concern...", "Let's find a middle ground...",
     mediation in disagreements → Conflict Resolution, Negotiation
   - **Collaboration signals**: Cross-channel/cross-team participation, tagging patterns,
     response time, helping behavior → Collaboration, Teamwork
   - **Communication quality**: Clarity, structure, empathy in messages → Communication skills
   - **Problem-solving patterns**: Root cause analysis discussions, debugging conversations,
     "Here's what I found..." → Analytical Thinking, Problem Solving
   - **Client management**: Professional tone, expectation setting, status updates →
     Client Relations, Stakeholder Management
   - **Initiative signals**: Proactively raising issues, volunteering for tasks, suggesting
     improvements → Initiative, Ownership

3. **What NOT to retain or include in the resume:**
   - Specific conversation content or quotes (even anonymized)
   - Names or identifying details of colleagues, clients, or partners
   - Proprietary business information
   - Any content the user asks to exclude

4. **Proof labels for communication-derived skills:**
   Use the label: `Evidenced from [X] anonymized [platform] interactions ([date range])`
   - Example: `Evidenced from 500+ anonymized Slack messages (Jan 2024 – Dec 2025)`
   - Never cite specific messages or conversations

**Primary sources for soft skill evidence (ranked by reliability):**

| Source | Reliability | What it proves | Privacy handling |
|---|---|---|---|
| **Verifiable Credentials (behavioral endorsements)** | Highest | Third-party attested soft skills | No anonymization needed — already structured |
| **360-degree review exports** | High | Multi-perspective behavioral assessment | Anonymize reviewer names; retain scores and themes |
| **Chat/messaging exports (Slack, Teams, WhatsApp)** | Medium-High | Real-world behavioral patterns at scale | Full PII anonymization required; analyze patterns only |
| **Email archives** | Medium-High | Professional communication, client relations, project coordination | Full PII anonymization required; analyze patterns only |
| **Phone call transcripts** | Medium | Verbal communication, negotiation, client rapport | Full PII anonymization required; analyze patterns only |
| **Meeting notes / transcripts** | Medium | Facilitation, presentation, collaboration | Full PII anonymization required; analyze patterns only |
| **Performance review excerpts** | Medium | Manager-assessed behavioral competencies | Anonymize manager name; retain assessment content |
| **Code review comments (GitHub PRs)** | Medium | Mentoring, collaboration, communication quality | Partially public already; anonymize if requested |
| **Recommendation letters** | Medium | Third-party character and competency endorsement | Include with user permission |
| **Role titles and tenure** | Low-Medium | Implies leadership, management, progression | No anonymization needed — public data |
| **Self-reported** | Low | User's own perception of soft skills | No anonymization needed; mark as self-reported |

**Proactively ask for soft skill evidence:**
Since soft skills are the hardest to prove but among the most valued by employers, the skill
should explicitly ask users:

> "Soft skills like leadership, communication, and collaboration are highly valued but hard
> to prove from public profiles alone. To strengthen your behavioral skills section, consider
> providing any of the following (all content will be anonymized — no personal details of
> others will appear in your resume):
>
> - [ ] Slack/Teams/Discord chat exports (I'll analyze communication patterns, not content)
> - [ ] Email samples or archives (anonymized analysis only)
> - [ ] Phone call transcripts or meeting notes
> - [ ] Performance review excerpts or 360-feedback summaries
> - [ ] Recommendation letters or peer endorsements
> - [ ] Any behavioral assessment results (DISC, MBTI, StrengthsFinder, etc.)
>
> You can also simply describe your soft skills and I'll include them as self-reported."

**How to extract behavioral skills from available data:**
- **Role titles**: "Manager" / "Director" / "Lead" → Leadership, People Management, Decision-Making
- **Team size managed**: Infer leadership and delegation scope
- **Career transitions**: Multiple industries or role types → Adaptability, Learning Agility
- **Chat/email data (anonymized)**: Language patterns reveal collaboration, mentoring, conflict resolution
- **Published writing**: Articles/talks → Communication (Written), Thought Leadership
- **Code reviews (GitHub)**: PR reviews → Mentoring, Code Quality Advocacy
- **Stack Overflow answers**: → Knowledge Sharing, Communication (Written), Problem Solving
- **Cross-team projects**: → Cross-functional Collaboration, Stakeholder Management
- **Client-facing roles**: → Client Relations, Negotiation, Presentation Skills
- **360/performance reviews**: Direct assessment of behavioral competencies
- **Behavioral assessments**: DISC, MBTI, StrengthsFinder, Hogan → personality-aligned skill framing
- **Self-reported**: Ask the user about soft skills directly — these are often under-represented
  in platform data but highly valued by employers

### Skill Level Definitions

Determine each skill's proficiency level using the evidence hierarchy below. Use the
**highest level supported by available evidence** — never over-claim.

**Technical skills:**

| Level | Criteria | Typical evidence |
|---|---|---|
| **Expert** | Deep, authoritative command. Recognized by others in the field. 5+ years of sustained, primary use. | VC-verified expert endorsement; top 1% Stack Overflow tag; 10+ major repos in this tech; patent using this skill; published papers/talks; senior/lead role title explicitly using this skill |
| **Advanced** | Strong proficiency. Can architect, mentor, and handle complex problems. 3–5 years of regular use. | VC-verified advanced assessment; professional certification (CKA, AWS SA Pro, etc.); 5+ repos with significant commits; Stack Overflow top 10% tag; 3+ years in role requiring this skill |
| **Intermediate** | Solid working knowledge. Can deliver independently. 1–3 years of use. | VC-verified intermediate assessment; foundational certification (AWS CCP, AZ-900, etc.); 2+ repos; Stack Overflow answers in this tag; 1–3 years in role using this skill; articles authored on topic |
| **Beginner** | Foundational understanding. Can contribute with guidance. <1 year of use. | Mentioned in 1–2 repos; coursework or bootcamp certs; minor chat/document references; self-reported with no corroborating evidence |

**Behavioral & soft skills:**

| Level | Criteria | Typical evidence |
|---|---|---|
| **Expert** | Recognized authority. Shapes organizational culture around this competency. Coaches others at scale. | VC-verified leadership endorsement; 5+ years managing large teams; keynote speaker; authored books/courses on leadership/communication; recognized mentor across organizations |
| **Advanced** | Consistently demonstrates at high level. Trusted to lead complex interpersonal situations. | 3+ years in management/leadership roles; cross-functional project leadership; pattern of conflict resolution in comms; strong PR review/mentoring record |
| **Intermediate** | Reliably applies in professional settings. Contributes positively to team dynamics. | 1–3 years in collaborative roles; evidence of mentoring juniors; client-facing experience; team project participation |
| **Beginner** | Developing awareness. Applies with guidance in structured settings. | Early-career roles; team participation without leadership; self-reported development goals |

### Proof Source Labels

Every proof in the Proof column MUST include a **credibility tier prefix** `[S]` through `[G]`
as defined in `skills-frameworks/SKILL.md` Section 15 (Verifier Credibility Hierarchy).

**Key rule: Publicly verifiable information = Tier [S] = no verification needed.**
If anyone can confirm the claim by visiting a public URL, it is self-evident truth.

| Tier | Source type | Label format |
|---|---|---|
| **[S]** | Public record (GitHub, patents, papers, packages, SO) | `[S] GitHub: [X] repos, [Y] commits` |
| **[S]** | Published writing (public articles, books) | `[S] [Platform]: [X] articles, [Y] reactions` |
| **[S]** | Granted patents | `[S] Patent US[Number]` |
| **[A]** | Verified by accredited institution (university, govt) | `[A] Verified by [Institution]` |
| **[B]** | Verified by employer (HR, manager VC) | `[B] Verified by [Company] HR ([Credential])` |
| **[C]** | Certified by industry body (AWS, PMI, CNCF, Cisco) | `[C] Certified by [Body] ([Cert Name], [Date])` |
| **[C]** | Verifiable Credential (cryptographically verified) | `[C] VC verified by [Issuer] ([Credential], [Date])` |
| **[C]** | Platform certification (Credly, cloud certs) | `[C] Credly badge: [Cert Name] ([Date])` |
| **[D]** | Assessment platform score | `[D] Assessed by [Platform] (Score: [X])` |
| **[E]** | Named peer endorsement | `[E] Endorsed by [Name, Title at Company]` |
| **[F]** | Community signal | `[F] Stack Overflow: top [X]% [tag]; GitHub: [Y] stars` |
| **[F]** | Chat/email inferred (anonymized) | `[F] Evidenced from [X] anonymized [platform] interactions` |
| **[F]** | Role-inferred | `[F] Inferred from role: "[Title]" at [Company] ([Duration])` |
| **[F]** | Document-inferred | `[F] Inferred from authored: "[Document Title]" |
| **[G]** | Self-reported | `[G] Self-reported (unverified)` |

### Multi-source Skill Aggregation

When a skill appears in multiple sources, **combine the evidence** to determine the level:
- A skill verified by VC always takes the VC level, regardless of other evidence
- Without VCs, combine evidence: e.g., GitHub (3 repos) + Stack Overflow (top 15%) +
  2 years in role → Advanced
- List all proof sources separated by semicolons in the Proof column
- Example: `GitHub: 8 repos, 200+ commits; Stack Overflow: top 8% tag; Verified by CNCF (CKA, Jan 2025)`

---

## Technical Profile — GitHub (only if GitHub data was collected)

**GitHub:** [URL] | **Repositories:** [count] | **Followers:** [count]

[Bio, if available]

### Key Repositories
- **[repo-name]** — [description] | [stars] stars
- **[repo-name]** — [description] | [stars] stars
[Top 3–5 by stars or recent activity]

### Languages & Technologies
[Comma-separated, extracted from repos and activity]

---

## Container & DevOps Profile — Docker Hub (only if Docker data was collected)

**Docker Hub:** [URL]

### Published Images
- **[image-name]** — [description] | [pulls] pulls
- **[image-name]** — [description] | [pulls] pulls
[Top 3–5 by pull count]

---

## Developer Community — Stack Overflow (only if SO data was collected)

**Stack Overflow:** [URL] | **Reputation:** [score] | **Badges:** [gold] gold, [silver] silver, [bronze] bronze

### Top Expertise Areas
[Comma-separated list of top tags by score]

---

## Open Source Packages — npm / PyPI (only if package data was collected)

### npm Packages
- **[package-name]** — [description] | [weekly downloads] downloads/week
[Top packages by downloads]

### PyPI Packages
- **[package-name]** — [description] | [version]
[Top packages]

---

## Technical Writing — Dev.to / Medium (only if writing data was collected)

**[Platform]:** [URL]

### Featured Articles
- **[article title]** — [reactions/claps count] | [published date]
- **[article title]** — [reactions/claps count] | [published date]
[Top 3–5 articles by engagement]

---

## Design Portfolio — Behance / Dribbble (only if design data was collected)

**[Platform]:** [URL]

### Featured Projects
- **[project name]** — [description] | [views/likes]
[Top 3–5 projects by engagement]

---

## Publishing & Content — WordPress (only if WordPress data was collected)

**Site:** [URL]

### Recent Publications
- **[post title]** — [published date]
- **[post title]** — [published date]
[Top 3–5 recent posts]

---

## Data Science — Kaggle (only if Kaggle data was collected)

**Kaggle:** [URL]

### Competitions & Notebooks
- **[competition/notebook name]** — [ranking/votes]
[Top entries by engagement]

---

## Publications & Authored Work (only if documents were provided)

### Published Work
- **[document/paper title]** — [type: whitepaper/article/paper] | [date if known]
- **[document/paper title]** — [type] | [date if known]
[List authored documents, ordered by relevance or date]

### Expertise Areas (from authored work)
[Comma-separated list of subject matter areas demonstrated in the documents,
tagged as "(inferred from authored work)"]

---

## Communication & Collaboration Profile (only if chat/email data was provided)

### Professional Communication
- **Platforms analyzed:** [Slack, Email, Teams, etc.]
- **Key discussion domains:** [comma-separated topics frequently discussed]
- **Collaboration patterns:** [e.g., cross-functional coordination, technical mentoring,
  client-facing communication]

### Inferred Skills (from communications)
[Comma-separated list of skills identified from chat/email content,
tagged as "(inferred from communications)"]

---

## Patents (only if patent data was collected)

- **[Patent Title]** — US Patent [Number] | Filed: [Date] | Granted: [Date]
  Co-inventors: [names if available]
- **[Patent Title]** — US Patent [Number] | Filed: [Date] | Granted: [Date]
[List all patents found]

---

## Certifications (only if certification data was collected)

- **[Certification Name]** — [Issuing Organization] | [Date] | [Verification URL if available]
- **[Certification Name]** — [Issuing Organization] | [Date]
[List all verified certifications]

---

## Credential Verification Status

| Resume Item | Status | Issuer | Verified On |
|---|---|---|---|
| [Job Title] at [Company] | Verified | [Company HR / VC Issuer] | [Date] |
| [Degree] from [University] | Verified | [University Registrar] | [Date] |
| [Certification Name] | Verified | [Cert Body] | [Date] |
| [Skill: Python] | Verified | [Endorser / Assessment Platform] | [Date] |
| [Job Title] at [Company] | Unverified | — | — |
[List all resume items with their verification status. Show verified items first,
then unverified items. This section provides a trust transparency layer.]
```

**Note:** Only include the platform-specific sections for which data was actually collected.
Omit all others entirely.

---

## Important Rules

1. **Never fabricate data.** If a field is not available from the enrichment or platform API,
   omit it entirely. Do not guess job responsibilities, achievements, metrics, or skills that
   are not supported by the retrieved data.

2. **Respect credit costs.** Profile enrichment and contact enrichment consume credits. Always
   show the cost estimate to the user and wait for confirmation before running enrichments.

3. **Privacy awareness.** Resumes contain personal information. Remind the user that the
   generated resume is based on publicly available profile data and should be used responsibly
   and in compliance with applicable privacy regulations.

4. **Date formatting.** Use "MMM YYYY" format (e.g., "Jan 2020") for dates. If only a year
   is available, use the year alone. If no dates are available for a role, use "Dates not
   available."

5. **Presentation order.** Always present sections in this order: Header, Summary, Experience,
   Education, Skills, Platform Portfolios (GitHub, Docker, SO, npm/PyPI, Dev.to/Medium,
   Behance/Dribbble, WordPress, Kaggle), Publications & Authored Work, Communication &
   Collaboration Profile, Patents, Certifications. If a section has no data, omit it entirely
   rather than showing an empty section.

6. **Multiple profiles.** If the user provides multiple platform URLs for the **same person**,
   combine all portfolio data into a single resume. If the user asks for resumes for
   **different people**, process them sequentially and confirm each enrichment cost separately.

7. **Multiple platform URLs.** When the user provides URLs from several platforms:
   - Use the LinkedIn URL (if present) as the primary identifier for `match-prospects`
   - Use other platform URLs for portfolio sections
   - Cross-reference names across platforms to confirm they belong to the same person
   - If names don't match across platforms, alert the user before proceeding

8. **Refinement.** After presenting the resume, proactively offer:
   - Adjusting the professional summary tone (e.g., more technical, more executive)
   - Reordering or emphasizing certain roles or portfolio sections
   - Adding a specific skills section focus
   - Removing platform sections the user doesn't want
   - Saving the resume to a file

9. **Unsupported platforms.** If the user provides a URL from a platform not listed in
   Tier 2, attempt a Tier 3 (WebFetch) resolution. If the page is not publicly accessible
   or returns no useful data, inform the user and suggest alternative platforms.

---

## Error Handling

| Scenario | Action |
|---|---|
| No match found (with portfolio data) | Offer portfolio-only resume; suggest LinkedIn URL for full resume |
| No match found (no portfolio data) | Ask user to verify input; suggest LinkedIn URL, email, or name+company |
| Multiple matches | Present options with name, title, and company; ask user to pick |
| Enrichment returns sparse data | Generate resume with available data; note which sections are incomplete |
| Enrichment cost too high | Show cost estimate; suggest matching only (free) for basic info |
| URL is malformed | Ask user to verify the URL format |
| Platform API rate limited | Inform user; skip that platform's portfolio section; proceed with others |
| Platform page not publicly accessible | Inform user; suggest alternative profile URL or platform |
| Profile has no name or email | Ask user for additional identifiers (LinkedIn, email, name) |
| Names don't match across platforms | Alert user; ask to confirm the profiles belong to the same person |

---

## Example Interactions

### Example 1 — LinkedIn URL

**User:** Create a resume from https://www.linkedin.com/in/janedoe

**Skill workflow:**
1. Call `match-prospects` with `linkedin: "https://www.linkedin.com/in/janedoe"`
2. Match found → call `enrich-prospects` with `["enrich-prospects-profiles"]`
3. Show cost estimate → user confirms
4. Receive enriched data (name, 3 roles, 1 education entry, location)
5. Generate and present resume in Markdown format
6. Offer refinements

### Example 2 — GitHub URL

**User:** Build a resume from https://github.com/jdoe

**Skill workflow:**
1. Fetch `https://api.github.com/users/jdoe` → name ("Jane Doe"), email, company ("Acme"),
   bio, 42 repos, 150 followers
2. Fetch `https://api.github.com/users/jdoe/repos?sort=stars&per_page=5` → top repos
3. Call `match-prospects` with `full_name: "Jane Doe"` + `company_name: "Acme"`
4. Match found → call `enrich-prospects` with `["enrich-prospects-profiles"]`
5. Show cost estimate → user confirms
6. Generate resume with standard sections + Technical Profile (GitHub) section
7. Offer refinements

### Example 3 — Multiple Platforms

**User:** Create a resume using https://www.linkedin.com/in/janedoe and https://github.com/jdoe
and https://stackoverflow.com/users/12345/jdoe

**Skill workflow:**
1. Resolve GitHub: fetch API → extract repos, languages, bio
2. Resolve Stack Overflow: fetch API → extract reputation, badges, top tags
3. Match via LinkedIn (primary): `match-prospects` with `linkedin` URL
4. Enrich → show cost → user confirms
5. Generate resume with: Experience, Education, Skills + GitHub section + Stack Overflow section
6. Offer refinements

### Example 4 — Non-LinkedIn, No Match

**User:** Build a resume from https://github.com/newdev123

**Skill workflow:**
1. Fetch GitHub API → name ("Alex Dev"), no email, no company, bio, 12 repos
2. Call `match-prospects` with `full_name: "Alex Dev"` → no match
3. Offer: "I couldn't find a professional profile match. I can generate a portfolio-based
   resume from your GitHub data, or you can provide a LinkedIn URL or email for a fuller resume."
4. User says "go with GitHub only"
5. Generate portfolio-only resume with: name, bio as summary, GitHub Technical Profile section,
   Skills from repo languages
6. Offer refinements

---

Maintained by Autonomyx. Last updated: March 2026.
