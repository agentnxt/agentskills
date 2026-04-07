# Security Certifications Reference

## SOC 2 (System and Organization Controls 2)

**What it covers:** Controls relevant to security, availability, processing integrity,
confidentiality, and privacy. Audited by a licensed CPA firm.

**Type I vs Type II:**
- Type I: Controls are *designed* appropriately at a point in time (weaker, easier)
- Type II: Controls *operated effectively* over a period (typically 6–12 months) — this is the standard to ask for

**How to verify:** Ask the vendor for their SOC 2 Type II report under NDA. Reports are
not public but should be shared with enterprise prospects. The report includes:
- Audit period (check it's recent, ideally within 12 months)
- Scope (which systems and services are in scope — critical)
- Exceptions noted (even a clean report can have qualifications)

**Red flags:**
- Vendor claims SOC 2 but won't share the report
- Report is Type I only
- Scope excludes the product/service you actually use
- Audit period ended >18 months ago

---

## ISO 27001

**What it covers:** Information security management system (ISMS). International standard,
broader than SOC 2 in some areas, narrower in others.

**How to verify:** Certificate should list the issuing accreditation body and scope.
Check the accreditation body's public registry:
- BSI: bsigroup.com/en-GB/validate-bsi-issued-certificates/
- Bureau Veritas: certificateverification.bureauveritas.com
- DNV: certifier.dnv.com

**Red flags:**
- Certificate expired or scope too narrow
- Issuing body not accredited by IAF (International Accreditation Forum) member

---

## FedRAMP (Federal Risk and Authorization Management Program)

**What it covers:** US federal government cloud security standard.
Three levels: Low, Moderate, High (most sensitive workloads require Moderate or High).

**How to verify:** FedRAMP Marketplace is public: marketplace.fedramp.gov
Look for: Authorization status (Authorized vs In Process vs FedRAMP Ready), impact level,
agency sponsor.

**Red flags:**
- "FedRAMP In Process" — this is not authorized, it's just started the process
- Impact level lower than required for the data being handled

---

## HIPAA BAA (Business Associate Agreement)

**What it covers:** Required for any vendor handling Protected Health Information (PHI).
A BAA is a contract, not a certification — it makes the vendor legally liable for PHI handling.

**How to verify:** Ask for the vendor's standard BAA template. Check:
- Does it cover the specific product/service you use?
- Is the vendor willing to negotiate terms?
- Is there a HIPAA-eligible tier vs standard tier?

**Red flags:**
- Vendor offers a BAA but HIPAA-eligible features are behind a higher pricing tier
- BAA scope excludes AI/ML features or data sent to third-party model providers
- Standard product sends data to model providers without a BAA chain

---

## PCI DSS (Payment Card Industry Data Security Standard)

**What it covers:** Security standards for handling credit/payment card data.
Levels 1–4 based on transaction volume. Level 1 is most rigorous (annual QSA audit).

**How to verify:** Ask for the vendor's Attestation of Compliance (AoC) or check Visa/Mastercard's
lists of compliant service providers.

---

## ISO 27701

**What it covers:** Extension to ISO 27001 covering Privacy Information Management (PIMS).
More directly relevant to GDPR compliance than ISO 27001 alone.

---

## Encryption standards quick reference

| Standard | Status | Notes |
|---|---|---|
| AES-256 | ✅ Current standard | For data at rest |
| TLS 1.3 | ✅ Current standard | For data in transit |
| TLS 1.2 | ⚠️ Acceptable | Older but still widely used |
| TLS 1.0 / 1.1 | ❌ Deprecated | Should not be in use |
| RSA-2048 | ⚠️ Acceptable | RSA-4096 preferred for new implementations |
| Customer-managed keys | ✅ Best practice | Vendor holds encrypted data, customer holds keys |

---

## Pen testing guidance

- Annual third-party penetration testing is the minimum expectation for enterprise SaaS
- Look for: testing firm named (not just "third-party"), scope, date
- Bug bounty programs (HackerOne, Bugcrowd) supplement but don't replace formal pen tests
- CVE disclosure history is searchable at: cve.mitre.org and nvd.nist.gov
