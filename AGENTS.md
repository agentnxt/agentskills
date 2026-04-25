# Repository Agent Instructions

Scope: entire repository.

This repository follows the shared OpenAutonomyX instruction layer in `openautonomyx/common-instructions` and is scoped to AgentNxt skill registry documentation and skill metadata.

## Documentation-only alignment rule

For documentation alignment tasks, update README files, docs, examples, registry metadata, and repo-level guidance only. Do not change implementation code unless a human maintainer explicitly requests it.

## Shared references

Use these shared references as the default baseline:

- `standards/engineering-execution-standard.md`
- `policies/context-and-guardrails-policy.md`
- `policies/test-and-process-improvement-policy.md`
- `policies/airgapped-operation-policy.md`

Do not duplicate shared policies or reusable prompt packs here. Reference them and add only registry-specific guidance.

## In scope

- Skill registry documentation
- Skill metadata conventions
- Skill examples and usage notes
- Review notes for substantial registry changes
- Guidance for discovery, compatibility, evaluation, and maintenance

## Out of scope

- Organization-level vision or strategy source documents
- Generic shared prompts owned by `common-instructions`
- Product implementation details owned by another repository
- Large private datasets or binary model artifacts unless explicitly approved

## Documentation rules

1. Keep skill entries clear, discoverable, and version-aware.
2. Document inputs, outputs, dependencies, limitations, and examples.
3. Include compatibility and review notes for production-facing skills.
4. Prefer small, composable skill docs over large monolithic files.
5. Record substantial registry changes in `reviews/` when applicable.
6. Require reviewer approval and HITL sign-off before production-facing skill behavior changes.
