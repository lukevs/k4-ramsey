"""Examples for the Typer boundary and the shared standalone strategy protocol."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from typer.testing import CliRunner

from k4_ramsey.artifacts import write_json
from k4_ramsey.engine import ROOT, make_certificate
from k4_ramsey.lab import app, run_experiment
from k4_ramsey.schemas.experiments import ExperimentRequest
from k4_ramsey.weighted_verify import app as weighted_app


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="k4-cli-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / "input with spaces.json"
        write_json(self.input, make_certificate(["00000"] * 5))
        self.runner = CliRunner()

    def test_help_and_required_options(self):
        for command in [[], ["run"], ["dashboard"], ["record-build"]]:
            result = self.runner.invoke(app, command + ["--help"])
            self.assertEqual(result.exit_code, 0, result.output)
        self.assertNotEqual(self.runner.invoke(app, ["run"]).exit_code, 0)

    def test_run_cli_preserves_flags_and_paths(self):
        config = self.root / "config.json"
        write_json(config, {"max_moves": 0})
        out = self.root / "run with spaces"
        result = self.runner.invoke(app, [
            "run", "--input", str(self.input), "--out", str(out),
            "--config", str(config), "--seconds", "0.1", "--timeout", "5",
            "--hypothesis", "A test with spaces", "--prediction", "Count unchanged",
        ])
        self.assertEqual(result.exit_code, 0, (result.output, result.exception))
        report = json.loads((out / "report.json").read_text())
        self.assertEqual(report["hypothesis"], "A test with spaces")
        self.assertEqual(report["improvement"], 0)
        self.assertEqual(report["evidence"], "lean_native_checked")
        self.assertTrue((out / "snapshot/src/k4_ramsey/schemas/certificates.py").is_file())
        self.assertIn("uv.lock", report["source_hashes"])

    def test_invalid_request_does_not_create_output(self):
        out = self.root / "invalid"
        result = self.runner.invoke(app, ["run", "--out", str(out), "--seconds", "nan",
                                         "--hypothesis", "A test", "--prediction", "A result"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertFalse(out.exists())

    def test_weighted_cli_writes_once(self):
        out = self.root / "weighted.json"
        args = ["--input", str(self.input), "--out", str(out), "--expected-density", "1"]
        result = self.runner.invoke(weighted_app, args)
        self.assertEqual(result.exit_code, 0, (result.output, result.exception))
        original = out.read_bytes()
        self.assertEqual(json.loads(original)["status"], "lean_native_checked_weighted_v1")
        self.assertNotEqual(self.runner.invoke(weighted_app, args).exit_code, 0)
        self.assertEqual(out.read_bytes(), original)

    def test_dashboard_cli(self):
        out = self.root / "dashboard.html"
        result = self.runner.invoke(app, ["dashboard", "--reports", str(self.root), "--out", str(out)])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("No experiment reports", out.read_text())

    def test_certificate_generator_cli(self):
        output = self.root / "Example.lean"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/generate_lean_certificate.py"),
                                 str(self.input), str(output), "--namespace", "Example"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("namespace K4Ramsey.Example", output.read_text())

    def test_every_strategy_uses_shared_typer_protocol(self):
        examples = {
            "edge_descent": {"max_moves": 0},
            "scan_descent": {"max_passes": 1},
            "anneal": {"max_moves": 1, "cycle_moves": 1},
            "clone_search": {"max_moves": 0},
            "tabu_search": {"max_moves": 0},
            "fast_neighborhood": {"max_moves": 1},
            "star_search": {"max_rounds": 1},
            "matching_search": {"size": 2, "pool_size": 10, "max_neighborhoods": 1},
            "cubic_star": {"size": 3, "max_neighborhoods": 1},
        }
        for name, config in examples.items():
            with self.subTest(strategy=name):
                request = ExperimentRequest(
                    out=self.root / name, input_path=self.input,
                    strategy=ROOT / f"experiments/strategies/{name}.py",
                    hypothesis="CLI smoke test", prediction="Exact recount agrees",
                    seconds=0.1, timeout=5.0, config=config,
                )
                report = run_experiment(request)
                self.assertEqual(report.status, "completed",
                                 (report.error, (request.out / "stderr.log").read_text()))
