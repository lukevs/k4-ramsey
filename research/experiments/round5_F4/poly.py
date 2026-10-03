"""F4 task 1: exact polynomial F(p,h) of the B192 Clebsch-design family.
Built directly from research/experiments/round4_E11/rule.json (types) + Clebsch set C.
Method: W is a 192x192 matrix of labels {0,1,p,h}. For integer (p,h) the rooted K4 sum
R(W) = sum_{b,c,d} W0b W0c W0d Wbc Wbd Wcd is an exact integer (int64 / python int);
F = [R(W) + R(1-W)] / 192^3 (vertex-transitivity checked at every block representative).
F has total degree <= 6, so exact tensor interpolation on {0..6}^2 recovers it."""
import json, sys, itertools
import numpy as np, sympy as sp
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
T = json.load(open(ROOT/'research/experiments/round4_E11/rule.json'))['types']
C = {0, 1, 2, 4, 8, 15}
q, k = 16, 12; N = q*k
# label codes: 0 -> 0, 1 -> 1, 2 -> p, 3 -> h
L = np.zeros((N, N), dtype=np.int64)
for s in range(k):
    for t in range(k):
        for x in range(q):
            for y in range(q):
                z = x ^ y; ty = T[s][t]
                if ty == 'Z': c = 0 if z in C else 1
                elif ty == 'X': c = 1 if z in C else 0
                elif ty == 'P': c = 2 if z in C else 0
                else: c = (3 if z == 0 else 1) if z in C else 0
                L[s*q+x, t*q+y] = c
assert (L == L.T).all()

def rooted(W, a):
    V = W[a][None, :] * W          # V[b,c] = W_ab W_bc
    G = (V @ W) * V                # sum_d (W_ad W_bd) W_cd ... careful: see below
    # R = sum_b W_ab sum_{c,d} (W_ac W_bc)(W_ad W_bd) W_cd = sum_b W_ab * (V_b W V_b^T)
    return int((W[a] * G.sum(axis=1)).sum())

def mats(p, h):
    red = np.choose(L, [0, 1, p, h]).astype(np.int64)
    blue = 1 - red
    return red, blue

def Fint(p, h, reps=(0,)):
    red, blue = mats(p, h)
    vals = [rooted(red, a) + rooted(blue, a) for a in reps]
    assert len(set(vals)) == 1, vals
    return vals[0]

def Fexact(p, h):
    """exact F at rational (p,h): scale to integers. p=a/D,h=b/D; W*D integer; degree-6 homogenise."""
    p, h = Fraction(p), Fraction(h)
    import math; D = math.lcm(p.denominator, h.denominator)
    a, b = int(p*D), int(h*D)
    red = np.choose(L, [0, D, a, b]).astype(object); blue = D - red
    return Fraction(rooted(red, 0) + rooted(blue, 0), N**3 * D**6)

if __name__ == '__main__':
    P, H = sp.symbols('p h')
    reps = tuple(s*q for s in range(k))
    pts = range(7)
    vals = {}
    for i in pts:
        for j in pts:
            vals[i, j] = Fint(i, j, reps if (i, j) in [(2, 3), (5, 4)] else (0,))
    # tensor Lagrange interpolation
    poly = 0
    for i in pts:
        Li = sp.prod([(P - m) / (i - m) for m in pts if m != i])
        for j in pts:
            Lj = sp.prod([(H - m) / (j - m) for m in pts if m != j])
            poly += vals[i, j] * Li * Lj
    Fpoly = sp.Poly(sp.expand(poly) / N**3, P, H, domain='QQ')
    print('total degree', Fpoly.total_degree())
    # verification vs lane P exact values + independent exact evaluator at extra points
    chk = {(Fraction(32, 41), Fraction(22, 41)): Fraction(1013294255057839, 33620705806123008),
           (Fraction(4, 5), Fraction(2, 5)): Fraction(3333439223, 110592000000)}
    for (a, b), v in chk.items():
        e = Fpoly.eval({P: sp.Rational(a.numerator, a.denominator), H: sp.Rational(b.numerator, b.denominator)})
        print('check P', a, b, e == sp.Rational(v.numerator, v.denominator), Fexact(a, b) == v)
    for (a, b) in [(Fraction(51064, 65536), Fraction(35015, 65536)), (Fraction(1, 3), Fraction(7, 9)), (Fraction(9, 2), Fraction(-3, 7))]:
        e = Fpoly.eval({P: sp.Rational(a.numerator, a.denominator), H: sp.Rational(b.numerator, b.denominator)})
        print('check fresh', a, b, e == sp.Rational(Fexact(a, b).numerator, Fexact(a, b).denominator), float(e))
    json.dump({'N': N, 'terms': [[list(m), str(c)] for m, c in Fpoly.terms()]}, open(Path(__file__).parent/'Fpoly.json', 'w'), indent=0)
    print(sp.factor(Fpoly.as_expr()))
    print(Fpoly.as_expr())
