"""Freeze the reported F3 optima so exact terminal gradients can be audited."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIGS = Path(__file__).resolve().parent / "configs" / "f3_quadratic"

for d in (4, 5):
    for twist in (1, 2):
        stem = f"f3d{d}_twist{twist}"
        report = ROOT / "reports" / f"relation-engine-f3d{d}-twist{twist}-translated-free-001" / "report.json"
        config = json.loads((CONFIGS / f"{stem}_translated_frozen.json").read_text())
        result = json.loads(report.read_text())
        config["probability_numerators"] = result["rounded_probabilities"]
        config["expected_parent_fraction"] = (
            f"{result['rounded_numerator']}/{result['parent_denominator']}"
        )
        (CONFIGS / f"{stem}_translated_final_frozen.json").write_text(
            json.dumps(config, separators=(",", ":")) + "\n"
        )
