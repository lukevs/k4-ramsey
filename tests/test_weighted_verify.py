from fractions import Fraction
import itertools
import random
import unittest

from k4_ramsey.engine import ROOT,certificate
from k4_ramsey.weighted_verify import validate_weighted,verify


def oracle(rows,weights):
    total=0
    for vs in itertools.product(range(len(rows)),repeat=4):
        if len({rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)})==1:
            total+=weights[vs[0]]*weights[vs[1]]*weights[vs[2]]*weights[vs[3]]
    return total


class WeightedVerifyTests(unittest.TestCase):
    def test_validation(self):
        for weights in [[0,1],[True,1],[1],[65536,1]]:
            data=certificate(['00','00'])
            data['weights']=weights
            with self.assertRaises(ValueError): validate_weighted(data)

    @unittest.skipUnless((ROOT/'.lake/build/bin/check_weighted_candidate').exists(),'build weighted checker')
    def test_random_literal_oracle_and_big_integers(self):
        rng=random.Random(347)
        for weights in [[1,1,1,1],[1,3,7,11],[65535]*4,[1024,960,1088,1024]]:
            rows=[['0']*4 for _ in range(4)]
            for u in range(4):
                for v in range(u): rows[u][v]=rows[v][u]=str(rng.randrange(2))
            data=certificate([''.join(row) for row in rows])
            data['weights']=weights
            expected=oracle(rows,weights)
            result=verify(data,Fraction(expected,sum(weights)**4))
            self.assertEqual(result['numerator'],expected)
            self.assertEqual(result['denominator'],sum(weights)**4)

    @unittest.skipUnless((ROOT/'.lake/build/bin/check_weighted_candidate').exists(),'build weighted checker')
    def test_boundary_and_wrong_claim(self):
        data=certificate(['0'*65]*65)
        data['weights']=[1+i%7 for i in range(65)]
        self.assertEqual(verify(data)['density'],'1')
        with self.assertRaises(ValueError): verify(data,'1/2')


if __name__=='__main__': unittest.main()
