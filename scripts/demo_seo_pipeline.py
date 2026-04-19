#!/usr/bin/env python3
import json
from tests.mock_audit import mock_audit
from tools.seo_checks import run_checks


def main(url: str = "https://example.com"):
    audit = mock_audit(url)
    result = run_checks(audit)
    payload = {"audit": audit, **{k: v for k, v in result.items()}}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    main(url)
