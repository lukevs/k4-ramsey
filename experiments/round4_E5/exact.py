"""Exact rational Delta for W' = W + (a/Q) (x) sigma sigma^T with integer a, |a|<=min(N,Q-N).
F(W') = F(W) + (24*S3 + 3*S4)/(n^4 Q^6). S3 over unordered support triangles (python ints),
S4 via CRT over int64 matmuls (independent of float code path)."""
import numpy as np
from fractions import Fraction
def exact_delta(N, Q, a):
    n = N.shape[0]; M = Q - N
    frac = a != 0
    assert (a == a.T).all() and (np.abs(a) <= np.minimum(N, M)).all() and not np.diag(frac).any()
    # S3
    S3 = 0
    nbr = [np.nonzero(frac[u])[0] for u in range(n)]
    Nl = N.astype(object); Ml = M.astype(object)
    N64 = N.astype(np.int64); M64 = M.astype(np.int64)
    assert n * (int(Q) ** 3) < 2**62
    for u in range(n):
        Nu = nbr[u]; Nu = Nu[Nu > u]
        if len(Nu) < 2: continue
        ii, jj = np.nonzero(np.triu(frac[np.ix_(Nu, Nu)], 1))
        if len(ii) == 0: continue
        v, w = Nu[ii], Nu[jj]
        K = (N64[u] * N64[v] * N64[w]).sum(1) - (M64[u] * M64[v] * M64[w]).sum(1)
        for vv, ww, kk in zip(v.tolist(), w.tolist(), K.tolist()):
            S3 += int(a[u, vv]) * int(a[vv, ww]) * int(a[ww, u]) * kk
    # S4 via CRT: residues < 2^16, float64 BLAS matmul exact (sums < n*2^32 < 2^53)
    primes = [65521, 65519, 65497, 65479, 65449, 65447, 65437, 65423, 65419, 65413, 65407, 65393, 65381, 65371]
    assert n * 2**32 < 2**53
    res = []
    for p in primes:
        tot = 0
        ap = a % p
        for X in (N % p, M % p):
            for u in range(n):
                Nu = nbr[u]
                if len(Nu) == 0: continue
                Y = (ap[u, Nu][:, None] * ap[Nu, :]) % p
                L = ((Y * X[u][None, :]) % p).astype(np.float64)
                S = np.rint(L @ Y.T.astype(np.float64)).astype(np.int64) % p
                tot = (tot + int(((S * X[np.ix_(Nu, Nu)]) % p).sum() % p)) % p
        res.append(tot)
    # CRT
    Mprod = 1; x = 0
    for p, r in zip(primes, res):
        # combine x mod Mprod with r mod p
        t = ((r - x) * pow(Mprod, -1, p)) % p
        x = x + Mprod * t; Mprod *= p
    if x > Mprod // 2: x -= Mprod
    S4 = x
    assert abs(S4) < Mprod // 4
    return Fraction(24 * S3 + 3 * S4, n**4 * Q**6), S3, S4
