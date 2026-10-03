"""Paper data contracts, score separation, and CLI."""

import gzip
import json
import unittest
from pathlib import Path

from pydantic import ValidationError
from typer.testing import CliRunner

from k4_ramsey.artifacts import read_json
from k4_ramsey.paper import app
from k4_ramsey.paper.witness import check_manifest, check_receipt, validate
from k4_ramsey.schemas.paper import CompactWitness, SupplementManifest

ROOT = Path(__file__).resolve().parents[1]


class PaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads(
            gzip.decompress((ROOT / "paper/data/final3840.json.gz").read_bytes())
        )

    def test_witness_roundtrip_and_exact_checks(self):
        witness = CompactWitness.model_validate(self.raw)
        self.assertEqual(witness.model_dump(by_alias=True), self.raw)
        validate(self.raw)
        check_receipt(self.raw)
        check_manifest()

    def test_witness_rejects_scores_wrong_types_and_shapes(self):
        for change in [
            {"density": 0.0301},
            {"denominator": 9},
            {"canonical_to_original_coarse": [0] * 192},
            {"block_index": [False] * 36864},
            {"blocks": [[0] * 399] * 1248},
            {"blocks": [[True] * 400] * 1248},
            {"blocks": [[65537] * 400] * 1248},
        ]:
            with (
                self.subTest(field=next(iter(change))),
                self.assertRaises(ValidationError),
            ):
                CompactWitness.model_validate(self.raw | change)

    def test_manifest_rejects_traversal_and_extra_fields(self):
        raw = read_json(ROOT / "paper/data/manifest.json")
        for change in [
            {"files": {"../outside": {"sha256": "0" * 64, "bytes": 0}}},
            {"files": {"x": {"sha256": "invalid", "bytes": 0}}},
            {"score": 1},
        ]:
            with (
                self.subTest(field=next(iter(change))),
                self.assertRaises(ValidationError),
            ):
                SupplementManifest.model_validate(raw | change)

    def test_wrong_block_mean_is_rejected_after_schema_validation(self):
        blocks = [self.raw["blocks"][0].copy(), *self.raw["blocks"][1:]]
        blocks[0][0] += 1
        changed = self.raw | {"blocks": blocks}
        CompactWitness.model_validate(changed)
        with self.assertRaisesRegex(ValueError, "incorrect row mean"):
            validate(changed)

    def test_check_cli(self):
        result = CliRunner().invoke(app, ["check"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("do not perform a new density recount", result.output)
