from __future__ import annotations

import re
from pathlib import Path
import pandas as pd
from .models import RequirementAnalysis


def read_uploaded_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix in {".txt", ".md"}:
        return raw.decode("utf-8", errors="replace")
    if suffix == ".csv":
        uploaded_file.seek(0)
        frame = pd.read_csv(uploaded_file)
        return "\n".join(frame.astype(str).agg(" | ".join, axis=1).tolist())
    if suffix == ".json":
        return raw.decode("utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {suffix}")


def parse_requirement(text: str) -> RequirementAnalysis:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        raise ValueError("Enter or upload a requirement before generating test cases.")
    rid_match = re.search(r"\b(?:REQ|US|STORY)[-_ ]?[A-Z0-9-]+\b", clean, re.I)
    rid = rid_match.group(0).replace(" ", "-").upper() if rid_match else "REQ-001"
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean) if len(s.strip()) > 3]
    actors = []
    for actor in ["customer", "user", "administrator", "reviewer", "system", "agent"]:
        if re.search(rf"\b{actor}\b", clean, re.I):
            actors.append(actor.title())
    rules = [s for s in sentences if re.search(r"\b(must|shall|should|after|before|only|cannot|can not)\b", s, re.I)]
    constraints = [s for s in sentences if re.search(r"\b\d+\b|within|maximum|minimum|consecutive|limit", s, re.I)]
    ambiguities = []
    if not re.search(r"error|message|notification|response", clean, re.I):
        ambiguities.append("Expected user-facing error or success messages are not specified.")
    if not re.search(r"audit|log|record|history", clean, re.I):
        ambiguities.append("Audit or logging requirements are not specified.")
    if not re.search(r"role|permission|authori[sz]", clean, re.I):
        ambiguities.append("Authorization and role behavior are not specified.")
    return RequirementAnalysis(
        requirement_id=rid,
        title=(sentences[0] if sentences else clean)[:120],
        actors=actors or ["User"],
        business_rules=rules or sentences,
        constraints=constraints,
        acceptance_criteria=rules or sentences,
        ambiguities=ambiguities,
    )

