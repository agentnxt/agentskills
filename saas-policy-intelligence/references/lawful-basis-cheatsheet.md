# GDPR Lawful Basis Cheatsheet

Quick reference for evaluating policy claims about EU/EEA data processing.

## The six lawful bases (Art. 6 GDPR)

| Basis | When valid | Strength for AI training | User rights |
|---|---|---|---|
| **Consent** (Art. 6(1)(a)) | User freely gave specific, informed, unambiguous consent | Strongest — requires genuine opt-in | Right to withdraw at any time |
| **Contract** (Art. 6(1)(b)) | Processing necessary to deliver the contracted service | Valid for core product function only | Right to erasure if contract ends |
| **Legal obligation** (Art. 6(1)(c)) | Processing required by EU/member-state law | Not applicable to AI training | Limited |
| **Vital interests** (Art. 6(1)(d)) | Life-or-death situations | Not applicable to AI training | N/A |
| **Public task** (Art. 6(1)(e)) | Public authorities performing official tasks | Not applicable to commercial AI | Limited |
| **Legitimate interests** (Art. 6(1)(f)) | Controller's interests outweigh user rights after balancing test | Weakest for AI training — heavily contested | Right to object (Art. 21) — must be honoured |

## What "legitimate interests" actually requires

Companies claiming legitimate interest must conduct a three-part balancing test:
1. **Purpose test**: Is there a genuine legitimate interest?
2. **Necessity test**: Is processing necessary for that purpose?
3. **Balancing test**: Do the user's interests/rights override the company's interest?

For AI model training on user interaction data, regulators in the EU have increasingly
found that the balancing test fails — users have a reasonable expectation their coding
interactions won't train commercial AI models without consent.

**Key precedents**:
- Meta's attempt to use legitimate interest for ad-targeting AI was blocked by Irish DPC (2023)
- LinkedIn paused AI training on EU user data after regulatory pressure (2024)
- X/Twitter faced enforcement action from Irish DPC over Grok AI training (2024)

## Red flags in policy language

- "Legitimate interest" claimed for AI training without publishing the balancing test → challenge it
- "De-identified" data used for training → de-identification is not anonymisation under GDPR
- No mention of data subjects' right to object → potential violation of Art. 21
- "Affiliate" sharing without naming affiliates → transparency violation (Art. 13/14)
- Bundled consent (accepting ToS = accepting AI training) → invalid under GDPR Art. 7(2)

## User rights relevant to AI training (EU)

- **Right to object** (Art. 21): If legitimate interest is the basis, user can object at any time
- **Right of access** (Art. 15): Request what data has been collected
- **Right to erasure** (Art. 17): Request deletion — but note: data used to train a model
  cannot always be "un-trained"; regulators are still working out the implications
- **Right to restriction** (Art. 18): Pause processing while a dispute is resolved
