"""Direct full-objective support derivative screen; no latent moment truncation.

Uniform graphon, ordered tuples with independent slots (including repeats).
For u != v, derivative when W_uv and W_vu move together is
12/n^4 [r^T W r - b^T (1-W) b], r_i=W_ui W_vi,
b_i=(1-W_ui)(1-W_vi). This is a finite-dimensional screen, not
a certificate for arbitrary infinitesimal graphon refinements.
"""
import os
for name in ("VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[name] = "1"
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time
import signal
import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def gradient(W, pairs, batch=128):
    ans = np.zeros(len(pairs))
    pairs = np.asarray(pairs, dtype=int)
    for sign, U in ((1, W), (-1, 1-W)):
        for start in range(0, len(pairs), batch):
            p = pairs[start:start+batch]
            V = U[p[:, 0]] * U[p[:, 1]]
            ans[start:start+batch] += sign*np.einsum('ij,ij->i', V @ U, V)
    return ans * (12.0/len(W)**4)


def brute_polynomial(N, Q, u, v):
    """Exact derivative of literal six-factor product on every ordered tuple."""
    n = len(N)
    total = 0
    for ids in itertools.product(range(n), repeat=4):
        edges = list(itertools.combinations(ids, 2))
        for color in (0, 1):
            factors = [int(N[a,b]) if color == 0 else Q-int(N[a,b]) for a,b in edges]
            for k, (a,b) in enumerate(edges):
                if {a,b} != {u,v}:
                    continue
                term = 1 if color == 0 else -1
                for j, f in enumerate(factors):
                    if j != k:
                        term *= f
                total += term
    return Fraction(total, n**4 * Q**5)


def validate():
    rng = np.random.default_rng(8921)
    errs = []
    for n in (2,3,4,5):
        for case in range(3):
            Q = 11
            N = rng.integers(Q+1, size=(n,n))
            N = np.triu(N)+np.triu(N,1).T
            pairs = list(itertools.combinations(range(n), 2))
            vals = gradient(N/Q, pairs)
            for (u,v), f in zip(pairs, vals):
                exact = brute_polynomial(N,Q,u,v)
                errs.append(abs(f-float(exact)))
    assert max(errs) < 2e-15, max(errs)
    return dict(cases=len(errs), max_abs_error=max(errs), oracle="literal integer product-rule enumeration, repeated indices and nonzero diagonals")


def exact_inward(N, Q, pair):
    """Integer CRT recount of the rooted-edge derivative at a red-solid edge."""
    n = len(N)
    bound = n*n*Q**5
    modulus, result = 1, 0
    primes = []
    p = 1000003
    while modulus <= 2*bound:
        while any(p%d == 0 for d in range(3,int(p**0.5)+1,2)):
            p += 2
        assert n*(p-1)**2 < 2**53
        residues = []
        for U in (N, Q-N):
            A = U % p
            v = (A[pair[0]]*A[pair[1]]) % p
            # Every dot-product partial sum is an integer below 2^53.
            y = np.rint(A.astype(float) @ v.astype(float)).astype(np.int64) % p
            residues.append(int(np.rint(v.astype(float) @ y.astype(float))) % p)
        residue = (residues[1]-residues[0]) % p
        result += modulus * ((residue-result)*pow(modulus,-1,p) % p)
        modulus *= p
        primes.append(p)
        p += 2
    if result > modulus//2:
        result -= modulus
    assert abs(result) <= bound
    f = Fraction(12*result,n**4*Q**5)
    return dict(value=str(f), decimal=float(f), primes=primes,
                method='integer CRT using exact-under-2^53 float64 dot products')


def load(path):
    d = json.loads(path.read_text())
    assert len(set(d['block_weights'])) == 1
    return np.asarray(d['red_probability_numerators'], dtype=np.int64), int(d['edge_probability_denominator'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--exhaust-cheap', action='store_true')
    args = parser.parse_args()
    signal.alarm(600)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    t0 = time.time()
    validation = validate()
    print('oracle', validation, flush=True)
    base_path = ROOT/'reports/literature-two-parameter-001/graphon-candidate.json'
    child_path = ROOT/'reports/round4-E5-depth2-001/graphon-candidate.json'
    B, QB = load(base_path)
    N, Q = load(child_path)
    W = N/Q
    nb = len(B); m = len(N)//nb
    assert m == 20
    blocks = N.reshape(nb,m,nb,m).transpose(0,2,1,3)
    mean = blocks.mean(axis=(2,3))/Q
    row_spread = float(np.max(np.ptp(blocks.sum(axis=3), axis=2))/(m*Q))
    # All coarse hard blocks must really remain constant.
    hard0, hard1 = B == 0, B == QB
    assert np.all(blocks[hard0] == 0) and np.all(blocks[hard1] == Q)
    mean_summary = dict(row_mean_spread=row_spread, levels=[])
    for val in sorted(set(B.ravel())-{0,QB}):
        z = mean[B == val]
        mean_summary['levels'].append(dict(base_numerator=int(val), minimum=float(z.min()), maximum=float(z.max()), distinct_means=len(np.unique(z))))
    print('coarse structure', mean_summary, flush=True)
    pairs0 = np.array(list(itertools.combinations(range(nb),2)))
    gb = gradient(B/QB, pairs0)
    levels = (B/QB)[pairs0[:,0],pairs0[:,1]]
    inward = gb*np.where(levels==0,1,-1)
    hard = (levels==0)|(levels==1)
    cheap = pairs0[hard & (inward<5e-8)]
    assert len(cheap)>0 and np.all(B[cheap[:,0],cheap[:,1]]==QB)
    rng = np.random.default_rng(664192)
    pairs = set()
    symmetry_verified = False
    if args.exhaust_cheap:
        ids = np.arange(len(N))
        for bit in (1,2):
            assert np.array_equal(N, N[np.ix_(ids^bit,ids^bit)])
        symmetry_verified = True
        for u,v in cheap:
            # Simultaneous XOR of the two binary labels moves x to 0 mod 4.
            for x in range(0,m,4):
                for y in range(m):
                    pairs.add((int(m*u+x),int(m*v+y)))
    # Each cheap coarse pair, with independently sampled latent endpoints.
    for u,v in ([] if args.exhaust_cheap else cheap):
        x,y = rng.integers(m,size=2)
        pairs.add((int(m*u+x),int(m*v+y)))
    # Exhaust all endpoint labels on root-0 cheap coarse pairs.
    for u,v in ([] if args.exhaust_cheap else cheap[cheap[:,0]==0]):
        for x in range(m):
            for y in range(m):
                pairs.add((int(m*u+x),int(m*v+y)))
    pairs = np.array(sorted(pairs))
    print('screening', len(pairs), 'fine pairs;', len(cheap), 'cheap coarse pairs', flush=True)
    g = gradient(W,pairs)
    slope = -g  # all tested entries equal one
    worst = int(np.argmin(slope))
    exact = exact_inward(N,Q,pairs[worst])
    assert abs(exact['decimal']-slope[worst]) < 1e-20
    np.savez(out/'derivatives.npz', pairs=pairs, gradients=g, base_pairs=cheap)
    report = dict(hypothesis='CB-WALL-001', validation=validation,
        candidate=str(child_path.relative_to(ROOT)), candidate_sha256=hashlib.sha256(child_path.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        n=len(N), Q=Q, seed=664192, numpy=np.__version__, coarse_means=mean_summary,
        tested_pairs=len(pairs), cheap_coarse_pairs=len(cheap), negative_inward_count=int((slope<0).sum()),
        exhaust_cheap=args.exhaust_cheap, xor_symmetry_verified=symmetry_verified,
        equivalent_fine_pairs=len(pairs)*(4 if symmetry_verified else 1),
        inward_derivative_min=float(slope.min()), inward_derivative_max=float(slope.max()),
        quantiles=np.quantile(slope,[0,.01,.1,.5,.9,.99,1]).tolist(),
        worst_pair=pairs[worst].tolist(), worst_coarse_pair=(pairs[worst]//m).tolist(),
        exact_worst_inward=exact,
        elapsed_seconds=time.time()-t0,
        evidence='float64 full-objective derivative screen; no claim for untested edges or arbitrary refinements')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'source_snapshot.py').write_text(Path(__file__).read_text())
    print(json.dumps(report,indent=2),flush=True)


if __name__ == '__main__':
    main()
