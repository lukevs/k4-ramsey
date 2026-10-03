import random
import unittest
from fractions import Fraction

from experiments.structural.new_profiles import explicit_expand, finite_profiles, limiting_profiles
from experiments.structural.profiles import graph_from_mask, nested_limit, profile


class NewStructuralTests(unittest.TestCase):
    def test_finite_heterogeneous_expansion(self):
        rng = random.Random(514)
        for _ in range(12):
            rules = [(graph_from_mask(3, rng.randrange(8)), [rng.randrange(2) for _ in range(3)])
                     for _ in range(2)]
            calculated = finite_profiles(rules, 2)
            for kind in range(2):
                explicit = explicit_expand(rules, kind, 2)
                expected = tuple(Fraction(x, len(explicit)**4) for x in profile(explicit))
                self.assertEqual(calculated[kind][4], expected)

    def test_uniform_reduces_to_existing_stationary_method(self):
        for mask in (0, 1, 3, 7, 12, 31, 63):
            rows = graph_from_mask(4, mask)
            rules = [(rows, [0]*4), (rows, [1]*4)]
            result = limiting_profiles(rules)
            self.assertEqual(result[0][4], nested_limit(rows))
            self.assertEqual(result[1][4], nested_limit(rows))

    def test_same_core_arbitrary_type_labels_and_convergence(self):
        rows = graph_from_mask(3, 3)
        rules = [(rows, [0, 1, 0]), (rows, [1, 0, 1])]
        result = limiting_profiles(rules)
        self.assertEqual(result[0][4], nested_limit(rows))
        self.assertEqual(result[1][4], nested_limit(rows))
        rules = [(graph_from_mask(3, 3), [0, 1, 0]), (graph_from_mask(3, 7), [1, 0, 1])]
        limit = limiting_profiles(rules)
        approximation = finite_profiles(rules, 8)
        self.assertLess(max(abs(float(a-b)) for a, b in zip(limit[0][4], approximation[0][4])), .001)


if __name__ == "__main__":
    unittest.main()
