import itertools
import random
import unittest

from experiments.algebraic.switching import canonical_cut, switch
from experiments.algebraic.gm_cells import cells, gm_switch, is_cell
from experiments.algebraic.lift import (decompose, gauge_relabel, materialize, PERMUTATIONS,
    REGULAR_TWO,half_blocks,materialize_half)
from experiments.algebraic.lift import standardize_halves,triangle_constraint_components
from experiments.algebraic.cycle_model import build_model
from k4_ramsey.engine import Graph, certificate


def oracle(rows):
    n = len(rows)
    return sum(len({rows[vs[i]][vs[j]] for i,j in itertools.combinations(range(4),2)}) == 1
               for vs in itertools.product(range(n),repeat=4))


class SwitchingTests(unittest.TestCase):
    def test_exact_cycle_model(self):
        fibers=[list(range(4*i,4*i+4)) for i in range(4)]
        rows=['0'*16 for _ in range(16)]
        blocks=[(2,0,(0,1,2,3)),(2,1,(0,1,2,3)),(3,0,(0,1,2,3)),(3,1,(0,1,2,3))]
        halves=[(1,0,(12,12,3,3)),(3,2,(12,12,3,3))]
        rows=materialize(rows,fibers,blocks,[b[2] for b in blocks])
        rows=materialize_half(rows,fibers,halves,[b[2] for b in halves])
        model=build_model(rows,fibers)
        initial=oracle(rows)
        for code in range(16):
            bits=[code>>e&1 for e in range(4)]
            predicted=initial+sum(t['delta']*((sum(bits[e] for e in t['edges'])%2)-t['baseline_parity'])
                                  for t in model['terms'])
            changed=materialize(rows,fibers,model['blocks'],[tuple(a^b for a in range(4)) for b in bits])
            self.assertEqual(predicted,oracle(changed))

    def test_triangle_constraints(self):
        fibers=[list(range(4*i,4*i+4)) for i in range(4)]
        rows=['0'*16 for _ in range(16)]
        blocks=[(2,0,(0,1,2,3)),(2,1,(0,1,2,3)),(3,0,(0,1,2,3)),(3,1,(0,1,2,3))]
        halves=[(1,0,(3,3,12,12)),(3,2,(3,3,12,12))]
        rows=materialize(rows,fibers,blocks,[b[2] for b in blocks])
        rows=materialize_half(rows,fibers,halves,[b[2] for b in halves])
        changed,gauges=standardize_halves(rows,fibers)
        self.assertEqual(oracle(changed),oracle(rows))
        blocks,_=decompose(changed,fibers)
        halves=half_blocks(changed,fibers)
        components,colors,adjacency=triangle_constraint_components(blocks,halves)
        self.assertEqual(list(map(len,components)),[4])
        anti=materialize(changed,fibers,blocks,[tuple(a^(2*colors[e]) for a in range(4)) for e in range(4)])
        for i,j,_ in halves:
            for k in range(4):
                if k in (i,j):continue
                # Count blue transversals of each partial quotient triangle.
                self.assertEqual(sum(anti[a][b]==anti[a][c]==anti[b][c]=='0'
                    for a in fibers[i] for b in fibers[j] for c in fibers[k]),0)

    def test_all_regular_two_patterns(self):
        self.assertEqual(len(REGULAR_TWO),90)
        self.assertEqual(sum(len(set(p))==2 for p in REGULAR_TWO),18)
        fibers=[list(range(4)),list(range(4,8))]
        rows=['0'*8 for _ in range(8)]
        blocks=[(1,0,None)]
        for pattern in REGULAR_TWO:
            changed=materialize_half(rows,fibers,blocks,[pattern])
            self.assertEqual(materialize_half(rows,fibers,blocks,[list(pattern)]),changed)
            self.assertEqual(half_blocks(changed,fibers),[(1,0,pattern)])
            self.assertEqual([row.count('1') for row in changed],[2]*8)
            g=Graph(certificate(changed))
            self.assertEqual(g.counts()['numerator'],oracle(changed))
            g.close()

    def test_lift_materialization_and_gauge(self):
        rng=random.Random(484)
        fibers=[list(range(4*i,4*i+4)) for i in range(3)]
        rows=['0'*12 for _ in range(12)]
        blocks=[(1,0,(0,1,2,3)),(2,0,(0,1,2,3)),(2,1,(0,1,2,3))]
        original=materialize(rows,fibers,blocks,[b[2] for b in blocks])
        recovered,kinds=decompose(original,fibers)
        self.assertEqual(recovered,blocks)
        self.assertEqual(kinds,{3:3})
        baseline=oracle(original)
        for _ in range(12):
            gauges=[rng.choice(PERMUTATIONS) for _ in fibers]
            gauged=gauge_relabel(original,fibers,gauges)
            self.assertEqual(oracle(gauged),baseline)
            inverse=[tuple(p.index(i) for i in range(4)) for p in gauges]
            self.assertEqual(gauge_relabel(gauged,fibers,inverse),original)
            changed=materialize(original,fibers,blocks,[rng.choice(PERMUTATIONS) for _ in blocks])
            self.assertEqual([row.count('1') for row in changed],[6]*12)
            self.assertEqual(materialize(changed,fibers,blocks,[b[2] for b in blocks]),original)
            g=Graph(certificate(changed))
            self.assertEqual(g.counts()['numerator'],oracle(changed))
            g.close()

    def test_gm_complete_enumeration_and_switch(self):
        # Every graph of order <=5; oracle directly checks every four-set.
        for n in range(1,6):
            edges=list(itertools.combinations(range(n),2))
            for mask in range(1<<len(edges)):
                a=[['0']*n for _ in range(n)]
                for bit,(i,j) in enumerate(edges):
                    a[i][j]=a[j][i]=str(mask>>bit&1)
                rows=[''.join(row) for row in a]
                expected=[cell for cell in itertools.combinations(range(n),4) if is_cell(rows,cell)]
                self.assertEqual(cells(rows)[0],expected)
                for cell in expected:
                    result=gm_switch(rows,cell)
                    self.assertEqual(gm_switch(result,cell),rows)
                    g=Graph(certificate(result))
                    self.assertEqual(g.counts()['numerator'],oracle(result))
                    g.close()

    def test_switch_involution_and_native_objective(self):
        rng = random.Random(403)
        for n in range(1,8):
            for _ in range(5):
                a = [['0']*n for _ in range(n)]
                for i,j in itertools.combinations(range(n),2):
                    a[i][j] = a[j][i] = str(rng.randrange(2))
                rows = [''.join(row) for row in a]
                cut = [rng.randrange(2) for _ in range(n)]
                result = switch(rows,cut)
                self.assertEqual(switch(result,cut), rows)
                self.assertEqual(switch(rows,[1-x for x in cut]),result)
                self.assertEqual(switch(rows,canonical_cut(cut)),result)
                self.assertTrue(all(result[i][i]=='0' for i in range(n)))
                # Exact entrywise Seidel conjugation proves spectrum invariance.
                for i,j in itertools.combinations(range(n),2):
                    self.assertEqual(1-2*int(result[i][j]),
                        (-1)**(cut[i]+cut[j])*(1-2*int(rows[i][j])))
                g=Graph(certificate(result))
                self.assertEqual(g.counts()['numerator'],oracle(result))
                g.close()


if __name__ == '__main__':
    unittest.main()
