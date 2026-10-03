import itertools
import random
import unittest

from experiments.strategies.clone_search import apply_edges, clone_edges, select_pair, trial_clone
from k4_ramsey.engine import Graph, certificate


def oracle(rows, weights=None):
    weights = weights or [1] * len(rows)
    value = 0
    for vs in itertools.product(range(len(rows)), repeat=4):
        colors = [rows[vs[i]][vs[j]] for i, j in itertools.combinations(range(4), 2)]
        if len(set(colors)) == 1:
            weight = 1
            for v in vs:
                weight *= weights[v]
            value += weight
    return value


class CloneTests(unittest.TestCase):
    def test_all_four_vertex_graphs_all_clone_pairs(self):
        edges = list(itertools.combinations(range(4), 2))
        for mask in range(64):
            rows = [["0"] * 4 for _ in range(4)]
            for bit, (u, v) in enumerate(edges):
                rows[u][v] = rows[v][u] = str(mask >> bit & 1)
            data = certificate(["".join(row) for row in rows])
            graph = Graph(data)
            before = oracle(rows)
            for u, v in itertools.permutations(range(4), 2):
                delta, flips = trial_clone(graph, rows, u, v)
                self.assertEqual(graph.export(), data)
                new = [row[:] for row in rows]
                for w in range(4):
                    if w != u:
                        new[u][w] = new[w][u] = rows[v][w]
                self.assertEqual(new[u][v], "0")
                self.assertEqual(oracle(new) - before, delta)
                weights = [1] * 4
                weights[u], weights[v] = 0, 2
                self.assertEqual(oracle(new), oracle(rows, weights))
                apply_edges(graph, rows, flips)
                self.assertEqual(graph.export()["red_rows"], ["".join(row) for row in new])
                self.assertEqual(graph.counts()["numerator"], before + delta)
                apply_edges(graph, rows, flips)
                self.assertEqual(graph.export(), data)

    def test_trial_restores_on_error(self):
        rows = [list(s) for s in ["011", "100", "100"]]
        g = Graph(certificate(["".join(r) for r in rows]))
        before = g.export()
        original = g.calculate_delta
        calls = 0
        def fail_after_one(u, v):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("injected failure")
            return original(u, v)
        g.calculate_delta = fail_after_one
        with self.assertRaises(RuntimeError):
            trial_clone(g, rows, 0, 1)
        self.assertEqual(g.export(), before)

    def test_selection_and_invalid(self):
        rows = [list(s) for s in ["011", "100", "100"]]
        g = Graph(certificate(["".join(r) for r in rows]))
        for selection in ["random", "closest", "linear"]:
            pair, _ = select_pair(g, rows, random.Random(4), selection, 3)
            self.assertNotEqual(*pair)
        with self.assertRaises(ValueError):
            clone_edges(rows, 0, 0)


if __name__ == "__main__":
    unittest.main()
