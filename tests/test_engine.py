import itertools
import random
import unittest

from k4_ramsey.engine import Graph, certificate


def oracle(rows):
    total = 0
    for vs in itertools.product(range(len(rows)), repeat=4):
        colors = [rows[vs[i]][vs[j]] for i in range(4) for j in range(i+1,4)]
        total += len(set(colors)) == 1
    return total


def random_rows(n, rng):
    a = [['0']*n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            a[i][j] = a[j][i] = str(rng.randrange(2))
    return [''.join(r) for r in a]


class EngineTests(unittest.TestCase):
    def test_exhaustive_five_vertices_and_deltas(self):
        edges = list(itertools.combinations(range(5),2))
        for bits in range(1 << len(edges)):
            a = [['0']*5 for _ in range(5)]
            for k,(i,j) in enumerate(edges):
                a[i][j] = a[j][i] = str((bits>>k)&1)
            g = Graph(certificate([''.join(r) for r in a]))
            n = oracle(g.export()['red_rows'])
            self.assertEqual(g.counts()['numerator'], n)
            for i,j in edges:
                delta = g.delta(i,j)
                g.flip(i,j)
                self.assertEqual(oracle(g.export()['red_rows']), n+delta)
                self.assertEqual(g.delta(i,j), -delta)
                g.flip(i,j)

    def test_long_sequences_boundaries_and_pairs(self):
        rng = random.Random(81)
        for n in [2,7,63,64,65,127,128,129]:
            g = Graph(certificate(random_rows(n,rng)))
            initial = g.export()
            value = g.counts()['numerator']
            moves = []
            for step in range(80):
                i,j = rng.sample(range(n),2)
                value += g.delta(i,j)
                g.flip(i,j)
                moves.append((i,j))
                if step%20 == 0:
                    self.assertEqual(g.counts()['numerator'], value)
            self.assertEqual(g.counts()['numerator'], value)
            for i,j in reversed(moves):
                g.flip(i,j)
            self.assertEqual(g.export(), initial)
            pairs = [tuple(rng.sample(range(n),2)) for _ in range(20)]
            self.assertEqual(g.deltas(pairs), [g.delta(*p) for p in pairs])

    def test_complete_empty_and_invalid(self):
        for n in [1,2,4,63,64,65,127,128,129]:
            empty = Graph(certificate(['0'*n]*n))
            self.assertEqual(empty.counts()['numerator'],n**4)
            complete = Graph(certificate([''.join('0' if i==j else '1' for j in range(n))
                                          for i in range(n)]))
            self.assertEqual(complete.counts()['numerator'],n+ n*(n-1)*(n-2)*(n-3))
        for data in [certificate(['1']),certificate(['01','00']),certificate(['00'])]:
            with self.assertRaises(ValueError): Graph(data)
        g = Graph(certificate(['00','00']))
        for edge in [(-1,1),(0,2),(0,0)]:
            with self.assertRaises(ValueError): g.delta(*edge)


if __name__ == '__main__':
    unittest.main()
