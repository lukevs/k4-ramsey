import random
import unittest
from fractions import Fraction
from itertools import product

from experiments.structural.profiles import (
    compose_graph, compose_profile, composition_terms, graph_from_mask,
    mono, nested_limit, profile, transform, xor_graph, xor_profiles,
)


class StructuralTests(unittest.TestCase):
    def test_transform_and_xor_tiny(self):
        rng = random.Random(991)
        for _ in range(12):
            a = graph_from_mask(3, rng.randrange(8))
            b = graph_from_mask(3, rng.randrange(8))
            p = profile(a)
            self.assertEqual(transform(transform(p)), tuple(64*x for x in p))
            self.assertEqual(xor_profiles(p, profile(b)), profile(xor_graph(a, b)))

    def test_composition_tiny(self):
        for a, b in product(range(8), repeat=2):
            outer, inner = graph_from_mask(3, a), graph_from_mask(3, b)
            predicted = compose_profile(composition_terms(outer), profile(inner))
            self.assertEqual(predicted, profile(compose_graph(outer, inner)))

    def test_published_historical_finite_and_limit(self):
        k3, k4, k2 = graph_from_mask(3, 7), graph_from_mask(4, 63), ["01", "10"]
        matching = ["0100", "1000", "0001", "0010"]
        q9 = xor_graph(k3, k3)
        base = xor_profiles(profile(matching), profile(k4))
        self.assertEqual(mono(xor_profiles(base, profile(q9))), Fraction(11411, 373248))
        p18 = compose_profile(composition_terms(q9), profile(k2))
        self.assertEqual(mono(xor_profiles(base, p18)), Fraction(3769, 124416))
        self.assertEqual(mono(xor_profiles(base, nested_limit(q9))), Fraction(1411, 46592))

    def test_repetitions_and_invalid(self):
        self.assertEqual(mono(profile(["01", "10"])), Fraction(1, 8))
        self.assertEqual(mono(nested_limit(["01", "10"])), 1)
        for rows in [["1"], ["01", "00"], ["00"]]:
            with self.assertRaises(ValueError):
                profile(rows)


if __name__ == "__main__":
    unittest.main()
