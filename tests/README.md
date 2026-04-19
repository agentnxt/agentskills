SEO Skill Test Harness

Overview
- A minimal end-to-end harness to sanity-check the agentic-seo skill core workflow using mock tool outputs.

How to use
- Run the mock audit script against a sample URL to verify output shape and fields.
- Expected outputs are JSON with sections: url, technical, on_page, content, summary.

Next steps
- Extend harness to exercise additional tool substitutions (local vs GBP data etc).
- Integrate with CI to run on PRs.
- Expected outputs are JSON with sections: url, technical, on_page, content, summary.
- The health-checks module can validate these sections and provide a pass/fail.
- You can run tests/mock_audit.py and pipe into checks to validate:

```
python tests/mock_audit.py https://example.com | jq  # produce audit json
python - <<'PY'
from tests.mock_audit import mock_audit
from tools.seo_checks import run_checks
aud = mock_audit("https://example.com")
print(run_checks(aud))
PY
```
