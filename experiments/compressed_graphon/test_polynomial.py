import json
from fractions import Fraction
from pathlib import Path
import unittest

from experiments.compressed_graphon.adapters import (
    adapt_degree_map_report, adapt_total_coefficients_report,
)
from experiments.compressed_graphon.polynomial import (
    CenteredKernel, ExactPolynomial, KernelLevel, additive_raw,
    interpolate_integer_polynomial, probabilities_feasible, probability_ranges,
)


ROOT = Path(__file__).resolve().parents[2]


class PolynomialTests(unittest.TestCase):
    def test_report_adapters_retain_exact_selected_counts(self):
        potts = json.loads((ROOT/"reports/correlated-graphon-potts-precision-003/report.json").read_text())
        canonical = adapt_total_coefficients_report(
            potts, source_path="potts-report", base_order=192,
            latent_order=3, probability_denominator=65536,
        )
        self.assertEqual(ExactPolynomial.from_record(canonical).raw(potts["best"]["q"]), potts["best"]["numerator"])
        phase = json.loads((ROOT/"reports/association-scheme-phase-001/report.json").read_text())
        parent = json.loads((ROOT/"reports/literature-two-parameter-001/report.json").read_text())
        canonical = adapt_degree_map_report(
            phase, parent, source_path="phase-report", parent_path="parent-report",
            base_order=192, latent_order=5, probability_denominator=65536,
        )
        self.assertEqual(ExactPolynomial.from_record(canonical).raw(phase["selected_q"]), phase["numerator"])

    def test_simple_potts_interpolation_and_all_raw_counts(self):
        report = json.loads((ROOT/"reports/correlated-graphon-potts-001/report.json").read_text())
        points = [(row["q"], row["numerator"]) for row in report["all_results"][:7]]
        total = interpolate_integer_polynomial(points, degree_bound_proven=True)
        expected = tuple(map(int, json.loads(
            (ROOT/"reports/correlated-graphon-potts-001/causal-analysis.json").read_text()
        )["numerator_polynomial_coefficients_low_to_high"]))
        self.assertEqual(total, expected[:-1])  # trailing recorded degree-six zero is canonicalized away
        polynomial = ExactPolynomial.from_total_coefficients(expected, report["normalization"])
        for row in report["all_results"]:
            self.assertEqual(polynomial.raw(row["q"]), row["numerator"])

    def test_precision_potts_exact_minimum_and_recount_fixture(self):
        report = json.loads((ROOT/"reports/correlated-graphon-potts-precision-003/report.json").read_text())
        polynomial = ExactPolynomial.from_total_coefficients(
            tuple(map(int, report["numerator_coefficients_low_to_high"])),
            report["normalization"], feasible_integer_interval=tuple(report["feasible_q"]),
            base_order=192, latent_order=3, probability_denominator=65536,
        )
        minimum = polynomial.minimize_integer()
        self.assertEqual(minimum.minimizers, (-4708,))
        self.assertEqual(minimum.value, report["best"]["numerator"])
        for row in report["candidate_recounts"]:
            self.assertEqual(polynomial.raw(row["q"]), row["numerator"])

    def test_binary_latent_raw_count(self):
        report = json.loads((ROOT/"reports/pilot-algebraic-latent-split-001/report.json").read_text())
        parent = json.loads((ROOT/"reports/literature-simple-graphon-001/report.json").read_text())
        normalization = report["normalization"]
        base = Fraction(parent["density"])*normalization
        self.assertEqual(base.denominator, 1)
        # This historical report states A,B over the coarse n^4 denominator
        # while its stored raw numerator uses the refined (2n)^4 denominator.
        # Convert once at the fixture boundary; canonical evaluator records
        # always use one normalization for base and every coefficient.
        refinement_scale = 2**4
        polynomial = ExactPolynomial(
            int(base), (0,0,0,
                refinement_scale*report["cubic_integer_coefficient"],
                refinement_scale*report["quartic_integer_coefficient"]),
            normalization,
        )
        self.assertEqual(polynomial.raw(report["grid_coordinate"]), report["numerator"])

    def test_z5_phase_raw_count_and_exact_interval_minimum(self):
        report = json.loads((ROOT/"reports/association-scheme-phase-001/report.json").read_text())
        parent = json.loads((ROOT/"reports/literature-two-parameter-001/report.json").read_text())
        normalization = report["normalization"]
        base = Fraction(parent["density"])*normalization
        self.assertEqual(base.denominator, 1)
        coefficients = [0]*7
        for degree, value in report["coefficients"].items():
            coefficients[int(degree)] = int(value)
        polynomial = ExactPolynomial(
            int(base), tuple(coefficients), normalization,
            feasible_integer_interval=tuple(report["feasible_q"]),
            base_order=192, latent_order=5, probability_denominator=65536,
        )
        self.assertEqual(polynomial.raw(report["selected_q"]), report["numerator"])
        minimum = polynomial.minimize_integer()
        self.assertEqual(minimum.minimizers, (report["selected_q"],))
        self.assertEqual(Fraction(minimum.value, normalization), Fraction(report["actual_density"]))

    def test_record_round_trip_and_convention_guard(self):
        polynomial = ExactPolynomial(10, (0,0,-2,1), 17, feasible_integer_interval=(-2,3))
        self.assertEqual(ExactPolynomial.from_record(polynomial.to_record()), polynomial)
        bad = polynomial.to_record(); bad["coefficient_convention"] = "ambiguous"
        with self.assertRaises(ValueError):
            ExactPolynomial.from_record(bad)

    def test_lossy_numbers_and_unproved_interpolation_rejected(self):
        with self.assertRaises((TypeError, ValueError)):
            ExactPolynomial(0, (0, Fraction(1,2)), 1)
        with self.assertRaises((TypeError, ValueError)):
            ExactPolynomial(0, (0, 1.0), 1)
        with self.assertRaises((TypeError, ValueError)):
            CenteredKernel(((1.0,-1),(-1,1)))
        with self.assertRaises(ValueError):
            interpolate_integer_polynomial(((0,0),(1,1)))

    def test_tie_minimum_and_additivity_guard(self):
        polynomial = ExactPolynomial(8, (0,-1,1), 10, feasible_integer_interval=(-2,3))
        self.assertEqual(polynomial.minimize_integer().minimizers, (0,1))
        with self.assertRaises(ValueError):
            polynomial.additive_raw([-1,-1])
        self.assertEqual(polynomial.additive_raw([-1,-1], mixed_terms_absent=True), 12)
        self.assertEqual(additive_raw(8, [((0,-1,1),-1),((0,2),3)], mixed_terms_absent=True), 16)

    def test_centered_kernels_and_multilevel_feasibility(self):
        potts = CenteredKernel(((2,-1,-1),(-1,2,-1),(-1,-1,2)))
        binary = CenteredKernel(((1,-1),(-1,1)))
        z5row = (-2,3,-2,-2,3)
        z5 = CenteredKernel(tuple(tuple(z5row[(b-a)%5] for b in range(5)) for a in range(5)))
        self.assertEqual((potts.order,binary.order,z5.order),(3,2,5))
        levels = [KernelLevel(potts,-4708)]*3
        self.assertEqual(probability_ranges((35015,51064),levels),((6767,49139),(22816,65188)))
        self.assertTrue(probabilities_feasible((35015,51064),65536,levels))
        self.assertFalse(probabilities_feasible((35015,51064),65536,levels+[KernelLevel(potts,-4708)]))
        mixed = [KernelLevel(binary,2),KernelLevel(z5,-1)]
        self.assertEqual(probability_ranges((10,),mixed),((5,14),))
        with self.assertRaises(ValueError):
            CenteredKernel(((1,0),(0,1)))


if __name__ == "__main__":
    unittest.main()
