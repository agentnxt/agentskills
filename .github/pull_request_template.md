## Summary

Describe the skill registry change in 2-3 sentences.

## Type of change

- [ ] New skill
- [ ] Skill update
- [ ] Documentation update
- [ ] Registry metadata/schema update
- [ ] Security or permissions update
- [ ] Bug fix

## Skill checklist

For new or updated skills:

- [ ] Skill lives under `skills/<skill-id>/`
- [ ] `SKILL.md` is present
- [ ] `skill.json` is present
- [ ] `skill.json` id matches the folder name
- [ ] README explains setup and usage when needed
- [ ] Runtime requirements are documented
- [ ] Required secrets are listed by environment variable name only
- [ ] Permissions are accurate and least-privilege
- [ ] Prompt-injection or external-content risks are documented when relevant
- [ ] Changelog is updated when relevant
- [ ] `registry.json` was regenerated

## Validation

Commands run:

```bash
npm run validate:registry
npm run build:index
# add any skill-specific commands here
```

## Runtime requirements

- Runtime:
- Required APIs, MCP servers, databases, or services:
- Required environment variables:
- Supported platforms:

## Security notes

Explain any network access, filesystem access, shell execution, browser automation, credential usage, external content ingestion, or prompt-injection concerns.

## Examples

Add sample prompts, outputs, screenshots, or logs if useful.

## Follow-up work

List known limitations or planned improvements.
