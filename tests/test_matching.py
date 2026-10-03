import importlib.util
import itertools
from pathlib import Path
import random
import time
import unittest

from k4_ramsey.engine import Graph, certificate

spec = importlib.util.spec_from_file_location('matching_search',Path(__file__).resolve().parents[1]/'experiments/strategies/matching_search.py')
matching = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matching)


def oracle(rows):
    return sum(len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)}) == 1
               for vs in itertools.product(range(len(rows)),repeat=4))


class MatchingTests(unittest.TestCase):
    def test_all_four_vertex_graphs_literal(self):
        edges = list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows = [['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits >> i & 1)
            graph = Graph(certificate([''.join(row) for row in rows]))
            free = [(0,1),(2,3)]
            linear, matrix = matching.quadratic(graph,free)
            baseline = oracle(rows)
            costs = []
            for mask in range(4):
                candidate = [row[:] for row in rows]
                for i,(u,v) in enumerate(free):
                    if mask >> i & 1: candidate[u][v]=candidate[v][u]=str(1-int(rows[u][v]))
                delta = oracle(candidate)-baseline
                predicted = sum(linear[i] for i in range(2) if mask >> i & 1)+(matrix[0][1] if mask==3 else 0)
                self.assertEqual(delta,predicted)
                costs.append(delta)
            result = matching.solve(linear,matrix)
            self.assertTrue(result['complete'])
            self.assertEqual(result['delta'],min(costs))
            self.assertEqual(costs[result['mask']],min(costs))
            graph.close()

    def test_six_vertices_and_all_matching_assignments(self):
        rng = random.Random(413)
        for _ in range(8):
            rows = [['0']*6 for _ in range(6)]
            for u in range(6):
                for v in range(u): rows[u][v]=rows[v][u]=str(rng.randrange(2))
            graph=Graph(certificate([''.join(row) for row in rows]))
            edges=[(0,1),(2,3),(4,5)]
            linear,matrix=matching.quadratic(graph,edges)
            base=oracle(rows)
            for mask in range(8):
                candidate=[row[:] for row in rows]
                for i,(u,v) in enumerate(edges):
                    if mask>>i&1: candidate[u][v]=candidate[v][u]=str(1-int(rows[u][v]))
                value=sum(linear[i] for i in range(3) if mask>>i&1)
                value+=sum(matrix[i][j] for i in range(3) for j in range(i) if mask>>i&1 and mask>>j&1)
                self.assertEqual(oracle(candidate)-base,value)
            graph.close()

    def test_generic_solver_and_timeout(self):
        rng=random.Random(555)
        for _ in range(25):
            linear=[rng.randrange(-40,80) for _ in range(8)]
            matrix=[[0]*8 for _ in range(8)]
            for i in range(8):
                for j in range(i): matrix[i][j]=matrix[j][i]=rng.randrange(-24,25)
            costs=[sum(linear[i] for i in range(8) if mask>>i&1)+sum(matrix[i][j] for i in range(8) for j in range(i) if mask>>i&1 and mask>>j&1) for mask in range(256)]
            result=matching.solve(linear,matrix)
            self.assertEqual(result['delta'],min(costs))
            self.assertEqual(costs[result['mask']],result['delta'])
        result=matching.solve([1,1],[[0,-24],[-24,0]],time.monotonic()-1)
        self.assertFalse(result['complete'])
        self.assertEqual(result['delta'],0)

    def test_pair_screen(self):
        rows=['0100','1000','0000','0000']
        edges,examined,complete=matching.improving_pair(rows,[(2,(0,1)),(10,(2,3))],float('inf'))
        self.assertEqual(edges,[(0,1),(2,3)])
        self.assertFalse(complete)
        edges,examined,complete=matching.improving_pair(rows,[(14,(0,1)),(10,(2,3))],float('inf'))
        self.assertFalse(edges)
        self.assertTrue(complete)


if __name__ == '__main__': unittest.main()
