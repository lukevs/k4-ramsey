"""F4 task 2: certificate that the E4-3840 orbital family (456 params, G/K invariant) has a strict
local minimum x* near the stored kernel, with the stored 0/1 pattern (433 bound params) and 23 free params.
  stage1: X1 = round(x_newton * 2^64); exact g(X1); exact-gradient FD Hessian; float Newton step -> X2.
  stage2: exact F(X2), g(X2), exact-gradient FD Hessian at X2 with rigorous remainder bound; exact
          Cholesky (Fractions) of sym(H~) - mu I; Newton-Kantorovich; complementarity at x*.
Derivative bounds used (all x in [0,1]^456): |d^k f / dx_i1..dx_ik| <= 2 * 6!/(6-k)! * s/n, where
s = max row-0 multiplicity of the differentiated params (each derivative selects distinct K4 edge slots,
one slot constraint P[a,b]=i has density s_i/n, other factors in [0,1]; x2 for red+blue)."""
import sys, json, time, math
import numpy as np
from fractions import Fraction as Fr
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import crt_exact as C
ROOT = HERE.parents[1]
T0 = time.time()
stage = sys.argv[1]; out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
D = 2**64; TAU_E = 20; T = D >> TAU_E; tau = Fr(1, 2**TAU_E)
n = C.n
num16 = [int(v) for v in C.Z['num']]
free = [i for i in range(456) if 0 < num16[i] < 65536]
at0 = [i for i in range(456) if num16[i] == 0]; at1 = [i for i in range(456) if num16[i] == 65536]
sfree = int(max(C.sizes[free])); m = len(free)
M2 = Fr(2 * 30 * sfree, n); M3 = Fr(2 * 120 * sfree, n); M4 = Fr(2 * 360 * sfree, n)
def gfrac(gn): return [Fr(6 * v, n**3 * D**5) for v in gn]
def fd_hessian(X):
    Hc = [[None]*m for _ in range(m)]
    for jj, j in enumerate(free):
        Xp = list(X); Xp[j] += T; Xm = list(X); Xm[j] -= T
        gp = C.exact_eval(Xp, D, need_F=False)[1]; gm = C.exact_eval(Xm, D, need_F=False)[1]
        for ii, i in enumerate(free):
            Hc[ii][jj] = Fr(6 * (gp[i] - gm[i]), n**3 * D**5) / (2 * tau)
        print(' fd col', jj, round(time.time() - T0), flush=True)
    return Hc
log = {}
if stage == 'stage1':
    xn = np.load(HERE/'x_newton.npy')
    X1 = [0 if num16[i] == 0 else D if num16[i] == 65536 else int(round(float(xn[i]) * 2**64)) for i in range(456)]
    # sanity: exact gradient at stored point vs float
    _, g, k = C.exact_eval(X1, D, need_F=False); g = gfrac(g)
    print('stage1 |g_free|max', float(max(abs(g[i]) for i in free)), 'primes', k, round(time.time()-T0), flush=True)
    Hc = fd_hessian(X1)
    Hf = np.array([[float(v) for v in r] for r in Hc]); Hf = (Hf + Hf.T) / 2
    step = np.linalg.solve(Hf, np.array([float(g[i]) for i in free]))
    X2 = list(X1)
    for ii, i in enumerate(free): X2[i] = X1[i] - int(round(step[ii] * 2**64))
    json.dump({'D': str(D), 'X1': [str(v) for v in X1], 'X2': [str(v) for v in X2], 'step_max': float(abs(step).max()),
               'eig_float_x1': list(np.linalg.eigvalsh(Hf))}, open(out/'stage1.json', 'w'), indent=0)
    print('step max', abs(step).max(), 'eig', np.linalg.eigvalsh(Hf)[:3], round(time.time()-T0))
