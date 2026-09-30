from __future__ import annotations

import io
import json
import pandas as pd
from .models import TestCase


def cases_to_frame(cases: list[TestCase]) -> pd.DataFrame:
    rows = []
    for c in cases:
        d = c.model_dump(mode="json")
        d["steps"] = "\n".join(f"{i}. {step}" for i, step in enumerate(c.steps, 1))
        rows.append(d)
    return pd.DataFrame(rows)


def export_csv(cases: list[TestCase]) -> bytes:
    return cases_to_frame(cases).to_csv(index=False).encode("utf-8-sig")


def export_json(cases: list[TestCase]) -> bytes:
    return json.dumps([c.model_dump(mode="json") for c in cases], indent=2).encode("utf-8")


def export_excel(cases: list[TestCase]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame = cases_to_frame(cases)
        frame.to_excel(writer, index=False, sheet_name="Test Cases")
        sheet = writer.book["Test Cases"]
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            letter = column[0].column_letter
            sheet.column_dimensions[letter].width = min(50, max(14, max(len(str(cell.value or "")) for cell in column) + 2))
    return output.getvalue()

