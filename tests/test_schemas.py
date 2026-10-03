"""Data examples, boundary cases, and counterexamples for the domain contracts."""
from pathlib import Path
import tempfile
import unittest

from pydantic import BaseModel, ValidationError

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.schemas.certificates import UnitCertificate, WeightedCertificate
from k4_ramsey.schemas.experiments import ExperimentReport, ExperimentRequest, ProcessResult, SearchMetrics
from k4_ramsey.schemas.strategies import (
    AnnealConfig, CloneConfig, CubicStarConfig, DescentConfig, FastNeighborhoodConfig,
    MatchingConfig, ScanConfig, StarConfig, TabuConfig,
)
from k4_ramsey.verify import parse_recount


def example_certificate():
    return {"schema": "weighted-two-color-blowup-v1", "weights": [1, 1], "red_rows": ["01", "10"]}


def example_request(**changes):
    data = dict(out=Path("out"), input_path=Path("in.json"), strategy=Path("search.py"),
                hypothesis="A test", prediction="Same exact count")
    return ExperimentRequest(**(data | changes))


def example_report(**changes):
    data = dict(hypothesis="A test", prediction="Same exact count", seed=0,
                search_seconds=1.0, timeout_seconds=5.0, started_at="2026-10-03T12:00:00Z",
                source_input="in.json", strategy="search.py", python="test", platform="test")
    return ExperimentReport(**(data | changes))


class SchemaTests(unittest.TestCase):
    def test_certificate_roundtrip_and_weighted_subset(self):
        raw = example_certificate()
        unit = UnitCertificate.model_validate(raw)
        self.assertIsInstance(unit, BaseModel)
        self.assertEqual(unit.model_dump(by_alias=True), raw)
        raw["weights"] = [1, 65535]
        self.assertEqual(WeightedCertificate.model_validate(raw).weights, [1, 65535])
        with self.assertRaises(ValidationError):
            UnitCertificate.model_validate(raw)

    def test_certificate_rejects_wrong_types_shapes_and_extra_fields(self):
        examples = [
            {"schema": "unknown"}, {"weights": [True, 1]}, {"weights": ["1", 1]},
            {"weights": [1.0, 1]}, {"weights": [0, 1]}, {"weights": [65536, 1]},
            {"weights": [1]}, {"red_rows": ["1"]}, {"red_rows": ["01", "00"]},
            {"red_rows": ["00"]}, {"red_rows": ["0x", "x0"]},
            {"red_rows": []}, {"red_rows": ("01", "10")}, {"unknown": 1},
        ]
        for change in examples:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                WeightedCertificate.model_validate(example_certificate() | change)

    def test_request_budgets_and_purpose(self):
        self.assertEqual(example_request().seconds, 10.0)
        for change in [{"seconds": 0}, {"seconds": True}, {"seconds": float("nan")},
                       {"timeout": float("inf")}, {"timeout": 1}, {"hypothesis": "  "},
                       {"prediction": ""}, {"config": []}, {"config": {"x": float("inf")}}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                example_request(**change)

    def test_strategy_config_examples_and_boundaries(self):
        schemas = [AnnealConfig, CloneConfig, CubicStarConfig, DescentConfig,
                   FastNeighborhoodConfig, MatchingConfig, ScanConfig, StarConfig, TabuConfig]
        for schema in schemas:
            with self.subTest(schema=schema):
                schema.model_validate({})
                with self.assertRaises(ValidationError):
                    schema.model_validate({"typo": 1})
        self.assertEqual(DescentConfig(max_moves=0).max_moves, 0)
        for schema, data in [(DescentConfig, {"max_moves": True}),
                             (ScanConfig, {"max_passes": 0}),
                             (AnnealConfig, {"temperature": float("inf")}),
                             (AnnealConfig, {"restart": 1}),
                             (MatchingConfig, {"size": 8, "pool_size": 7}),
                             (CubicStarConfig, {"size": 3, "random_per_color": 2}),
                             (TabuConfig, {"max_moves": 2**31}),
                             (TabuConfig, {"checkpoint_seconds": True})]:
            with self.subTest(schema=schema, data=data), self.assertRaises(ValidationError):
                schema.model_validate(data)

    def test_untrusted_search_claims(self):
        metrics = SearchMetrics.model_validate({"numerator": 12, "diagnostic": [1, "x"]})
        self.assertEqual(metrics.numerator, 12)
        self.assertEqual(metrics.model_extra, {"diagnostic": [1, "x"]})
        for value in [True, "12", 12.0, -1]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                SearchMetrics.model_validate({"numerator": value})

    def test_recount_contract(self):
        checked = parse_recount("2 2 16 1 0 0 0", 2, 2, 0.1, "hash")
        self.assertEqual(checked.density, "1/8")
        for output in ["2 2 16", "2 2 15 1 0 0 0", "3 2 81 1 0 0 0",
                       "2 -1 16 1 0 0 0", "2 17 16 1 0 0 0", "2 2 16 -1 0 0 0"]:
            with self.subTest(output=output), self.assertRaises(ValueError):
                parse_recount(output, 2, None, 0.1, "hash")
        with self.assertRaises(ValueError):
            parse_recount("2 2 16 1 0 0 0", 2, 3, 0.1, "hash")

    def test_evidence_cannot_be_promoted_without_recount(self):
        for changes in [dict(status="completed"), dict(evidence="lean_native_checked"),
                        dict(status="failed", evidence="lean_native_checked")]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                example_report(**changes)
        checked = parse_recount("2 2 16 1 0 0 0", 2, None, 0.1, "hash")
        report = example_report(status="completed", evidence="lean_native_checked",
                                verification=checked, candidate_sha256="hash")
        restored = ExperimentReport.model_validate(report.model_dump(by_alias=True, exclude_none=True))
        self.assertEqual(restored.verification, checked)

    def test_timeout_roundtrip_retains_nullable_returncode(self):
        report = example_report(status="timeout", process=ProcessResult(
            status="timeout", returncode=None, seconds=0.0))
        restored = ExperimentReport.model_validate(report.model_dump(by_alias=True, exclude_none=True))
        self.assertIsNone(restored.process.returncode)

    def test_json_boundary_rejects_duplicate_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            write_json(path, UnitCertificate.model_validate(example_certificate()))
            self.assertEqual(read_json(path), example_certificate())
            for text in ['{"x": 1, "x": 2}', '{"x": NaN}', '{"x": Infinity}', '{"x": 1e999}']:
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(ValueError):
                    read_json(path)
