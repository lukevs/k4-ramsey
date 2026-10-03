import itertools
import random
import unittest

from experiments.diagonal.optimize import coefficients,optimize


def oracle(rows):
    return sum(len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)})==1
               for vs in itertools.product(range(len(rows)),repeat=4))


class DiagonalTests(unittest.TestCase):
    def check(self,rows):
        n=len(rows)
        baseline=oracle(rows)
        linear,_=coefficients(rows)
        values=[]
        for mask in range(1<<n):
            candidate=[row[:] for row in rows]
            for i in range(n): candidate[i][i]=str(mask>>i&1)
            actual=oracle(candidate)-baseline
            k=mask.bit_count()
            predicted=sum(linear[i] for i in range(n) if mask>>i&1)+3*k*(k-1)
            self.assertEqual(actual,predicted)
            values.append(actual)
        result=optimize(rows)
        self.assertEqual(result['delta'],min(values))
        mask=sum(1<<i for i in result['red_loop_vertices'])
        self.assertEqual(values[mask],result['delta'])
        for k,value in enumerate(result['minimum_delta_by_red_count']):
            self.assertEqual(value,min(v for mask,v in enumerate(values) if mask.bit_count()==k))

    def test_all_graphs_up_to_four_vertices_all_diagonals(self):
        for n in range(1,5):
            edges=list(itertools.combinations(range(n),2))
            for bits in range(1<<len(edges)):
                rows=[['0']*n for _ in range(n)]
                for i,(u,v) in enumerate(edges): rows[u][v]=rows[v][u]=str(bits>>i&1)
                self.check(rows)

    def test_random_five_vertices(self):
        rng=random.Random(932)
        for _ in range(12):
            rows=[['0']*5 for _ in range(5)]
            for u in range(5):
                for v in range(u): rows[u][v]=rows[v][u]=str(rng.randrange(2))
            self.check(rows)


if __name__=='__main__': unittest.main()
