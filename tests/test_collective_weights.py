from fractions import Fraction
import itertools
import random
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from experiments.weights.collective_gradient import differences,evaluate,gradient_direction
from experiments.weights.collective_curvature import hessian,projected_cg,quantize
from experiments.weights.pair_transfer import features
from k4_ramsey.engine import Graph,certificate
from experiments.weights.collective_graphon import positive_restricted_hessian


def oracle(rows,weights):
    value=0
    for vertices in itertools.product(range(len(rows)),repeat=4):
        colors={rows[vertices[i]][vertices[j]] for i in range(4) for j in range(i+1,4)}
        if len(colors)==1:
            product=1
            for v in vertices: product*=weights[v]
            value+=product
    return value


class CollectiveWeightTests(unittest.TestCase):
    def test_exact_quartic_all_four_vertex_graphs(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
            for direction in ([1,-1,1,-1],[3,-2,-2,1]):
                values=[oracle(rows,[32+s*d for d in direction]) for s in range(5)]
                poly=differences(values)
                for s in (-3,5,9):
                    self.assertEqual(evaluate(poly,s),oracle(rows,[32+s*d for d in direction]))

    def test_gradient_zero_sum_descent(self):
        rng=random.Random(1)
        for n in (1,2,7,32,768):
            for _ in range(20):
                gradient=[rng.randrange(-1000,1000) for _ in range(n)]
                direction=gradient_direction(gradient)
                self.assertEqual(sum(direction),0)
                self.assertLessEqual(sum(g*d for g,d in zip(gradient,direction)),0)
                self.assertLessEqual(max(map(abs,direction)),33)
        self.assertEqual(gradient_direction([7]*8),[0]*8)

    def test_degree_four_identity(self):
        coefs=[3,-5,7,-11,13]
        direct=lambda s:sum(Fraction(c)*s**i for i,c in enumerate(coefs))
        poly=differences([direct(s) for s in range(5)])
        for s in range(-10,100): self.assertEqual(evaluate(poly,s),direct(s))

    def test_hessian_all_tiny_graphs(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
            graph=Graph(certificate([''.join(row) for row in rows]))
            try: matrix=hessian(features(graph))
            finally: graph.close()
            for direction in ([1,-1,1,-1],[3,-2,-2,1]):
                values=[oracle(rows,[1+s*d for d in direction]) for s in range(5)]
                # Quartic symmetric difference extracts second derivative exactly.
                p=differences(values)
                curvature=(-evaluate(p,2)+16*evaluate(p,1)-30*evaluate(p,0)+16*evaluate(p,-1)-evaluate(p,-2))/12
                expected=sum(direction[i]*matrix[i][j]*direction[j] for i in range(4) for j in range(4))
                self.assertEqual(curvature,expected)

    def test_cg_projected_quadratic(self):
        matrix=[[4,1,1],[1,4,1],[1,1,4]]
        x,history=projected_cg(matrix,[1,2,3])
        self.assertAlmostEqual(sum(x),0)
        for actual,expected in zip(x,[1/3,0,-1/3]): self.assertAlmostEqual(actual,expected)
        direction=quantize(x,32)
        self.assertEqual(direction,[32,0,-32])

    def test_exact_restricted_curvature_certificate(self):
        positive=[[4,1,1],[1,4,1],[1,1,4]]
        self.assertEqual(positive_restricted_hessian(positive)['status'],
                         'exact_positive_definite_on_zero_sum_subspace')
        negative=[[-4,1,1],[1,-4,1],[1,1,-4]]
        self.assertEqual(positive_restricted_hessian(negative)['status'],
                         'not_strictly_positive_by_this_test')
        self.assertEqual(positive_restricted_hessian([[1]*3 for _ in range(3)])['status'],'zero_hessian')

    def test_graphon_mass_derivatives_against_literal_tuples(self):
        with tempfile.TemporaryDirectory() as directory:
            binary=Path(directory)/'derivative'
            source=Path(__file__).resolve().parents[1]/'experiments/weights/collective_graphon.cpp'
            subprocess.run(['c++','-O2','-std=c++17',str(source),'-o',str(binary)],check=True,timeout=30)
            for matrix in ([[0,1],[1,0]],[[0,1,2],[1,0,1],[2,1,0]]):
                n=len(matrix);den=2
                payload=f'{n} {den}\n'+'\n'.join(' '.join(map(str,row))for row in matrix)+'\n'
                values=list(map(int,subprocess.check_output([str(binary)],input=payload,text=True).split()))
                total=0;gradient=[0]*n;h=[[0]*n for _ in range(n)]
                for vertices in itertools.product(range(n),repeat=4):
                    red=blue=1
                    for i,j in itertools.combinations(range(4),2):
                        p=matrix[vertices[i]][vertices[j]]
                        red*=p;blue*=den-p
                    value=red+blue;total+=value
                    counts=[vertices.count(i)for i in range(n)]
                    for i in range(n):
                        gradient[i]+=counts[i]*value
                        for j in range(n): h[i][j]+=counts[i]*(counts[j]-(i==j))*value
                self.assertEqual(values,[total]+gradient+[v for row in h for v in row])


if __name__=='__main__': unittest.main()
