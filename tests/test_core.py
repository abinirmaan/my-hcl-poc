from src.exports import export_csv, export_excel, export_json
from src.generator import generate_cases
from src.quality import coverage_metrics, quality_findings
from src.sample_data import SAMPLE_REQUIREMENT


def test_demo_generation_and_exports():
    result = generate_cases(SAMPLE_REQUIREMENT, ["Functional", "Negative", "Boundary", "Security"], 8, "Demo Engine")
    assert len(result.test_cases) == 8
    assert result.analysis.requirement_id == "REQ-LOGIN-01"
    assert coverage_metrics(result.analysis, result.test_cases)["coverage"] > 0
    assert isinstance(quality_findings(result.test_cases), list)
    assert len(export_csv(result.test_cases)) > 100
    assert len(export_json(result.test_cases)) > 100
    assert len(export_excel(result.test_cases)) > 1000

