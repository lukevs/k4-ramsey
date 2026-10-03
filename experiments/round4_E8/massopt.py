# Insert priced new type(s) and optimise all masses by projected gradient with exact quartic line search.
import json, sys, time, numpy as np
d = json.load(open(sys.argv[1])); t0 = time.time()
A = np.array(d["red_probability_numerators"], float) / d["edge_probability_denominator"]
n = len(A); extra = [np.load(p) for p in sys.argv[3:]]
if extra:
    k = len(extra); A2 = np.zeros((n+k, n+k)); A2[:n,:n] = A
    for a, r in enumerate(extra):
        A2[n+a,:n] = r; A2[:n,n+a] = r
        for b, r2 in enumerate(extra): A2[n+a,n+b] = 0.5 if a != b else r[np.argmin(np.abs(A - r).sum(1))]
    A = A2
N = len(A); B = 1 - A
m = np.append(np.full(n, 1.0/n), np.zeros(N-n))
def Rvec(m):
    out = np.empty(N)
    for i in range(N):
        u = m*A[i]; v = m*B[i]
        out[i] = u @ ((A*(A@(u[:,None]*A))) @ u) + v @ ((B*(B@(v[:,None]*B))) @ v)
    return out
R = Rvec(m); F = m @ R; F0 = F
print("start F", repr(F), "R-F new types", R[n:]-F, "time", time.time()-t0, flush=True)
for it in range(int(sys.argv[2])):
    g = 4*R; dvec = -(g - g[m > 0].mean() if True else 0)
    dvec = -(g - np.mean(g))  # simplex-projected steepest descent
    dvec[(m <= 0) & (dvec < 0)] = 0; dvec -= dvec[(m > 0)].mean() * (m > 0)  # keep sum zero on support
    dvec[(m <= 0) & (dvec < 0)] = 0
    dvec -= dvec.sum() / max(1, (m > 0).sum()) * (m > 0)
    neg = dvec < 0; smax = np.min(-m[neg] / dvec[neg]) if neg.any() else 1.0
    s1 = min(smax, 1e-3 / np.abs(dvec).max())
    ss = np.array([0, 0.25, 0.5, 0.75, 1.0]) * s1
    vals = [F] + [ (lambda mm: mm @ Rvec(mm))(m + s*dvec) for s in ss[1:] ]
    c = np.polyfit(ss, vals, 4); grid = np.linspace(0, s1, 20001); sb = grid[np.argmin(np.polyval(c, grid))]
    m = m + sb*dvec; m = np.maximum(m, 0); m /= m.sum()
    R = Rvec(m); F = m @ R
    print(f"it{it}: step={sb:.3e}/{s1:.3e} F={F!r} gain={F0-F:.3e} spread(R-F on supp)={np.ptp(R[m>0]):.3e} newmass={m[n:]} minR-F={np.min(R-F):.3e} t={time.time()-t0:.0f}", flush=True)
np.save(sys.argv[3].replace('.npy','') + "_masses.npy" if extra else "masses.npy", m)
