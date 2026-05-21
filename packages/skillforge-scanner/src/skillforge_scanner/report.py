"""ScanReport model — security scan results."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    """A single security finding from the scanner."""
    rule: str
    severity: RiskLevel
    description: str
    line: int | None = None
    offset: int | None = None


class ScanReport(BaseModel):
    """Aggregated scan report with all findings."""
    total_score: int = Field(ge=0, le=100, description="0-100, higher = safer")
    risk_level: RiskLevel
    findings: list[Finding] = Field(default_factory=list)
    summary: str = ""

    @classmethod
    def from_findings(cls, findings: list[Finding]) -> ScanReport:
        """Build a ScanReport from a list of Findings, computing score and risk level."""
        severity_deductions: dict[RiskLevel, int] = {
            RiskLevel.LOW: 5,
            RiskLevel.MEDIUM: 15,
            RiskLevel.HIGH: 25,
            RiskLevel.CRITICAL: 40,
        }

        total_deduction = sum(
            severity_deductions.get(f.severity, 0) for f in findings
        )
        total_score = max(0, 100 - total_deduction)

        if total_score >= 80:
            risk_level = RiskLevel.LOW
        elif total_score >= 60:
            risk_level = RiskLevel.MEDIUM
        elif total_score >= 30:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        summary_parts: list[str] = []
        if not findings:
            summary_parts.append("No issues found. Skill appears safe.")
        else:
            sev_counts: dict[str, int] = {}
            for f in findings:
                sev_counts[f.severity.value] = sev_counts.get(f.severity.value, 0) + 1
            parts: list[str] = []
            for sev in ("critical", "high", "medium", "low"):
                if sev_counts.get(sev):
                    parts.append(f"{sev_counts[sev]} {sev}")
            summary_parts.append(f"Found {len(findings)} issue(s): {', '.join(parts)}.")
            summary_parts.append(f"Score: {total_score}/100 — Risk level: {risk_level.value.upper()}.")

        return cls(
            total_score=total_score,
            risk_level=risk_level,
            findings=findings,
            summary=" ".join(summary_parts),
        )
