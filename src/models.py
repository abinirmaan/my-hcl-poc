from __future__ import annotations

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    NEEDS_REVIEW = "Needs review"
    ACCEPTED = "Accepted"
    EDITED = "Edited"
    REJECTED = "Rejected"


class RequirementAnalysis(BaseModel):
    requirement_id: str = "REQ-001"
    title: str
    actors: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)


class TestCase(BaseModel):
    test_case_id: str
    requirement_id: str
    scenario: str
    test_type: Literal["Functional", "Negative", "Boundary", "Validation", "Security", "Regression"]
    preconditions: str
    steps: list[str]
    test_data: str
    expected_result: str
    priority: Literal["High", "Medium", "Low"] = "Medium"
    risk: Literal["High", "Medium", "Low"] = "Medium"
    confidence: float = Field(default=0.80, ge=0, le=1)
    source_rule: str
    status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    reviewer_comment: str = ""


class GenerationResult(BaseModel):
    analysis: RequirementAnalysis
    test_cases: list[TestCase]
    model_used: str
    generation_mode: str

