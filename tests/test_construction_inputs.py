"""The relocated generators must retain the exact attributed source bytes."""

import gzip
import hashlib
import unittest

from k4_ramsey.artifacts import read_json
from k4_ramsey.engine import ROOT


class ConstructionInputTests(unittest.TestCase):
    def test_bundled_inputs_match_provenance(self):
        directory = ROOT / "data/constructions"
        manifest = read_json(directory / "provenance.json")
        self.assertEqual(
            set(manifest),
            {"quotient.json", "base192.json", "family-rule.json",
             "vertex-map.json", "final3840.json.gz"},
        )
        for name, metadata in manifest.items():
            with self.subTest(name=name):
                path = directory / name
                self.assertEqual(path.stat().st_size, metadata["stored_bytes"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 metadata["stored_sha256"])
                digest = hashlib.sha256()
                size = 0
                opener = gzip.open if name.endswith(".gz") else open
                with opener(path, "rb") as source:
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        size += len(chunk)
                self.assertEqual(size, metadata["source_bytes"])
                self.assertEqual(digest.hexdigest(), metadata["source_sha256"])
