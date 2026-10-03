import random
import unittest

from research.experiments.finite_joint.joint_voltage import apply_transition, infer_shift, transition_edges
from research.experiments.finite_joint.block_cycle_escape import apply as apply_cycle, edges as cycle_edges
from research.experiments.finite_joint.two_switch_escape import apply as apply_switch
from k4_ramsey.engine import Graph, certificate


class JointVoltageTests(unittest.TestCase):
    def test_group_delta_and_rollback_match_full_recount(self):
        rng = random.Random(917)
        fibers = [list(range(4)), list(range(4, 8))]
        block = (1, 0, [0, 1, 2, 3])
        for old in range(4):
            rows = [["0"] * 8 for _ in range(8)]
            for u in range(8):
                for v in range(u):
                    red = rng.randrange(2)
                    rows[u][v] = rows[v][u] = str(red)
            for a, u in enumerate(fibers[1]):
                for b, v in enumerate(fibers[0]):
                    rows[u][v] = rows[v][u] = str(int(b != (a ^ old)))
            rows = ["".join(row) for row in rows]
            self.assertEqual(infer_shift(rows, fibers[1], fibers[0]), old)
            for new in range(4):
                graph = Graph(certificate(rows))
                before = graph.counts()["numerator"]
                delta = apply_transition(graph, fibers, block, old, new)
                after = graph.counts()["numerator"]
                self.assertEqual(after - before, delta)
                rollback = apply_transition(graph, fibers, block, new, old)
                self.assertEqual(rollback, -delta)
                self.assertEqual(graph.counts()["numerator"], before)
                self.assertEqual(len(transition_edges(fibers, block, old, new)),
                                 0 if old == new else 8)
                graph.close()

    def test_matching_cycle_move_on_arbitrary_block(self):
        rng = random.Random(1229)
        fibers = [list(range(4)), list(range(4, 8))]
        block = (1, 0, None)
        for p in range(4):
            for q in range(p + 1, 4):
                rows = [["0"] * 8 for _ in range(8)]
                for u in range(8):
                    for v in range(u):
                        rows[u][v] = rows[v][u] = str(rng.randrange(2))
                graph = Graph(certificate(["".join(row) for row in rows]))
                before = graph.counts()["numerator"]
                move = cycle_edges(fibers, block, p, q)
                delta = apply_cycle(graph, move)
                self.assertEqual(graph.counts()["numerator"] - before, delta)
                rollback = apply_cycle(graph, list(reversed(move)))
                self.assertEqual(rollback, -delta)
                self.assertEqual(graph.counts()["numerator"], before)
                graph.close()

    def test_two_switch_delta_rollback_and_degrees(self):
        rows = [[0] * 8 for _ in range(8)]
        for u, v in ((0, 1), (2, 3), (4, 5), (5, 6), (6, 7)):
            rows[u][v] = rows[v][u] = 1
        move = [(0, 1), (2, 3), (0, 2), (1, 3)]
        before_degrees = [sum(row) for row in rows]
        graph = Graph(certificate(["".join(map(str, row)) for row in rows]))
        before = graph.counts()["numerator"]
        delta = apply_switch(graph, move)
        self.assertEqual(graph.counts()["numerator"] - before, delta)
        after = graph.export()["red_rows"]
        self.assertEqual([row.count("1") for row in after], before_degrees)
        rollback = apply_switch(graph, list(reversed(move)))
        self.assertEqual(rollback, -delta)
        self.assertEqual(graph.counts()["numerator"], before)
        graph.close()


if __name__ == "__main__":
    unittest.main()
