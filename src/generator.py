from __future__ import annotations

from itertools import cycle
from .config import SETTINGS
from .llm_client import generate_json
from .models import GenerationResult, ReviewStatus, TestCase
from .parser import parse_requirement
from .prompts import build_generation_prompt


def _demo_case(rid: str, idx: int, test_type: str, rule: str) -> TestCase:
    templates = {
        "Functional": ("Successful behavior for the stated rule", "Use valid input and complete the action", "The system completes the action and records the correct state"),
        "Negative": ("Reject behavior that violates the rule", "Use invalid input or violate the stated rule", "The system blocks the action and displays a safe, clear message"),
        "Boundary": ("Verify behavior at the rule threshold", "Exercise values immediately below, at, and above the threshold", "Each boundary produces the specified state transition"),
        "Validation": ("Validate required and malformed input", "Submit missing, malformed, and valid values", "Invalid input is rejected and valid input is processed"),
        "Security": ("Protect information and prevent unauthorized behavior", "Attempt the action with invalid credentials or an unauthorized context", "The system reveals no sensitive information and records the event"),
        "Regression": ("Preserve related existing behavior", "Complete a successful action after exercising the new rule", "Existing behavior remains available and stored counters are correct"),
    }
    scenario, action, expected = templates[test_type]
    return TestCase(
        test_case_id=f"TC-{rid.replace('REQ-', '')}-{idx:03d}", requirement_id=rid,
        scenario=scenario, test_type=test_type, preconditions="Test user and controlled test data are available",
        steps=["Open the relevant application function", action, "Observe the response and resulting state"],
        test_data=f"Representative {test_type.lower()} data", expected_result=expected,
        priority="High" if test_type in {"Negative", "Boundary", "Security"} else "Medium",
        risk="High" if test_type in {"Security", "Boundary"} else "Medium", confidence=0.84,
        source_rule=rule[:240], status=ReviewStatus.NEEDS_REVIEW,
    )


def generate_cases(requirement: str, selected_types: list[str], count: int, mode: str) -> GenerationResult:
    analysis = parse_requirement(requirement)
    if mode == "Vertex AI Gemini":
        prompt = build_generation_prompt(requirement, analysis, selected_types, count)
        payload, model_name = generate_json(prompt)
        cases = []
        for i, item in enumerate(payload.get("test_cases", []), 1):
            item.setdefault("test_case_id", f"TC-{i:03d}")
            item.setdefault("requirement_id", analysis.requirement_id)
            item.setdefault("status", ReviewStatus.NEEDS_REVIEW)
            cases.append(TestCase.model_validate(item))
        if not cases:
            raise ValueError("No valid test cases were returned by Gemini.")
        return GenerationResult(analysis=analysis, test_cases=cases, model_used=model_name, generation_mode=mode)
    rules = analysis.business_rules or [requirement]
    rule_cycle = cycle(rules)
    type_cycle = cycle(selected_types)
    cases = [_demo_case(analysis.requirement_id, i, next(type_cycle), next(rule_cycle)) for i in range(1, count + 1)]
    return GenerationResult(analysis=analysis, test_cases=cases, model_used="Deterministic demo engine", generation_mode="Demo Engine")


def regenerate_case(case: TestCase) -> TestCase:
    updated = case.model_copy(deep=True)
    updated.scenario = f"Alternative: {case.scenario}"
    updated.steps = ["Reset the test environment", *case.steps[1:]]
    updated.confidence = min(0.95, case.confidence + 0.04)
    updated.status = ReviewStatus.NEEDS_REVIEW
    updated.reviewer_comment = "Regenerated for reviewer comparison"
    return updated

