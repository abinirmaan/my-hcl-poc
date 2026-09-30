from __future__ import annotations

import json
from .models import RequirementAnalysis


def build_generation_prompt(raw_requirement: str, analysis: RequirementAnalysis, selected_types: list[str], count: int) -> str:
    schema = {
        "test_cases": [{
            "test_case_id": "TC-001", "requirement_id": analysis.requirement_id,
            "scenario": "string", "test_type": "Functional|Negative|Boundary|Validation|Security|Regression",
            "preconditions": "string", "steps": ["step 1"], "test_data": "string",
            "expected_result": "string", "priority": "High|Medium|Low", "risk": "High|Medium|Low",
            "confidence": 0.9, "source_rule": "exact business rule or acceptance criterion"
        }]
    }
    return f"""You are a senior QA test designer. Generate exactly {count} concise, executable test cases.
Use only these test types: {', '.join(selected_types)}.
Maintain traceability to the supplied requirement. Include positive, error, and boundary behavior where applicable.
Do not invent external systems. If information is missing, use a neutral placeholder and lower confidence.
Return JSON only, conforming to this shape: {json.dumps(schema)}

Requirement analysis:
{analysis.model_dump_json(indent=2)}

Original requirement:
{raw_requirement}
"""

