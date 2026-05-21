"""Security scanner for SkillForge skill packs.

Performs static analysis on SKILL.md content and parsed Skill objects,
checking for prompt injection, hardcoded secrets, permission risks,
overly broad network egress, and suspicious dependencies.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from skillforge_core.models import RiskLevel as SkillRiskLevel

from .report import Finding, RiskLevel, ScanReport

if TYPE_CHECKING:
    from skillforge_core import Skill

# ──────────────────────────────────────────
# Prompt Injection patterns
# ──────────────────────────────────────────
_PROMPT_INJECTION_PATTERNS: list[tuple[str, RiskLevel, str]] = [
    (
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
        RiskLevel.CRITICAL,
        "Direct prompt injection override: '{match}' attempts to discard prior instructions.",
    ),
    (
        r"(you\s+are\s+now|act\s+as|pretend\s+you\s+are|you\s+must)\s+(DA[NND]|a\s+different\s+(ai|assistant|model|system))",
        RiskLevel.CRITICAL,
        "Role hijacking attempt: '{match}' tries to redefine the agent identity.",
    ),
    (
        r"===BEGIN===|===END===|---BEGIN|---END---|<<<BEGIN>>>|<<<END>>>",
        RiskLevel.HIGH,
        "Injection delimiter pattern '{match}' — often used to hide embedded prompts.",
    ),
    (
        r"(system\s*:\s*|system\s+prompt\s*:|system\s+message\s*:)",
        RiskLevel.HIGH,
        "System-prompt framing '{match}' — attempts to speak as the system.",
    ),
    (
        r"\[SYSTEM\]|\[HIDDEN\]|\[OVERRIDE\]|\[INJECT\]",
        RiskLevel.MEDIUM,
        "Bracketed tag '{match}' — may indicate hidden directive markers.",
    ),
    (
        r"<\|im_start\|>|<\|im_end\|>|</?system>",
        RiskLevel.MEDIUM,
        "LLM token delimiter '{match}' — could be used to inject system messages.",
    ),
    (
        r"disregard\s+(all\s+)?(safety|security|content\s+policy|guidelines?|rules?)",
        RiskLevel.CRITICAL,
        "Safety bypass attempt: '{match}' tells the model to ignore safety constraints.",
    ),
    (
        r"zero-width\s+(space|joiner|non-joiner)|&#x200[BbDd]|\\\\u200[BbDd]",
        RiskLevel.HIGH,
        "Zero-width character reference '{match}' — may be used for hidden text encoding.",
    ),
    (
        r"\bprint\s*\(\s*[\"'](.*?system.*?)[\"']\s*\)",
        RiskLevel.MEDIUM,
        "Suspicious print-debug of system instructions: '{match}'.",
    ),
    (
        r"(never\s+say\s+no|always\s+comply|obey\s+(all|every)\s+(command|instruction|order))",
        RiskLevel.HIGH,
        "Universal compliance demand '{match}' — tries to force unconditional obedience.",
    ),
]

# ──────────────────────────────────────────
# Secrets patterns
# ──────────────────────────────────────────
_SECRET_PATTERNS: list[tuple[str, RiskLevel, str]] = [
    (
        r"\b(sk-[a-zA-Z0-9]{20,60})\b",
        RiskLevel.CRITICAL,
        "OpenAI API key detected: '{match}'.",
    ),
    (
        r"\b(ghp_[a-zA-Z0-9]{36})\b",
        RiskLevel.CRITICAL,
        "GitHub personal access token detected: '{match}'.",
    ),
    (
        r"\b(github_pat_[a-zA-Z0-9_]{50,})\b",
        RiskLevel.CRITICAL,
        "GitHub fine-grained PAT detected: '{match}'.",
    ),
    (
        r"\b(AKIA[0-9A-Z]{16})\b",
        RiskLevel.CRITICAL,
        "AWS access key ID detected: '{match}'.",
    ),
    (
        r"\b(xox[baprs]-[a-zA-Z0-9-]{10,60})\b",
        RiskLevel.CRITICAL,
        "Slack token detected: '{match}'.",
    ),
    (
        r"\b(hf_[a-zA-Z0-9]{34})\b",
        RiskLevel.HIGH,
        "HuggingFace API token detected: '{match}'.",
    ),
    (
        r"\b(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b",
        RiskLevel.HIGH,
        "JWT token detected: '{match}'.",
    ),
    (
        r"-----BEGIN\s+(RSA\s+PRIVATE\s+KEY|EC\s+PRIVATE\s+KEY|PRIVATE\s+KEY|DSA\s+PRIVATE\s+KEY|OPENSSH\s+PRIVATE\s+KEY|PGP\s+PRIVATE\s+KEY\s+BLOCK)",
        RiskLevel.CRITICAL,
        "Private key PEM header detected: '{match}'.",
    ),
    (
        r"\b(password|passwd|pwd|secret|api_key|apikey|api_secret|token)\s*[:=]\s*[\"']?([^\s\"']{8,})[\"']?",
        RiskLevel.HIGH,
        "Hardcoded credential: '{match}' — value assigned to sensitive variable.",
    ),
    (
        r"(export\s+)?[A-Z_]{3,30}\s*=\s*[\"']([^\s\"']{30,})[\"']",
        RiskLevel.LOW,
        "Long environment variable assignment '{match}' — possibly a token.",
    ),
]

# ──────────────────────────────────────────
# Network egress patterns
# ──────────────────────────────────────────
_BROAD_EGRESS_PATTERNS: list[str] = [
    "*",
    "0.0.0.0",
    "0.0.0.0/0",
    "::/0",
    "all",
    "any",
]

# ──────────────────────────────────────────
# Permission risk patterns
# ──────────────────────────────────────────
_HIGH_RISK_TOOL_PATTERNS: list[tuple[str, str]] = [
    (r"\b(write|create|delete|remove|unlink|rmdir|mkdir)\b", "filesystem write"),
    (r"\b(exec|execute|run|spawn|subprocess|popen|system)\b", "process execution"),
    (r"\b(read_file|cat|open|read)\b", "filesystem read"),
    (r"\b(http|https|fetch|request|download|curl|wget)\b", "network access"),
    (r"\b(install|pip|npm|apt|brew|choco)\b", "package installation"),
    (r"\b(eval|exec|__import__|compile)\b", "code evaluation"),
]

# ──────────────────────────────────────────
# Suspicious dependency patterns
# ──────────────────────────────────────────
_SUSPICIOUS_IMPORTS: list[tuple[str, RiskLevel, str]] = [
    (
        r"\bimport\s+subprocess\b|\bfrom\s+subprocess\b",
        RiskLevel.HIGH,
        "'subprocess' import detected — allows arbitrary command execution.",
    ),
    (
        r"\bimport\s+os\b|\bfrom\s+os\b",
        RiskLevel.MEDIUM,
        "'os' module import detected — provides system-level access.",
    ),
    (
        r"\bimport\s+sys\b|\bfrom\s+sys\b",
        RiskLevel.LOW,
        "'sys' module import detected — provides interpreter-level access.",
    ),
    (
        r"\bimport\s+ctypes\b|\bfrom\s+ctypes\b",
        RiskLevel.HIGH,
        "'ctypes' import detected — allows native code execution.",
    ),
    (
        r"\bimport\s+socket\b|\bfrom\s+socket\b",
        RiskLevel.MEDIUM,
        "'socket' import detected — enables raw network access.",
    ),
    (
        r"\bimport\s+pickle\b|\bfrom\s+pickle\b",
        RiskLevel.HIGH,
        "'pickle' import detected — deserialization can lead to RCE.",
    ),
    (
        r"\bimport\s+requests\b|\bfrom\s+requests\b",
        RiskLevel.LOW,
        "'requests' import — network access (HTTP client).",
    ),
    (
        r"\bimport\s+shutil\b|\bfrom\s+shutil\b",
        RiskLevel.MEDIUM,
        "'shutil' import detected — provides high-level file operations.",
    ),
    (
        r"\bimport\s+pty\b|\bfrom\s+pty\b",
        RiskLevel.HIGH,
        "'pty' import detected — pseudo-terminal access.",
    ),
    (
        r"\bimport\s+base64\b|\bfrom\s+base64\b",
        RiskLevel.LOW,
        "'base64' import — often used in obfuscation of payloads.",
    ),
]


def _offset_to_line(text: str, offset: int) -> int:
    """Convert a character offset to a 1-indexed line number."""
    return text[:offset].count("\n") + 1


def _scan_patterns(
    text: str,
    patterns: list[tuple[str, RiskLevel, str]],
    rule_name: str,
) -> list[Finding]:
    """Scan text against a list of (pattern, severity, description) tuples."""
    findings: list[Finding] = []
    seen_positions: set[int] = set()
    lines = text.split("\n")

    for pattern, severity, desc_template in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if match.start() in seen_positions:
                continue
            seen_positions.add(match.start())
            line_no = _offset_to_line(text, match.start())
            findings.append(
                Finding(
                    rule=rule_name,
                    severity=severity,
                    description=desc_template.format(match=match.group(0)),
                    line=line_no,
                    offset=match.start(),
                )
            )
    return findings


# ──────────────────────────────────────────
# Individual check functions
# ──────────────────────────────────────────


def check_prompt_injection(text: str) -> list[Finding]:
    """Scan text for prompt injection patterns."""
    return _scan_patterns(text, _PROMPT_INJECTION_PATTERNS, "prompt-injection")


def check_secrets(text: str) -> list[Finding]:
    """Scan text for hardcoded secrets (API keys, tokens, passwords)."""
    return _scan_patterns(text, _SECRET_PATTERNS, "secrets-detection")


def check_network_egress(network_egress: list[str]) -> list[Finding]:
    """Check if network egress targets are too broad."""
    findings: list[Finding] = []
    for target in network_egress:
        if target in _BROAD_EGRESS_PATTERNS:
            findings.append(
                Finding(
                    rule="network-egress-audit",
                    severity=RiskLevel.HIGH,
                    description=(
                        f"Network egress target '{target}' is overly broad — "
                        f"allows unrestricted network access."
                    ),
                )
            )
    if not network_egress:
        # No restrictions specified = implicit allow
        findings.append(
            Finding(
                rule="network-egress-audit",
                severity=RiskLevel.MEDIUM,
                description="No network egress restrictions defined. Implicitly allows all traffic.",
            )
        )
    return findings


def check_permission_risk(
    tools: list,  # list[SkillTool]
    security,  # SkillSecurity
    environment: list[str],
) -> list[Finding]:
    """Analyze declared permissions for risk signals."""
    findings: list[Finding] = []

    for tool in tools:
        tool_name = tool.name if hasattr(tool, "name") else tool.get("name", str(tool))
        tool_desc = (
            tool.description
            if hasattr(tool, "description")
            else tool.get("description", "")
        )
        combined = f"{tool_name} {tool_desc}"

        # Check high-risk tool class
        declared_risk = None
        if hasattr(tool, "risk"):
            declared_risk = tool.risk
        elif isinstance(tool, dict):
            declared_risk = tool.get("risk")

        # If the declared risk is medium or higher, surface it
        if declared_risk is not None:
            risk_str = declared_risk.value if hasattr(declared_risk, "value") else str(declared_risk)
            if risk_str in ("high", "critical"):
                findings.append(
                    Finding(
                        rule="permission-risk",
                        severity=RiskLevel.HIGH,
                        description=(
                            f"Tool '{tool_name}' declares risk level '{risk_str}'. "
                            f"Validate that this tool is safe."
                        ),
                    )
                )
            elif risk_str == "medium":
                findings.append(
                    Finding(
                        rule="permission-risk",
                        severity=RiskLevel.MEDIUM,
                        description=(
                            f"Tool '{tool_name}' declares risk level 'medium'. "
                            f"Review for potential escalation."
                        ),
                    )
                )

        # Check tool name/description for dangerous operations
        for pattern, risk_desc in _HIGH_RISK_TOOL_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                findings.append(
                    Finding(
                        rule="permission-risk",
                        severity=RiskLevel.MEDIUM,
                        description=(
                            f"Tool '{tool_name}' may perform {risk_desc} "
                            f"(matched '{pattern}')."
                        ),
                    )
                )
                break  # One finding per tool is enough

    # Check security.secrets_required vs permissions.environment
    secrets_req = (
        list(security.secrets_required)
        if hasattr(security, "secrets_required")
        else security.get("secrets_required", []) if isinstance(security, dict) else []
    )
    env_vars = list(environment)

    if secrets_req and not env_vars:
        findings.append(
            Finding(
                rule="permission-risk",
                severity=RiskLevel.MEDIUM,
                description=(
                    f"Skill declares required secrets ({', '.join(secrets_req)}) "
                    f"but no environment variables are listed in permissions.environment."
                ),
            )
        )

    for secret in secrets_req:
        if not any(secret.upper() in ev.upper() for ev in env_vars):
            findings.append(
                Finding(
                    rule="permission-risk",
                    severity=RiskLevel.LOW,
                    description=(
                        f"Secret '{secret}' is declared in security.secrets_required "
                        f"but no matching entry found in permissions.environment."
                    ),
                )
            )

    return findings


def check_dependency_risk(text: str) -> list[Finding]:
    """Scan body text for suspicious imports or dependency references."""
    return _scan_patterns(text, _SUSPICIOUS_IMPORTS, "dependency-risk")


# ──────────────────────────────────────────
# Main scanner API
# ──────────────────────────────────────────


class SkillScanner:
    """Security scanner for SkillForge skill packs.

    Accepts either a parsed Skill object or raw SKILL.md text.
    """

    def scan_skill(self, skill: Skill) -> ScanReport:
        """Scan a parsed Skill object and return a ScanReport."""
        text = skill.body
        findings: list[Finding] = []

        # Also scan the description
        text_to_scan = f"{skill.manifest.description}\n{text}"

        findings.extend(check_prompt_injection(text_to_scan))
        findings.extend(check_secrets(text))
        findings.extend(
            check_network_egress(list(skill.manifest.security.network_egress))
        )
        findings.extend(
            check_permission_risk(
                list(skill.manifest.permissions.tools),
                skill.manifest.security,
                list(skill.manifest.permissions.environment),
            )
        )
        findings.extend(check_dependency_risk(text))

        return ScanReport.from_findings(findings)

    def scan_text(self, raw_text: str) -> ScanReport:
        """Scan raw SKILL.md text and return a ScanReport."""
        from skillforge_core import parse_skill_md

        try:
            skill = parse_skill_md(raw_text)
            return self.scan_skill(skill)
        except Exception:
            # Can't parse — fall back to text-only scanning
            findings: list[Finding] = []
            findings.extend(check_prompt_injection(raw_text))
            findings.extend(check_secrets(raw_text))
            findings.extend(check_dependency_risk(raw_text))
            # Generic check for broad network patterns
            for broad in _BROAD_EGRESS_PATTERNS:
                if re.search(re.escape(broad), raw_text):
                    findings.append(
                        Finding(
                            rule="network-egress-audit",
                            severity=RiskLevel.HIGH,
                            description=f"Possible broad network egress target '{broad}' found in raw text.",
                        )
                    )
            return ScanReport.from_findings(findings)

    def scan(self, skill_or_text: Skill | str) -> ScanReport:
        """Scan either a Skill object or raw SKILL.md text."""
        if isinstance(skill_or_text, str):
            return self.scan_text(skill_or_text)
        return self.scan_skill(skill_or_text)


# Module-level convenience functions
_default_scanner = SkillScanner()


def scan_skill(skill: Skill) -> ScanReport:
    """Convenience: scan a parsed Skill object."""
    return _default_scanner.scan_skill(skill)


def scan_skill_text(raw_text: str) -> ScanReport:
    """Convenience: scan raw SKILL.md text."""
    return _default_scanner.scan_text(raw_text)
