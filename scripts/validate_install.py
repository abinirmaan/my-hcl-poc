from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.generator import generate_cases
from src.sample_data import SAMPLE_REQUIREMENT

result = generate_cases(SAMPLE_REQUIREMENT, ["Functional", "Negative", "Boundary", "Security"], 8, "Demo Engine")
assert len(result.test_cases) == 8
assert result.analysis.requirement_id == "REQ-LOGIN-01"
print("POC validation passed: parser and demo generator are ready.")
