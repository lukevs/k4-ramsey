import importlib.util
import itertools
from pathlib import Path
import random
import time
import unittest

from k4_ramsey.engine import Graph,certificate

spec=importlib.util.spec_from_file_location('cubic_star',Path(__file__).resolve().parents[1]/'experiments/strategies/cubic_star.py')
cubic=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cubic)


def oracle(rows):
    return sum(len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)})==1
               for vs in itertools.product(range(len(rows)),repeat=4))


def evaluate(linear,pair,triples,mask):
    return (sum(a for i,a in enumerate(linear) if mask>>i&1)
            +sum(pair[i][j] for i in range(len(linear)) for j in range(i) if mask>>i&1 and mask>>j&1)
            +sum(c for i,j,k,c in triples if mask>>i&1 and mask>>j&1 and mask>>k&1))


class CubicTests(unittest.TestCase):
    def test_all_four_vertex_graphs_and_assignments_literal(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
            graph=Graph(certificate([''.join(row) for row in rows]))
            red,blue=cubic.masks(rows)
            linear,pair,triples=cubic.compile_star(graph,rows,red,blue,0,[1,2,3])
            baseline=oracle(rows)
            values=[]
            for mask in range(8):
                candidate=[row[:] for row in rows]
                for i,v in enumerate([1,2,3]):
                    if mask>>i&1: candidate[0][v]=candidate[v][0]=str(1-int(rows[0][v]))
                actual=oracle(candidate)-baseline
                self.assertEqual(actual,evaluate(linear,pair,triples,mask))
                values.append(actual)
            result=cubic.solve(linear,pair,triples)
            self.assertTrue(result['complete'])
            self.assertEqual(result['delta'],min(values))
            self.assertEqual(values[result['mask']],min(values))
            graph.close()

    def test_gray_solver_generic_cubics_and_deadline(self):
        rng=random.Random(3351)
        for _ in range(20):
            linear=[rng.randrange(-50,50) for _ in range(8)]
            pair=[[0]*8 for _ in range(8)]
            for i in range(8):
                for j in range(i): pair[i][j]=pair[j][i]=rng.randrange(-80,81)
            triples=[(i,j,k,rng.randrange(-24,25)) for i,j,k in itertools.combinations(range(8),3)]
            values=[evaluate(linear,pair,triples,mask) for mask in range(256)]
            result=cubic.solve(linear,pair,triples)
            self.assertEqual(result['delta'],min(values))
            self.assertEqual(values[result['mask']],min(values))
            self.assertEqual(result['assignments'],256)
        self.assertFalse(cubic.solve(linear,pair,triples,time.monotonic()-1)['complete'])


if __name__=='__main__': unittest.main()
