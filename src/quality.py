from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
from .models import RequirementAnalysis, TestCase


def coverage_metrics(analysis: RequirementAnalysis, cases: list[TestCase]) -> dict:
    rules = analysis.business_rules or analysis.acceptance_criteria
    covered = 0
    for rule in rules:
        if any(SequenceMatcher(None, rule.lower(), c.source_rule.lower()).ratio() >= 0.45 for c in cases):
            covered += 1
    coverage = round(100 * covered / max(len(rules), 1))
    statuses = Counter(c.status.value for c in cases)
    types = Counter(c.test_type for c in cases)
    return {"coverage": coverage, "rules_total": len(rules), "rules_covered": covered, "statuses": dict(statuses), "types": dict(types)}


def quality_findings(cases: list[TestCase]) -> list[str]:
    findings = []
    seen = set()
    for case in cases:
        key = case.scenario.strip().lower()
        if key in seen:
            findings.append(f"Potential duplicate scenario: {case.test_case_id}")
        seen.add(key)
        if len(case.steps) < 2:
            findings.append(f"Too few execution steps: {case.test_case_id}")
        if len(case.expected_result.strip()) < 20:
            findings.append(f"Expected result may be vague: {case.test_case_id}")
        if case.confidence < 0.65:
            findings.append(f"Low confidence: {case.test_case_id}")
    return findings

