"""F4 task 1: exact critical-point analysis of F(p,h) on [0,1]^2.
Exact algebra in sympy (QQ); root isolation by sympy's exact (Vincent/continued-fraction)
real-root isolation; values/signs by mpmath interval arithmetic on isolating intervals."""
import json, sys
import sympy as sp, mpmath
from mpmath import iv
from pathlib import Path
HERE = Path(__file__).parent
P, H, Z = sp.symbols('p h z')
d = json.load(open(HERE/'Fpoly.json'))
F = sp.Poly(sum(sp.Rational(c)*P**m[0]*H**m[1] for m, c in d['terms']), P, H, domain='QQ')
Fp, Fh = F.diff(P), F.diff(H)
print('deg F', F.total_degree(), 'deg_p', F.degree(P), 'deg_h', F.degree(H))
g = sp.gcd(Fp, Fh); print('gcd(Fp,Fh) =', g.as_expr())
iv.prec = 600
EPS = sp.Rational(1, 10**90)
def lo(x): return mpmath.mp.make_mpf(x._mpi_[0])
def hi(x): return mpmath.mp.make_mpf(x._mpi_[1])
def fmt(x, n=45):
    mpmath.mp.dps = 120
    return [mpmath.nstr(lo(x), n), mpmath.nstr(hi(x), n)]

def roots01(poly1, var):
    """isolated real roots of univariate poly in [0,1]: list of (factor, (a,b)) with exact rational a<=b"""
    out = []
    pu = sp.Poly(poly1, var)
    if pu.is_zero: raise ValueError('zero poly')
    for fac, mult in sp.factor_list(pu.as_expr())[1]:
        fu = sp.Poly(fac, var)
        if fu.degree() < 1: continue
        for (a, b), m in fu.intervals(eps=EPS):
            if b >= 0 and a <= 1:
                out.append((fu, (sp.Rational(a), sp.Rational(b))))
    return out

def I(a, b):
    return iv.mpf([mpmath.mpf(sp.Rational(a).p)/sp.Rational(a).q, mpmath.mpf(sp.Rational(b).p)/sp.Rational(b).q]) if a != b else iv.mpf(sp.Rational(a).p)/sp.Rational(a).q

def ivq(r):
    r = sp.Rational(r); return iv.mpf(r.p)/r.q

def ev(poly, pI, hI):
    tot = iv.mpf(0)
    for (i, j), c in poly.terms():
        tot += ivq(c) * pI**i * hI**j
    return tot

def ivI(a, b):
    a, b = sp.Rational(a), sp.Rational(b)
    lo = iv.mpf(a.p)/a.q; hi = iv.mpf(b.p)/b.q
    return iv.mpf([lo.a, hi.b])

# ---- interior critical points via lex Groebner basis
Gb = sp.groebner([Fp.as_expr(), Fh.as_expr()], H, P, order='lex', domain='QQ')
print('Groebner basis sizes (deg in h, deg in p):', [(sp.degree(e, H), sp.degree(e, P)) for e in Gb.exprs])
gp = [e for e in Gb.exprs if not e.has(H)]
assert len(gp) == 1; gp = sp.Poly(gp[0], P)
print('elimination poly in p: degree', gp.degree(), 'factors', [(sp.Poly(f, P).degree(), m) for f, m in sp.factor_list(gp.as_expr())[1]])
# also elimination in h (for boxes)
Gb2 = sp.groebner([Fp.as_expr(), Fh.as_expr()], P, H, order='lex', domain='QQ')
gh = sp.Poly([e for e in Gb2.exprs if not e.has(P)][0], H)
proots = roots01(gp.as_expr(), P)
hroots = [r for r in roots01(gh.as_expr(), H)]
print('p-roots in [0,1]:', [(float(a), float(b)) for _, (a, b) in proots])
print('h-roots in [0,1]:', [(float(a), float(b)) for _, (a, b) in hroots])
crit = []
for fp_, (pa, pb) in proots:
    for fh_, (ha, hb) in hroots:
        pI, hI = ivI(pa, pb), ivI(ha, hb)
        A, B = ev(Fp, pI, hI), ev(Fh, pI, hI)
        if (A.a > 0 or A.b < 0) or (B.a > 0 or B.b < 0):
            continue  # certified not a common zero
        crit.append((fp_, (pa, pb), fh_, (ha, hb)))
