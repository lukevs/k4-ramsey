from fractions import Fraction
import itertools
import unittest

from experiments.weights.pair_transfer import coefficients,features,grid_minimum
from k4_ramsey.engine import Graph,certificate


def oracle(rows,weights):
    value=Fraction(0)
    for vs in itertools.product(range(len(rows)),repeat=4):
        if len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)})==1:
            value+=weights[vs[0]]*weights[vs[1]]*weights[vs[2]]*weights[vs[3]]
    return value


class WeightTests(unittest.TestCase):
    def test_all_four_vertex_graphs_pairs_rational_steps(self):
        edges=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
            graph=Graph(certificate([''.join(row) for row in rows]))
            f=features(graph)
            baseline=oracle(rows,[1]*4)
            self.assertEqual(f['numerator'],baseline)
            for u,v in edges:
                a,b,c,d=coefficients(f,u,v)
                for t in map(Fraction,[-1,Fraction(-1,2),0,Fraction(1,2),1]):
                    weights=[1]*4
                    weights[u]-=t
                    weights[v]+=t
                    self.assertEqual(oracle(rows,weights)-baseline,a*t+b*t*t+c*t**3+d*t**4)
            graph.close()

    def test_grid_minimum(self):
        for coefs in [(2,3,4,5),(-4,3,0,0),(-10,-3,20,-2)]:
            gain,t=grid_minimum(coefs,16)
            values=[sum(Fraction(s,16)**(i+1)*c for i,c in enumerate(coefs)) for s in range(16)]
            self.assertEqual(gain,min(values))
            self.assertEqual(gain,sum(t**(i+1)*c for i,c in enumerate(coefs)))


if __name__=='__main__': unittest.main()
