import importlib.util
import itertools
from pathlib import Path
import random
import unittest

from k4_ramsey.engine import Graph,certificate

spec=importlib.util.spec_from_file_location('star_search',Path(__file__).resolve().parents[1]/'experiments/strategies/star_search.py')
star=importlib.util.module_from_spec(spec)
spec.loader.exec_module(star)


def oracle(rows):
    return sum(len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)})==1
               for vs in itertools.product(range(len(rows)),repeat=4))


class StarTests(unittest.TestCase):
    def test_all_four_vertex_graphs_against_literal_oracle(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
            graph=Graph(certificate([''.join(row) for row in rows]))
            red,blue=star.masks(rows)
            base=oracle(rows)
            coefficient=star.interaction(rows,red,blue,0,1,2)
            self.assertEqual(coefficient,star.native_interaction(graph,0,1,2))
            for mask in range(4):
                candidate=[row[:] for row in rows]
                for i,v in enumerate([1,2]):
                    if mask>>i&1: candidate[0][v]=candidate[v][0]=str(1-int(rows[0][v]))
                value=(graph.delta(0,1) if mask&1 else 0)+(graph.delta(0,2) if mask&2 else 0)+(coefficient if mask==3 else 0)
                self.assertEqual(oracle(candidate)-base,value)
            self.assertEqual(graph.export()['red_rows'],[''.join(row) for row in rows])
            graph.close()

    def test_random_six_vertices(self):
        rng=random.Random(491)
        for _ in range(12):
            rows=[['0']*6 for _ in range(6)]
            for u in range(6):
                for v in range(u): rows[u][v]=rows[v][u]=str(rng.randrange(2))
            graph=Graph(certificate([''.join(row) for row in rows]))
            red,blue=star.masks(rows)
            for u,v,w in itertools.permutations(range(6),3):
                self.assertEqual(star.interaction(rows,red,blue,u,v,w),star.native_interaction(graph,u,v,w))
            graph.close()


if __name__=='__main__': unittest.main()