print('surviving candidate boxes:', len(crit))
# shape lemma: lex GB = [h - r(p), g(p)] with g irreducible => each root of g gives exactly one common zero,
# h = r(p) real when p real. So real critical points <-> real roots of g.
lin = [e for e in Gb.exprs if e.has(H)][0]
lp = sp.Poly(lin, H)
assert lp.degree() == 1 and lp.LC().is_Number, lp.LC()
r = sp.Poly(-lp.coeff_monomial(1) / lp.LC(), P)
allreal = sp.Poly(gp, P).count_roots()   # exact Sturm count of all real roots
print('shape lemma OK; g irreducible:', len(sp.factor_list(gp.as_expr())[1]) == 1, '; real roots of g (all R):', allreal,
      '; in [0,1]:', sp.Poly(gp, P).count_roots(0, 1))
for fp_, (pa, pb) in proots:
    hv = sp.Poly(r, P); x = ivI(pa, pb); t = iv.mpf(0)
    for (i,), c in hv.terms(): t += ivq(c) * x**i
    print('h = r(p) on p-box:', fmt(t, 30))
# minimal polynomial of F* : resultant_p(g(p), z - F(p, r(p)))
Fr = sp.rem(sp.Poly(sp.expand(F.as_expr().subs(H, r.as_expr())), P), sp.Poly(gp, P))
R = sp.resultant(gp.as_expr(), Z - Fr.as_expr(), P)
Rf = sp.factor_list(sp.Poly(R, Z).as_expr())[1]
print('F* resultant factors (degree, mult):', [(sp.degree(f, Z), m) for f, m in Rf])
MINF = None

# every root of gp in the (p,h) system: count check -- each common zero with p in [0,1] must have h real;
# for each p-root, the h values are the common roots of Fp(p0,.),Fh(p0,.); verify exactly one h box survives per p-root
Fpp, Fph, Fhh = Fp.diff(P), Fp.diff(H), Fh.diff(H)
res = {'interior': []}
for fp_, (pa, pb), fh_, (ha, hb) in crit:
    pI, hI = ivI(pa, pb), ivI(ha, hb)
    val = ev(F, pI, hI)
    a11, a12, a22 = ev(Fpp, pI, hI), ev(Fph, pI, hI), ev(Fhh, pI, hI)
    det = a11*a22 - a12*a12
    inside = (pa >= 0 and pb <= 1 and ha >= 0 and hb <= 1)
    rec = dict(p=[str(pa), str(pb)], h=[str(ha), str(hb)], p_minpoly=str(fp_.as_expr()), h_minpoly=str(fh_.as_expr()),
               F=fmt(val), Fpp=fmt(a11, 20), Fhh=fmt(a22, 20), detHess=fmt(det, 20), inside=bool(inside),
               Fpp_pos=bool(lo(a11) > 0), det_pos=bool(lo(det) > 0))
    for f, m in Rf:
        fz = sp.Poly(f, Z)
        vz = iv.mpf(0)
        for (i,), c in fz.terms(): vz += ivq(c) * val**i
        if lo(vz) <= 0 <= hi(vz): 
            # confirm by isolating the unique root of fz inside val's enclosure
            ints = [(a, b) for (a, b), mm in fz.intervals(eps=sp.Rational(1, 10**40)) if a <= mpmath.mpf(hi(val)) and b >= mpmath.mpf(lo(val))]
            rec['F_minpoly'] = str(fz.as_expr()); rec['F_minpoly_degree'] = fz.degree(); rec['F_isolating_hits'] = len(ints)
    print(rec)
    res['interior'].append(rec)

# ---- boundary
edges = {'p=0': (F.as_expr().subs(P, 0), H), 'p=1': (F.as_expr().subs(P, 1), H),
         'h=0': (F.as_expr().subs(H, 0), P), 'h=1': (F.as_expr().subs(H, 1), P)}
res['edges'] = {}
for name, (fe, var) in edges.items():
    fe = sp.Poly(sp.expand(fe), var)
    pts = []
    for fac, (a, b) in roots01(fe.diff(var).as_expr(), var):
        if a < 0 or b > 1: continue
        x = ivI(a, b); v = iv.mpf(0)
        for (i,), c in fe.terms(): v += ivq(c) * x**i
        pts.append(dict(x=[float(a), float(b)], F=fmt(v, 25), Flo=float(lo(v))))
    res['edges'][name] = pts
    print(name, pts)
res['corners'] = {f'{a},{b}': str(F.eval({P: a, H: b})) for a in (0, 1) for b in (0, 1)}
res['F_poly'] = str(F.as_expr()); res['g_p'] = str(gp.as_expr()); res['r_p'] = str(r.as_expr())
print('corners', {k: float(sp.Rational(v)) for k, v in res['corners'].items()})
json.dump(res, open(HERE/'crit.json', 'w'), indent=1)
