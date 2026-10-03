"""F4 task 2: EXACT F and gradient of the E4-3840 orbital kernel at a rational point X/D (X integer
numerators), by CRT over primes p < 1.5e6 using float64 BLAS arithmetic on integers < 2^53 (exact).
F * n^3 * D^6 = sum_orbits cnt*w*S (red) + (blue);  dF/dx_i * n^3 * D^5 / 6 = red_i - blue_i,
with S(0,b) = sum_{c,d} W_0c W_bc W_0d W_bd W_cd  (vertex-transitive rooted formula, E4)."""
import numpy as np, math, os
from pathlib import Path
HERE = Path(__file__).parent
Z = np.load(HERE/'setup3840.npz')
P, reps, cnt, rep_pid, sizes = Z['P'].astype(np.int64), Z['reps'], Z['cnt'].astype(np.int64), Z['rep_pid'], Z['sizes']
n = P.shape[0]; NPAR = 456
assert 3840 * 1531000**2 < 2**53

def primes_below(m, k):
    out = []; c = m
    while len(out) < k:
        c -= 1
        if all(c % d for d in range(2, int(c**.5)+1)): out.append(c)
    return out
PR = primes_below(1531000, 40)

def one_prime(X, D, p):
    """returns (Fnum mod p, gnum mod p array)"""
    Fm = 0; gm = np.zeros(NPAR, dtype=np.int64)
    for colour in (0, 1):
        vals = np.array([(int(v) if colour == 0 else D - int(v)) % p for v in X], dtype=np.float64)
        W = vals[P]
        w = W[0]
        Br = np.fmod(W[reps] * w[None, :], p)
        BW = np.fmod(Br @ W, p)
        S = np.fmod((np.fmod(BW * Br, p)).sum(axis=1), p).astype(np.int64)
        wr = w[reps].astype(np.int64)
        Fm = (Fm + int(((cnt * wr % p) * S % p).sum())) % p
        gi = np.bincount(rep_pid, weights=(cnt * S % p).astype(np.float64), minlength=NPAR).astype(np.int64) % p
        gm = (gm + gi) % p if colour == 0 else (gm - gi) % p
    return Fm, gm

def crt(res, ps, signed):
    M = 1; x = 0
    for r, p in zip(res, ps):
        # x = x mod M, r mod p
        t = ((r - x) * pow(M, -1, p)) % p
        x += M * t; M *= p
    if signed and x > M // 2: x -= M
    return x, M

def exact_eval(X, D, need_F=True):
    """X: list of python ints. Returns (Fnum, gnum list) with F = Fnum/(n^3 D^6), g_i = 6*gnum_i/(n^3 D^5)."""
    bitsF = math.ceil(math.log2(2 * n**3)) + 6 * D.bit_length() + 2
    bitsg = math.ceil(math.log2(2 * n**3)) + 5 * D.bit_length() + 2
    bits = bitsF if need_F else bitsg
    ps = []; acc = 0
    for p in PR:
        ps.append(p); acc += math.log2(p)
        if acc > bits: break
    rs = [one_prime(X, D, p) for p in ps]
    Fn = crt([r[0] for r in rs], ps, False)[0] if need_F else None
    g = [crt([int(r[1][i]) for r in rs], ps, True)[0] for i in range(NPAR)]
    return Fn, g, len(ps)
