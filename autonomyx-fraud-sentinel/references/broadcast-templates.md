# Autonomyx Fraud Sentinel — Broadcast Templates

> Customise these per event. Replace [BRACKETS] with real values.
> Always adjust tone to audience. Never share evidence details publicly.

---

## END USERS (In-app / Email)

**Subject:** ⚠️ Fraud Alert — Protect Your Account

**Body:**
We've detected suspicious activity on [PLATFORM] that may affect you.

A [PATTERN_DESCRIPTION] has been identified involving [IDENTITY_DESCRIPTION — no PII unless legally cleared].

**What to do:**
- Do not respond to unexpected messages asking for payments or personal details.
- If you received a message from [identity/account], do not act on it.
- Report anything suspicious using the button below.
- Change your password if you shared any credentials recently.

We are actively investigating and will keep you updated.

— The [PLATFORM] Safety Team

---

## GENERAL PUBLIC (Social Media — Twitter/X, LinkedIn, Facebook)

**Headline:** 🚨 Fraud Alert on [PLATFORM]

**Body (short form — Twitter/X):**
We've identified a fraud pattern on [PLATFORM]: [1-sentence plain description].
If you receive [BEHAVIOUR_DESCRIPTION], don't engage. Report it here: [LINK] #FraudAlert #StaySafe

**Body (long form — LinkedIn/Facebook):**
Our fraud detection system has flagged suspicious activity on [PLATFORM].

Pattern detected: [PATTERN_NAME]
What it looks like: [PLAIN ENGLISH DESCRIPTION — no technical jargon]

How to protect yourself:
✅ Verify before you act — especially on urgent requests
✅ Never share OTPs, passwords, or payment details via chat
✅ Report suspicious accounts using [REPORT_LINK]

We take fraud seriously. Our team is actively investigating. Stay safe.

---

## SUBSCRIBED WATCHERS / ADMINS (Email / Webhook)

**Subject:** [RISK_LEVEL] Fraud Event Detected — Event ID [EVENT_ID]

**Body:**
A fraud event has been recorded by Autonomyx Fraud Sentinel.

| Field | Value |
|-------|-------|
| Event ID | [EVENT_ID] |
| Pattern | [PATTERN_ID] — [PATTERN_NAME] |
| Platform | [PLATFORM] |
| Identity | [IDENTITY_ID] |
| Risk Level | [RISK_LEVEL] |
| Confidence | [CONFIDENCE]% |
| Detected At | [TIMESTAMP] |
| Status | [STATUS] |

**Matched Indicators:**
[LIST OF MATCHED INDICATORS]

**Recommended Actions:**
[ACTION_CHECKLIST]

**Access Block Issued:** [YES / NO / PENDING_AGENT]

This is an automated alert from Autonomyx Fraud Sentinel. Log in to the dashboard to review full evidence.

---

## INTERNAL TEAM (Slack / Internal Webhook)

**Format:** Single structured message

🚨 *Fraud Sentinel Alert* | Risk: *[RISK_LEVEL]* | Confidence: *[CONFIDENCE]%*

> *Event:* [EVENT_ID]
> *Pattern:* [PATTERN_ID] — [PATTERN_NAME]
> *Platform:* [PLATFORM] | *Identity:* [IDENTITY_ID]
> *Detected:* [TIMESTAMP]
> *Block Issued:* [YES/NO/PENDING]

*Evidence:* [RAW_EVIDENCE_SUMMARY — full detail in SurrealDB]

*Action Required:* [TOP 1-2 IMMEDIATE ACTIONS]
cc: @fraud-team @platform-[PLATFORM]-lead

---

## GOVERNMENT & LOCAL AUTHORITIES (Formal Email / Official Report)

**Subject:** Official Fraud Report — [PLATFORM] — Ref: [EVENT_ID]

**Body:**

Dear [AUTHORITY_NAME / Sir/Madam],

We are writing to formally report a fraud incident detected on [PLATFORM], operated by [COMPANY_NAME].

**Incident Reference:** [EVENT_ID]
**Date/Time Detected:** [TIMESTAMP]
**Nature of Fraud:** [PATTERN_NAME — plain English description]
**Platform:** [PLATFORM]
**Affected Parties:** [NUMBER/DESCRIPTION — no PII without legal clearance]
**Risk Classification:** [RISK_LEVEL]

**Summary of Evidence:**
[2–4 sentence factual summary. Attach full evidence package separately.]

**Actions Taken:**
- Access suspended for flagged identity: [YES/NO]
- Affected users notified: [YES/NO]
- Internal investigation initiated: [YES/NO]

We are prepared to cooperate fully with any investigation and can provide full technical evidence
upon request. Please direct correspondence to [CONTACT_EMAIL] referencing the incident number above.

Yours sincerely,
[SIGNATORY NAME]
[TITLE], [COMPANY_NAME]
[DATE]

---

> 📌 Add new audience templates below this line as new broadcast channels are onboarded.
