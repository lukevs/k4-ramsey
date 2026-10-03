import ctypes as C
import unittest

from experiments.strategies.tabu_search import expiry_step, tabu_walk
from k4_ramsey.engine import Graph, certificate


class TabuTests(unittest.TestCase):
    def test_tenure_boundaries(self):
        self.assertEqual(expiry_step(0, 0), 1)
        self.assertEqual(expiry_step(4, 3), 8)
        self.assertTrue(all(expiry_step(4, 3) > step for step in (5, 6, 7)))
        self.assertFalse(expiry_step(4, 3) > 8)

    def test_native_eligibility_and_strict_aspiration(self):
        g = Graph(certificate(["000", "000", "000"]))
        g.enable_cache()
        expiry = (C.c_int * 9)(*([10] * 9))
        delta = g.delta(0, 1)
        self.assertIsNone(g.best_cached_allowed(expiry, 0, delta))
        self.assertEqual(g.best_cached_allowed(expiry, 0, delta + 1), (0, 1, delta))
        self.assertEqual(g.best_cached_allowed(expiry, 10, -10**9), (0, 1, delta))
        expiry[1] = expiry[3] = 0
        self.assertEqual(g.best_cached_allowed(expiry, 0, -10**9), (0, 1, delta))

    def test_walk_best_retention_and_determinism(self):
        data = certificate(["00000"] * 5)
        config = {"max_moves": 30, "tenure": 1, "tenure_jitter": 2}
        a, report_a = tabu_walk(data, seed=71, seconds=5, config=config)
        b, report_b = tabu_walk(data, seed=71, seconds=5, config=config)
        self.assertEqual(a, b)
        self.assertEqual(report_a["trace"], report_b["trace"])
        self.assertLessEqual(report_a["numerator"], report_a["initial_numerator"])
        self.assertLessEqual(report_a["numerator"], report_a["final_walk_numerator"])
        self.assertEqual(Graph(a).counts()["numerator"], report_a["numerator"])

    def test_no_allowed_move_retains_best(self):
        data = certificate(["00", "00"])
        best, report = tabu_walk(data, seed=0, seconds=5,
                                 config={"max_moves": 10, "tenure": 5, "tenure_jitter": 0})
        self.assertEqual(report["termination"], "no_allowed_move")
        self.assertEqual(report["attempted"], 1)
        self.assertEqual(report["numerator"], Graph(best).counts()["numerator"])


if __name__ == "__main__":
    unittest.main()
