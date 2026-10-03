import itertools
import ctypes as C
import random
import unittest

from k4_ramsey.engine import Graph,certificate


def random_graph(n,rng):
    rows=[['0']*n for _ in range(n)]
    for u in range(n):
        for v in range(u): rows[u][v]=rows[v][u]=str(rng.randrange(2))
    return Graph(certificate([''.join(row) for row in rows]))


class LandscapeTests(unittest.TestCase):
    def check(self,graph,pairs):
        self.assertEqual(graph.cached_deltas(pairs),graph.deltas(pairs))
        best=graph.best_cached_flip()
        if pairs:
            self.assertEqual(best[2],min(graph.deltas(pairs)))
            self.assertEqual(graph.delta(best[0],best[1]),best[2])

    def test_exhaustive_four_vertex_initial_graphs_and_flips(self):
        pairs=list(itertools.combinations(range(4),2))
        for bits in range(64):
            rows=[['0']*4 for _ in range(4)]
            for i,(u,v) in enumerate(pairs): rows[u][v]=rows[v][u]=str(bits>>i&1)
            graph=Graph(certificate([''.join(row) for row in rows]))
            graph.enable_cache()
            self.check(graph,pairs)
            for edge in pairs:
                graph.flip(*edge)
                self.check(graph,pairs)
                graph.flip(*edge)
                self.check(graph,pairs)
            graph.close()

    def test_long_random_sequences_and_word_boundaries(self):
        rng=random.Random(901)
        for n in [2,7,63,64,65,129]:
            graph=random_graph(n,rng)
            original=graph.export()
            pairs=list(itertools.combinations(range(n),2))
            graph.enable_cache()
            graph.enable_cache() # idempotent
            self.check(graph,pairs)
            moves=[]
            value=graph.counts()['numerator']
            for step in range(120):
                edge=tuple(rng.sample(range(n),2))
                self.assertEqual(graph.cached_delta(*edge),graph.delta(*edge))
                value+=graph.cached_delta(*edge)
                graph.flip(*edge)
                moves.append(edge)
                if step%20==0: self.check(graph,pairs)
            self.check(graph,pairs)
            self.assertEqual(value,graph.counts()['numerator'])
            for edge in reversed(moves): graph.flip(*edge)
            self.assertEqual(graph.export(),original)
            self.check(graph,pairs)
            graph.close()

    def test_empty_neighborhood_and_closed_graph(self):
        graph=Graph(certificate(['0']))
        self.assertIsNone(graph.best_cached_flip())
        self.assertEqual(graph.cached_deltas([]),[])
        graph.close()
        with self.assertRaises(ValueError): graph.best_cached_flip()

    def test_tabu_expiry_and_aspiration(self):
        graph=random_graph(8,random.Random(911))
        expiry=(C.c_int*64)()
        initial=graph.best_cached_flip()
        self.assertEqual(graph.best_cached_allowed(expiry,0,-10**9),initial)
        u,v,delta=initial
        expiry[u*8+v]=expiry[v*8+u]=10
        allowed=graph.best_cached_allowed(expiry,0,delta)
        self.assertNotEqual(allowed[:2],initial[:2])
        self.assertEqual(graph.best_cached_allowed(expiry,0,delta+1),initial)
        self.assertEqual(graph.best_cached_allowed(expiry,10,-10**9),initial)
        for i in range(64): expiry[i]=10
        self.assertIsNone(graph.best_cached_allowed(expiry,0,-10**9))
        with self.assertRaises(ValueError): graph.best_cached_allowed([],0,0)
        graph.close()

    def test_native_star_full_shortlist_vs_sequential_deltas(self):
        rng=random.Random(781)
        for _ in range(15):
            graph=random_graph(8,rng)
            rows=graph.export()['red_rows']
            best=0
            for u in range(8):
                for v in range(8):
                    if u==v or rows[u][v]!='0': continue
                    a=graph.delta(u,v)
                    graph.flip(u,v)
                    for w in range(8):
                        if u!=w and rows[u][w]=='1': best=min(best,a+graph.delta(u,w))
                    graph.flip(u,v)
            result=graph.best_cached_star(8)
            self.assertEqual(result[3] if result else 0,best)
            if result:
                u,v,w,delta=result
                actual=graph.cached_delta(u,v)
                graph.flip(u,v)
                actual+=graph.cached_delta(u,w)
                graph.flip(u,w)
                self.assertEqual(actual,delta)
            graph.close()


if __name__=='__main__': unittest.main()
