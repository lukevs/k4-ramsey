"""Lane F5 (round 5): independent exact checker for graphons with a Z2^k fibre structure.

Reads ONLY a rational-step-graphon-v1 candidate matrix (uniform weights).  No search-side
formula or evaluator code is used.  Method (derived here):

1. Fibre discovery.  Find every XOR mask g in [1,N) such that i -> i^g is a permutation of
   [N] and W[i^g][j^g] == W[i][j] for all i,j (exhaustive over masks, exact integers).  The
   good masks with 0 form a group G ~= Z2^k acting freely; its orbits are the fibres.
   Label vertex i = r_u ^ g(x), x in F2^k (coordinates w.r.t. a basis of G), r_u = orbit min.
   Invariance gives W((u,x),(v,y)) = f_uv(x+y) with f_uv(z) = W[r_u][r_v ^ g(z)].
2. Integer Fourier transform F_c(u,v) = sum_z f_uv(z) (-1)^{c.z}; verify entry by entry
   2^k W[i][j] == sum_c F_c(u,v) (-1)^{c.x} (-1)^{c.y}  (zero mismatches required).
3. With D = sum over all N^4 ordered tuples of prod_{6 edges} W (denominator N^4 Q^6),
   expanding each edge in characters and summing over fibre coordinates:
       D = 2^{-2k} sum_{c in cycle space of K4 (x) F2^k} S(c),
       S(c) = sum_{u in [n]^4} prod_{e=ab} F_{c_e}(u_a,u_b).
   Cycle space basis: c = a*T123 + b*T124 + d*T134, a,b,d in F2^k, so
   c12=a+b, c13=a+d, c14=b+d, c23=a, c24=b, c34=d.  S is invariant under the S4 vertex
   action (F_c symmetric), so only orbit representatives are computed.
4. S(c) exactly: pair-quadratic count mod 8 primes < 2^21 with float64 dgemm (every
   intermediate < 2^53 asserted), CRT with symmetric lift; the bound
   |S| <= n^4 * prod_e max|F_{c_e}| is checked against prod(primes)/2.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k4mix")
PRIMES = [2097143, 2097133, 2097131, 2097097, 2097091, 2097083, 2097047, 2097041,
          2097031, 2097023]
EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]  # 12 13 14 23 24 34


def is_prime(p):
    if p < 2:
        return False
    for q in range(2, int(p ** 0.5) + 1):
        if p % q == 0:
            return False
    return True


assert all(is_prime(p) for p in PRIMES) and len(set(PRIMES)) == len(PRIMES)


# ---------------------------------------------------------------- fibre discovery
def discover_group(W):
    N = W.shape[0]
    idx = np.arange(N)
    good = []
    for g in range(1, N):
        perm = idx ^ g
        if perm.max() >= N:
            continue
        # cheap filter on row 0, then full check
        if not np.array_equal(W[g, perm], W[0]):
            continue
        if np.array_equal(W[np.ix_(perm, perm)], W):
            good.append(g)
    G = [0] + good
    Gs = set(G)
    for a in G:  # closure check (automatic in theory; checked anyway)
        for b in G:
            assert (a ^ b) in Gs
    basis = []
    span = {0}
    for g in good:
        if g not in span:
            basis.append(g)
            span = span | {s ^ g for s in span}
    assert span == Gs
    k = len(basis)
    assert len(G) == 2 ** k
    return basis, k


def fibre_labels(N, basis):
    k = len(basis)
    gx = []  # g(x) for x = 0..2^k-1 (bit j of x -> basis[j])
    for x in range(2 ** k):
        g = 0
        for j in range(k):
            if (x >> j) & 1:
                g ^= basis[j]
        gx.append(g)
    reps = sorted({min(i ^ g for g in gx) for i in range(N)})
    n = len(reps)
    assert n * 2 ** k == N
    base = {}
    for u, r in enumerate(reps):
        for x, g in enumerate(gx):
            i = r ^ g
            assert i not in base
            base[i] = (u, x)
    assert len(base) == N
    return reps, gx, base


def popparity(v):
    return bin(v).count("1") & 1


def fourier_blocks(W, basis):
    """Return k, n, F (2^k x n x n int64), label arrays, and reconstruction mismatch count."""
    N = W.shape[0]
    k = len(basis)
    K = 2 ** k
    reps, gx, base = fibre_labels(N, basis)
    n = len(reps)
    reps_a = np.array(reps)
    f = np.zeros((K, n, n), dtype=np.int64)
    for z in range(K):
        f[z] = W[np.ix_(reps_a, reps_a ^ gx[z])]
    chi = np.array([[1 - 2 * popparity(c & z) for z in range(K)] for c in range(K)],
                   dtype=np.int64)
    F = np.einsum("cz,zuv->cuv", chi, f)
    # entrywise reconstruction of the full matrix
    uu = np.array([base[i][0] for i in range(N)])
    xx = np.array([base[i][1] for i in range(N)])
    recon = np.zeros((N, N), dtype=np.int64)
    for c in range(K):
        s = chi[c, xx]  # chi_c(x_i)
        recon += F[c][np.ix_(uu, uu)] * np.outer(s, s)
    mism = int(np.count_nonzero(recon != K * W.astype(np.int64)))
    # also: the invariance implies f symmetric in (u,v) blockwise
    return k, n, F, uu, xx, mism


# ---------------------------------------------------------------- cycle space
def cycle_assignments(k):
    K = 2 ** k
    out = []
    for a in range(K):
        for b in range(K):
            for d in range(K):
                out.append((a ^ b, a ^ d, b ^ d, a, b, d))
    return out


def edge_perm(sigma):
    m = {}
    for ei, (a, b) in enumerate(EDGES):
        pa, pb = sorted((sigma[a], sigma[b]))
        m[ei] = EDGES.index((pa, pb))
    return m


PERMS = [edge_perm(s) for s in itertools.permutations(range(4))]


def canon(c):
    best = None
    for m in PERMS:
        img = [0] * 6
        for ei in range(6):
            img[m[ei]] = c[ei]
        t = tuple(img)
        if best is None or t < best:
            best = t
    return best


def orbit_plan(k):
    """Orbits of valid assignments; choose members so that few dgemm keys (c13,c23,c34) needed."""
    orbits = {}
    for c in cycle_assignments(k):
        orbits.setdefault(canon(c), []).append(c)
    uncovered = set(orbits)
    plan = {}  # key -> list of (assignment, multiplicity)
    while uncovered:
        keycount = {}
        for o in uncovered:
            for c in orbits[o]:
                key = (c[1], c[3], c[5])
                keycount.setdefault(key, set()).add(o)
        key = max(sorted(keycount), key=lambda kk: len(keycount[kk]))
        for o in sorted(keycount[key]):
            c = next(cc for cc in orbits[o] if (cc[1], cc[3], cc[5]) == key)
            plan.setdefault(key, []).append((c, len(orbits[o])))
            uncovered.discard(o)
    return orbits, plan


# ---------------------------------------------------------------- exact K4 count mod p
def k4_mod_multi(F, key, assigns, p, batch=None):
    """For fixed (c13,c23,c34)=key, return {assignment: S mod p} for each assignment."""
    c13, c23, c34 = key
    n = F.shape[1]
    if batch is None:
        batch = 48 if n >= 96 else max(1, n // 3)
    assert n * (p - 1) ** 2 < 2 ** 53
    R = [np.mod(F[c], p).astype(np.float64) for c in range(F.shape[0])]
    X13, X23, X34 = R[c13], R[c23], R[c34]
    acc = {c: 0 for c, _ in assigns}
    pf = float(p)
    for s in range(0, n, batch):
        e = min(n, s + batch)
        B = e - s
        P = np.fmod(X13[s:e, None, :] * X23[None, :, :], pf)  # [b,u2,u3], < 2^42 before fmod
        G = np.fmod(P.reshape(B * n, n) @ X34, pf).reshape(B, n, n)  # [b,u2,u4]
        for c, _ in assigns:
            X12, X14, X24 = R[c[0]], R[c[2]], R[c[4]]
            T = np.fmod(G * X24[None, :, :], pf)
            T = np.fmod(T * X14[s:e, None, :], pf)
            v = np.fmod(T.sum(axis=2), pf)  # n terms < 2^21 -> < 2^31
            v = np.fmod(v * X12[s:e, :], pf)
            acc[c] = (acc[c] + int(v.sum())) % p
    return acc


def crt_signed(residues, primes):
    M = 1
    x = 0
    for r, p in zip(residues, primes):
        # x = r mod p, combine
        t = ((r - x) * pow(M, -1, p)) % p
        x += M * t
        M *= p
    if x > M // 2:
        x -= M
    return x, M


def exact_count(F, k, primes=PRIMES, log=None):
    """Return D = sum over all N^4 ordered tuples of prod W (numerator units), and details."""
    K = 2 ** k
    n = F.shape[1]
    orbits, plan = orbit_plan(k)
    fmax = [int(np.abs(F[c]).max()) for c in range(K)]
    M = 1
    for p in primes:
        M *= p
    per = {}
    total_bound = 0
    for key, assigns in plan.items():
        for c, mult in assigns:
            bnd = n ** 4
            for ei in range(6):
                bnd *= fmax[c[ei]]
            total_bound += bnd * mult
            assert 2 * bnd < M, "CRT modulus too small"
    # choose the fewest primes whose product exceeds 2*max bound (signed lift)
    maxb = max(n ** 4 * math.prod(fmax[c[e]] for e in range(6))
               for assigns in plan.values() for c, _ in assigns)
    use = []
    M = 1
    for p in primes:
        use.append(p)
        M *= p
        if M > 2 * maxb + 1:
            break
    assert M > 2 * maxb + 1, "CRT modulus too small"
    primes = use
    res = {}
    t0 = time.time()
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as td:
        fb = os.path.join(td, "F.bin")
        np.ascontiguousarray(F, dtype="<i8").tofile(fb)
        pl = os.path.join(td, "plan.txt")
        keys = list(plan.keys())
        with open(pl, "w") as fh:
            for key in keys:
                fh.write(f"{key[0]} {key[1]} {key[2]} {len(plan[key])}\n")
                for c, _ in plan[key]:
                    fh.write(" ".join(map(str, c)) + "\n")
        proc = subprocess.Popen([BIN, fb, str(n), str(K), pl] + [str(p) for p in primes],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        assert proc.returncode == 0, err
        if log:
            for line in err.strip().splitlines()[-3:]:
                log("  " + line)
        got = {}
        for line in out.splitlines():
            _, p, ki, ai, r = line.split()
            got[(int(p), int(ki), int(ai))] = int(r)
        for ki, key in enumerate(keys):
            for ai, (c, _) in enumerate(plan[key]):
                res[c] = [got[(p, ki, ai)] for p in primes]
    S = 0
    details = []
    for key, assigns in plan.items():
        for c, mult in assigns:
            val, _ = crt_signed(res[c], primes)
            S += mult * val
            details.append({"assignment": list(c), "orbit_size": mult, "S": str(val)})
    assert sum(len(v) for v in orbits.values()) == 2 ** (3 * k)
    assert S % (4 ** k) == 0
    return S // (4 ** k), {"orbits": len(orbits), "dgemm_keys": len(plan),
                           "primes": primes, "log2_crt_modulus": math.log2(M),
                           "log2_max_abs_bound": math.log2(maxb), "engine": "k4mix.cpp (Accelerate dgemm mod p)",
                           "log2_bound_per_assignment_max": max(
                               math.log2(max(1, n ** 4 * math.prod(fmax[c[e]] for e in range(6))))
                               for c in cycle_assignments(k)),
                           "assignments": details}


# ---------------------------------------------------------------- oracle
def brute_force(W):
    N = W.shape[0]
    Wl = W.tolist()
    tot = 0
    for a in range(N):
        ra = Wl[a]
        for b in range(N):
            wab = ra[b]
            rb = Wl[b]
            for c in range(N):
                w3 = wab * ra[c] * rb[c]
                if w3 == 0:
                    continue
                rc = Wl[c]
                s = 0
                for d in range(N):
                    s += ra[d] * rb[d] * rc[d]
                tot += w3 * s
    return tot


def random_structured(rng, n, k, Q, shuffle_masks=False):
    K = 2 ** k
    f = rng.integers(0, Q + 1, size=(K, n, n))
    f = np.triu(f) + np.transpose(np.triu(f, 1), (0, 2, 1))  # f_uv = f_vu
    N = n * K
    W = np.zeros((N, N), dtype=np.int64)
    for i in range(N):
        for j in range(N):
            u, x = divmod(i, K)
            v, y = divmod(j, K)
            W[i, j] = f[x ^ y, u, v]
    return W


def check_matrix(W, Q, log=None):
    basis, k = discover_group(W)
    k_, n, F, uu, xx, mism = fourier_blocks(W, basis)
    assert mism == 0, f"reconstruction mismatches: {mism}"
    D, det = exact_count(F, k, log=log)
    return D, k, basis, n, det


def run_oracle(seed=20260927):
    rng = np.random.default_rng(seed)
    cases = []
    specs = [(1, 1, 65536), (2, 1, 65536), (3, 1, 65536), (2, 2, 65536), (1, 3, 65536),
             (3, 2, 7), (4, 1, 65536), (2, 3, 65536), (5, 1, 1), (1, 2, 65536)]
    for (n, k, Q) in specs:
        W = random_structured(rng, n, k, Q)
        # relabel by an XOR-compatible scrambling of the fibre id bits? keep base labelling,
        # but also test complement
        for label, M in (("W", W), ("Q-W", Q - W)):
            D, kk, basis, nn, _ = check_matrix(M, Q)
            bf = brute_force(M)
            cases.append({"n": n, "k_built": k, "k_found": kk, "Q": Q, "matrix": label,
                          "N": int(M.shape[0]), "checker": str(D), "brute": str(bf),
                          "match": D == bf})
    # relabelled structured cases: random base-class permutation, random invertible linear
    # map on fibre coordinates, random per-fibre XOR offset (group still acts by XOR masks)
    for (n, k) in ((3, 2), (24, 1), (2, 3)):
        K = 2 ** k
        W0 = random_structured(rng, n, k, 65536)
        while True:
            L = [int(v) for v in rng.integers(1, K, size=k)] if k else []
            span = {0}
            for v in L:
                span = span | {s ^ v for s in span}
            if len(span) == K:
                break
        def lin(x):
            r = 0
            for j in range(k):
                if (x >> j) & 1:
                    r ^= L[j]
            return r
        bp = rng.permutation(n)
        off = rng.integers(0, K, size=n)
        lab = np.array([int(bp[i // K]) * K + (lin(i % K) ^ int(off[i // K])) for i in range(n * K)])
        W = np.zeros_like(W0)
        W[np.ix_(lab, lab)] = W0
        D, kk, basis, nn, _ = check_matrix(W, 65536)
        bf = brute_force(W)
        cases.append({"n": n, "k_built": k, "k_found": kk, "Q": 65536, "matrix": "relabelled",
                      "N": n * K, "checker": str(D), "brute": str(bf), "match": D == bf})
    # unstructured random symmetric matrices (k found should be 0 or small) incl. diagonal
    for N in (5, 7, 9):
        A = rng.integers(0, 65537, size=(N, N))
        A = np.triu(A) + np.triu(A, 1).T
        D, kk, basis, nn, _ = check_matrix(A, 65536)
        bf = brute_force(A)
        cases.append({"n": nn, "k_built": 0, "k_found": kk, "Q": 65536, "matrix": "W",
                      "N": N, "checker": str(D), "brute": str(bf), "match": D == bf})
    # deliberately broken invariance: structured then perturb one symmetric pair
    W = random_structured(rng, 3, 2, 65536)
    W[0, 5] = W[5, 0] = (W[0, 5] + 1) % 65537
    D, kk, basis, nn, _ = check_matrix(W, 65536)
    bf = brute_force(W)
    cases.append({"n": nn, "k_built": 2, "k_found": kk, "Q": 65536, "matrix": "perturbed",
                  "N": 12, "checker": str(D), "brute": str(bf), "match": D == bf,
                  "note": "perturbation must reduce discovered k"})
    ok = all(c["match"] for c in cases) and cases[-1]["k_found"] < 2
    return {"status": "passed" if ok else "FAILED", "cases": cases, "seed": seed}


# ---------------------------------------------------------------- main
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate")
    ap.add_argument("--expected-sha256")
    ap.add_argument("--out")
    ap.add_argument("--oracle-only", action="store_true")
    ap.add_argument("--part", choices=["both", "red", "blue"], default="both",
                    help="red/blue: compute one colour, save part-<colour>.json (for <10 min jobs);"
                         " the blue run merges when part-red.json exists")
    args = ap.parse_args()
    logs = []

    def log(m):
        line = f"[{time.strftime('%H:%M:%S', time.gmtime())}] {m}"
        print(line, flush=True)
        logs.append(line)

    t_start = time.time()
    t0 = time.time()
    oracle = run_oracle()
    t_oracle = time.time() - t0
    log(f"oracle {oracle['status']} ({len(oracle['cases'])} cases, {t_oracle:.1f}s)")
    if args.oracle_only:
        print(json.dumps(oracle, indent=1))
        return
    assert oracle["status"] == "passed"
    if args.part in ("both", "red"):
        assert not os.path.exists(args.out), "output dir exists"
    else:
        assert os.path.exists(os.path.join(args.out, "part-red.json"))
    sha = sha256(args.candidate)
    assert sha == args.expected_sha256, f"sha mismatch {sha}"
    os.makedirs(args.out, exist_ok=(args.part == "blue"))
    t0 = time.time()
    with open(args.candidate) as fh:
        cand = json.load(fh)
    assert cand["schema"] == "rational-step-graphon-v1"
    Q = int(cand["edge_probability_denominator"])
    W = np.array(cand["red_probability_numerators"], dtype=np.int64)
    wts = cand["block_weights"]
    N = W.shape[0]
    validation = {
        "square": W.shape == (N, N) and len(wts) == N,
        "uniform_weights": len(set(wts)) == 1,
        "symmetric": bool(np.array_equal(W, W.T)),
        "in_range_0_Q": bool(W.min() >= 0 and W.max() <= Q),
    }
    assert all(validation.values()), validation
    t_load = time.time() - t0
    log(f"loaded N={N} Q={Q} in {t_load:.1f}s; validation {validation}")

    t0 = time.time()
    basis, k = discover_group(W)
    t_disc = time.time() - t0
    log(f"discovered XOR group basis {basis} (k={k}) in {t_disc:.1f}s")
    t0 = time.time()
    _, n, F, uu, xx, mism = fourier_blocks(W, basis)
    _, n2, Fb, _, _, mismb = fourier_blocks(Q - W, basis)
    t_four = time.time() - t0
    log(f"n={n}; reconstruction mismatches red={mism} blue={mismb} ({t_four:.1f}s)")
    assert mism == 0 and mismb == 0
    nz = {c: int(np.count_nonzero(F[c])) for c in range(2 ** k)}
    log(f"nonzero entries per character block (red): {nz}")

    if args.part in ("both", "red"):
        t0 = time.time()
        red, det_r = exact_count(F, k, log=log)
        t_red = time.time() - t0
        log(f"red done {t_red:.1f}s")
        if args.part == "red":
            with open(os.path.join(args.out, "part-red.json"), "w") as fh:
                json.dump({"sha256": sha, "red": str(red), "method": det_r, "t_red": t_red,
                           "log": logs}, fh, indent=1)
            return
    else:
        with open(os.path.join(args.out, "part-red.json")) as fh:
            pr = json.load(fh)
        assert pr["sha256"] == sha
        red, det_r, t_red = int(pr["red"]), pr["method"], pr["t_red"]
        logs[:0] = pr["log"] + ["--- blue part (separate job) ---"]
    t0 = time.time()
    blue, det_b = exact_count(Fb, k, log=log)
    t_blue = time.time() - t0
    log(f"blue done {t_blue:.1f}s")
    total = red + blue
    denom = N ** 4 * Q ** 6
    dens = Fraction(total, denom)
    report = {
        "schema": "zk-fibre-character-audit-v1",
        "lane": "round5-F5",
        "status": "completed",
        "evidence": "independent_structured_Z2k_character_expansion_multiprime_crt_recount",
        "candidate": {"path": args.candidate, "sha256": sha, "N": N, "Q": Q},
        "validation": validation,
        "fibre_structure": {"xor_basis": basis, "k": k, "base_classes": n,
                            "reconstruction_mismatches_red": mism,
                            "reconstruction_mismatches_blue": mismb,
                            "entries_checked": N * N,
                            "nonzero_per_character_red": {str(c): v for c, v in nz.items()}},
        "exact": {"red": str(red), "blue": str(blue), "total": str(total),
                  "denominator": str(denom), "denominator_formula": "N^4 * Q^6",
                  "density_fraction": f"{dens.numerator}/{dens.denominator}",
                  "density_decimal_display": f"{float(dens):.18f}"},
        "method": {"red": {k_: v for k_, v in det_r.items()},
                   "blue": {k_: v for k_, v in det_b.items()}},
        "tiny_oracle": oracle,
        "timings_s": {"oracle": t_oracle, "load": t_load, "discover": t_disc,
                      "fourier_and_reconstruction": t_four, "red": t_red, "blue": t_blue,
                      "wall": time.time() - t_start},
        "log": logs,
        "trust_boundary": (
            "Native exact computation (Python ints + numpy/Accelerate float64 dgemm mod 8 primes "
            "< 2^21 with asserted < 2^53 intermediates, CRT). Reads only the candidate matrix; "
            "fibre group discovered by exhaustive XOR-mask invariance search; character "
            "decomposition verified entry by entry. The reduction D = 2^-2k sum_cycle S(c) is a "
            "derived identity tested against brute force on tiny cases, not a formal proof. S4 "
            "orbit reduction of assignments is used. Not Lean; no optimality/novelty claim."),
    }
    with open(os.path.join(args.out, "report.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    import shutil
    shutil.copy(__file__, os.path.join(args.out, "zk_checker_snapshot.py"))
    log(f"density {dens} = {float(dens):.18f}")


if __name__ == "__main__":
    main()
