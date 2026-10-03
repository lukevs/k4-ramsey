"""Independent literal tests for the compressed graphon polynomial utilities."""

from fractions import Fraction
from itertools import combinations, product
import unittest

from experiments.compressed_graphon.polynomial import (
    CenteredKernel,
    ExactPolynomial,
    KernelLevel,
    interpolate_integer_polynomial,
    probabilities_feasible,
    probability_ranges,
)


def literal_raw(matrix, denominator):
    """Direct ordered four-position red+blue numerator, repeated indices included."""
    answer = 0
    for vertices in product(range(len(matrix)), repeat=4):
        red = 1
        blue = 1
        for a, b in combinations(range(4), 2):
            value = matrix[vertices[a]][vertices[b]]
            red *= value
            blue *= denominator - value
        answer += red + blue
    return answer


def expand(base, support, kernels, coordinates):
    """Materialize only tiny Cartesian latent products for an independent oracle."""
    assert len(kernels) == len(coordinates)
    state_space = list(product(*(range(len(kernel)) for kernel in kernels)))
    classes = [(base_vertex, state) for base_vertex in range(len(base)) for state in state_space]
    matrix = []
    for i, si in classes:
        row = []
        for j, sj in classes:
            value = base[i][j]
            if support[i][j]:
                value += sum(
                    q * kernel[si[level]][sj[level]]
                    for level, (kernel, q) in enumerate(zip(kernels, coordinates))
                )
            row.append(value)
        matrix.append(row)
    return matrix


def one_level_polynomial(base, support, kernel, denominator, coordinates=range(-3, 4)):
    points = []
    normalization = None
    for q in coordinates:
        matrix = expand(base, support, [kernel], [q])
        assert all(0 <= value <= denominator for row in matrix for value in row)
        raw = literal_raw(matrix, denominator)
        points.append((q, raw))
        candidate_normalization = len(matrix) ** 4 * denominator**6
        normalization = candidate_normalization if normalization is None else normalization
        assert normalization == candidate_normalization
    # A six-edge four-vertex product has degree at most six in one amplitude.
    total = interpolate_integer_polynomial(
        points, max_degree=6, degree_bound_proven=True
    )
    return ExactPolynomial.from_total_coefficients(
        total,
        normalization,
        feasible_integer_interval=(min(coordinates), max(coordinates)),
        base_order=len(base),
        latent_order=len(kernel),
        probability_denominator=denominator,
    )


class IndependentCompressedPolynomialTests(unittest.TestCase):
    def test_signed_exact_feasible_endpoints_and_cartesian_extrema(self):
        potts = CenteredKernel(((2, -1, -1), (-1, 2, -1), (-1, -1, 2)))

        positive_endpoint = [KernelLevel(potts, 3)]
        self.assertEqual(probability_ranges((6, 14), positive_endpoint), ((3, 12), (11, 20)))
        self.assertTrue(probabilities_feasible((6, 14), 20, positive_endpoint))
        self.assertFalse(probabilities_feasible((6, 14), 20, [KernelLevel(potts, 4)]))

        negative_endpoint = [KernelLevel(potts, -3)]
        self.assertEqual(probability_ranges((6, 14), negative_endpoint), ((0, 9), (8, 17)))
        self.assertTrue(probabilities_feasible((6, 14), 20, negative_endpoint))
        self.assertFalse(probabilities_feasible((6, 14), 20, [KernelLevel(potts, -4)]))

        # Independent latent coordinates realize all Cartesian combinations,
        # so signed per-level extrema add rather than merely bounding the range.
        signed_levels = [KernelLevel(potts, 3), KernelLevel(potts, -3)]
        self.assertEqual(probability_ranges((9, 11), signed_levels), ((0, 18), (2, 20)))
        self.assertTrue(probabilities_feasible((9, 11), 20, signed_levels))
        self.assertFalse(
            probabilities_feasible((9, 11), 20, signed_levels + [KernelLevel(potts, 1)])
        )

    def test_centered_multilevel_matches_literal_with_diagonal_support(self):
        denominator = 20
        base = ((7, 11), (11, 13))
        # Deliberately perturb every entry, including both base diagonals. This
        # makes repeated base indices exercise real perturbation terms.
        support = ((True, True), (True, True))
        binary = ((1, -1), (-1, 1))
        CenteredKernel(binary)  # independently assert the utility accepts it
        polynomial = one_level_polynomial(base, support, binary, denominator)

        for q in (-3, -1, 0, 2, 3):
            matrix = expand(base, support, [binary], [q])
            self.assertEqual(
                polynomial.density(q),
                Fraction(literal_raw(matrix, denominator), len(matrix) ** 4 * denominator**6),
            )

        coordinates = (2, -3, 1)
        expanded = expand(base, support, [binary] * len(coordinates), coordinates)
        literal_density = Fraction(
            literal_raw(expanded, denominator), len(expanded) ** 4 * denominator**6
        )
        self.assertEqual(
            polynomial.additive_density(coordinates, mixed_terms_absent=True), literal_density
        )

        # The normalization is the one-level refined order, not the coarse
        # order. Omitting the latent-order^4 factor must visibly fail.
        wrong_normalization = len(base) ** 4 * denominator**6
        self.assertNotEqual(polynomial.normalization_denominator, wrong_normalization)
        self.assertNotEqual(
            Fraction(polynomial.additive_raw(coordinates, mixed_terms_absent=True), wrong_normalization),
            literal_density,
        )

    def test_noncentered_kernel_is_rejected_and_would_create_mixed_terms(self):
        noncentered = ((1, 0), (0, -1))
        with self.assertRaisesRegex(ValueError, "zero uniform row sums"):
            CenteredKernel(noncentered)

        denominator = 20
        base = ((7, 11), (11, 13))
        support = ((True, True), (True, True))
        polynomial = one_level_polynomial(base, support, noncentered, denominator)
        coordinates = (2, 1)
        literal = expand(base, support, [noncentered, noncentered], coordinates)
        literal_density = Fraction(
            literal_raw(literal, denominator), len(literal) ** 4 * denominator**6
        )

        with self.assertRaisesRegex(ValueError, "no-mixed-terms argument"):
            polynomial.additive_density(coordinates)
        # This explicit false assertion demonstrates why centering and the
        # no-mixed proof are required: the naive additive value is wrong.
        self.assertNotEqual(
            polynomial.additive_density(coordinates, mixed_terms_absent=True), literal_density
        )

    def test_record_rejects_convention_drift_and_minimum_includes_endpoints(self):
        polynomial = ExactPolynomial(
            100,
            (0, 5),
            17,
            feasible_integer_interval=(-4, 3),
            base_order=2,
            latent_order=2,
            probability_denominator=20,
        )
        minimum = polynomial.minimize_integer()
        self.assertEqual(minimum.minimizers, (-4,))
        self.assertEqual(minimum.evaluations, 8)
        self.assertEqual(minimum.interval, (-4, 3))

        record = polynomial.to_record()
        record["coefficient_convention"] = "same coefficients, unspecified normalization"
        with self.assertRaisesRegex(ValueError, "unknown coefficient convention"):
            ExactPolynomial.from_record(record)


if __name__ == "__main__":
    unittest.main()