else:
    s1 = json.load(open(sys.argv[3]))
    X = [int(v) for v in s1['X2']]
    Fn, gn, k = C.exact_eval(X, D, need_F=True)
    Fx = Fr(Fn, n**3 * D**6); g = gfrac(gn)
    print('F(X2) =', float(Fx), 'primes', k, round(time.time()-T0), flush=True)
    Hc = fd_hessian(X)
    Hs = [[(Hc[a][b] + Hc[b][a]) / 2 for b in range(m)] for a in range(m)]
    eps = tau**2 / 6 * M4            # entrywise |H(x2) - sym(H~)|
    Hf = np.array([[float(v) for v in r] for r in Hs]); ev = np.linalg.eigvalsh(Hf)
    mu = Fr(ev[0] * 0.95).limit_denominator(10**30)
    # exact Cholesky / LDL of Hs - mu I
    A = [[Hs[a][b] - (mu if a == b else 0) for b in range(m)] for a in range(m)]
    pivots = []
    for c in range(m):
        piv = A[c][c]; pivots.append(piv)
        if piv <= 0: break
        for r_ in range(c+1, m):
            fct = A[r_][c] / piv
            for cc in range(c, m): A[r_][cc] -= fct * A[c][cc]
    pd = all(pv > 0 for pv in pivots) and len(pivots) == m
    lam0 = mu - m * eps                # lambda_min(H(x2)) >= lam0 (Frobenius bound on sym perturbation)
    beta = 1 / lam0
    gg2 = sum(g[i]**2 for i in free)
    G = Fr(math.sqrt(float(gg2)) * (1 + 1e-9)).limit_denominator(10**60)
    while G * G < gg2: G *= Fr(1000001, 1000000)
    eta = beta * G
    L = Fr(m) * M3 * Fr(math.ceil(math.sqrt(m) * 10**9), 10**9)   # ||H(x)-H(y)||_2 <= m*M3*sqrt(m)*||x-y||_2
    hK = beta * L * eta
    rho = 2 * eta
    runiq = 1 / (beta * L)
    lam_star = lam0 - L * rho
    sq = Fr(math.ceil(math.sqrt(m) * 10**9), 10**9)
    dg = M2 * sq * rho                 # |g_i(x*) - g_i(x2)| for every i
    min0 = min(g[i] for i in at0); max1 = max(g[i] for i in at1)
    xfree = [Fr(X[i], D) for i in free]
    margin_box = min(min(v, 1 - v) for v in xfree)
    dF = G * rho + Fr(1, 2) * m * M2 * rho**2
    res = dict(F_X2=str(Fx), F_X2_float=float(Fx), primes=k, pd_exact_cholesky=pd, mu=float(mu), eps_entry=float(eps),
               lam0=float(lam0), eig_float=list(ev), grad_free_norm_upper=float(G), eta=float(eta), L=float(L),
               kantorovich_h=float(hK), kantorovich_ok=bool(hK <= Fr(1, 2)), rho=float(rho), unique_radius=float(runiq),
               lam_min_Hstar_lower=float(lam_star), grad_perturb=float(dg),
               min_grad_at0_x2=float(min0), max_grad_at1_x2=float(max1),
               complementarity_ok=bool(min0 - dg > 0 and max1 + dg < 0), interior_margin=float(margin_box),
               interior_ok=bool(margin_box > rho), F_star_interval=[float(Fx - dF), float(Fx)], dF=float(dF),
               n_at0=len(at0), n_at1=len(at1), n_free=m, s_free_max=sfree, D='2^64', tau='2^-20',
               grad_bound_sorted_at0=sorted(float(g[i]) for i in at0)[:5], grad_bound_sorted_at1=sorted(float(g[i]) for i in at1)[-5:],
               X2_free_numerators=[str(X[i]) for i in free], free_params=free, F_X2_exact=str(Fx))
    json.dump(res, open(out/'certificate.json', 'w'), indent=1)
    for kk, v in res.items():
        if kk not in ('X2_free_numerators', 'free_params', 'F_X2', 'F_X2_exact'): print(kk, v)
    print('time', round(time.time()-T0))
