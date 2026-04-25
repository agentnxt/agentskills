"""Code Review skill for CrewAI agents."""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class CodeReviewInput(BaseModel):
    code: str = Field(description="Code to review")
    language: str = Field(default="python", description="Programming language")
    focus: str = Field(default="all", description="Focus area: security, performance, style, all")


class CodeReviewTool(BaseTool):
    name: str = "code_review"
    description: str = "Review code for bugs, security issues, performance problems, and style."
    args_schema: Type[BaseModel] = CodeReviewInput

    def _run(self, code: str, language: str = "python", focus: str = "all") -> str:
        checks = []

        if focus in ("all", "security"):
            checks.extend(self._check_security(code, language))
        if focus in ("all", "performance"):
            checks.extend(self._check_performance(code, language))
        if focus in ("all", "style"):
            checks.extend(self._check_style(code, language))

        if not checks:
            return "No issues found. Code looks good."

        return "## Code Review Findings\n\n" + "\n".join(
            f"- **[{c['severity']}]** {c['message']}" for c in checks
        )

    def _check_security(self, code: str, language: str) -> list:
        issues = []
        patterns = {
            "python": [
                ("eval(", "Avoid eval() - use ast.literal_eval() for safe parsing"),
                ("exec(", "Avoid exec() - potential code injection"),
                ("os.system(", "Use subprocess.run() instead of os.system()"),
                ("pickle.loads", "Pickle deserialization can execute arbitrary code"),
                ("shell=True", "shell=True in subprocess is a security risk"),
            ],
            "javascript": [
                ("eval(", "Avoid eval() - potential code injection"),
                ("innerHTML", "Use textContent instead of innerHTML to prevent XSS"),
                ("document.write", "Avoid document.write - potential XSS"),
            ],
        }
        for pattern, msg in patterns.get(language, patterns["python"]):
            if pattern in code:
                issues.append({"severity": "SECURITY", "message": msg})
        return issues

    def _check_performance(self, code: str, language: str) -> list:
        issues = []
        if language == "python":
            if "for " in code and ".append(" in code:
                issues.append({"severity": "PERF", "message": "Consider list comprehension instead of loop + append"})
            if "import *" in code:
                issues.append({"severity": "PERF", "message": "Wildcard imports slow down module loading"})
        return issues

    def _check_style(self, code: str, language: str) -> list:
        issues = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({"severity": "STYLE", "message": f"Line {i} exceeds 120 characters"})
        if not any(line.strip().startswith(('"""', "'''", "#")) for line in lines[:5]):
            issues.append({"severity": "STYLE", "message": "Missing module-level docstring"})
        return issues
