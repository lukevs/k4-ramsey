"""Round4-P independent audit for vertex-transitive step graphons.

1. Reads the candidate (SHA-checked) and a list of permutations of [N]
   (generator images, supplied as data by anyone; trusted only after checks).
2. Verifies each permutation s satisfies M[s(i)][s(j)] == M[i][j] for all i, j
   (red numerators; blue follows), and that the generated group is transitive
   (orbit of 0 under the generators is all of [N]).
3. Then the ordered count satisfies total = N * rooted(0), where rooted(r) =
   sum over (b,c,d) in [N]^3 of the six-edge product with first index r.
   rooted(r) is computed exactly mod seven primes < 2^21 (Accelerate dgemm,
   exact: partial sums < N * 2^37 < 2^53 for N <= 4096) and CRT; extra roots
   are computed and must agree (a consistency check implied by 2).
Tiny oracle: circulant (transitive) matrices vs brute force, and
sum-over-all-roots vs brute force on arbitrary symmetric matrices.
"""
import argparse, hashlib, itertools, json, operator, os, random, shutil, subprocess, time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "crt_rooted.cpp"


def primes_below(limit, k):
    out, n = [], limit - 1
    while len(out) < k:
        if all(n % d for d in range(2, int(n ** .5) + 1)):
            out.append(n)
        n -= 1
    return out


def crt(rs, ps):
    x, m = 0, 1
    for r, p in zip(rs, ps):
        t = ((r - x) * pow(m, -1, p)) % p
        x, m = x + m * t, m * p
    return x, m


def brute(A, Q):
    n = len(A); red = blue = 0
    for v in itertools.product(range(n), repeat=4):
        pr = pb = 1
        for i, j in itertools.combinations(range(4), 2):
            x = A[v[i]][v[j]]; pr *= x; pb *= Q - x
        red += pr; blue += pb
    return red, blue


def rooted(binary, M, Q, primes, roots):
    n = len(M)
    payload = f"{n} {Q} {len(primes)} {len(roots)}\n" + " ".join(map(str, roots)) + "\n"
    payload += " ".join(map(str, primes)) + "\n" + "\n".join(" ".join(map(str, r)) for r in M) + "\n"
    env = dict(os.environ, VECLIB_MAXIMUM_THREADS="1")
    lines = subprocess.run([str(binary)], input=payload, capture_output=True, text=True,
                           check=True, env=env).stdout.split("\n")
    rows = [list(map(int, l.split())) for l in lines if l.strip()]
    res = {}
    for r in roots:
        rr = [x for x in rows if x[0] == r]
        assert [x[1] for x in rr] == primes
        red, m = crt([x[2] for x in rr], primes)
        blue, _ = crt([x[3] for x in rr], primes)
        res[r] = (red, blue, m)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--generators", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--extra-roots", type=int, nargs="*", default=[])
    a = ap.parse_args()
    t_start = time.monotonic()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    assert not (out / "report.json").exists()
    raw = Path(a.candidate).read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    assert sha == a.expected_sha256, sha
    shutil.copy2(SRC, out / "crt_rooted_snapshot.cpp"); shutil.copy2(__file__, out / "driver_snapshot.py")
    binary = out / "crt_rooted"
    subprocess.run(["c++", "-O3", "-std=c++17", str(SRC), "-framework", "Accelerate", "-o", str(binary)],
                   check=True, capture_output=True)
    cand = json.loads(raw); M = cand["red_probability_numerators"]; Q = cand["edge_probability_denominator"]
    N = len(M)
    assert cand["schema"] == "rational-step-graphon-v1" and cand["block_weights"] == [1] * N
    assert all(len(r) == N for r in M) and Q <= 65536 and N <= 4096
    assert all(isinstance(x, int) and 0 <= x <= Q for r in M for x in r)
    cols = list(zip(*M)); assert all(tuple(M[i]) == cols[i] for i in range(N)); del cols
    t_valid = time.monotonic()

    gens_raw = Path(a.generators).read_bytes()
    gens = json.loads(gens_raw)["generators"]
    inv_checks = []
    for s in gens:
        assert sorted(s) == list(range(N))
        get = operator.itemgetter(*s)
        ok = all(get(M[s[i]]) == tuple(M[i]) for i in range(N))
        inv_checks.append(ok); assert ok
    seen = {0}; frontier = [0]
    while frontier:
        nxt = []
        for v in frontier:
            for s in gens:
                w = s[v]
                if w not in seen:
                    seen.add(w); nxt.append(w)
        frontier = nxt
    transitive = len(seen) == N; assert transitive
    t_group = time.monotonic()

    rng = random.Random(927)
    small = primes_below(1 << 21, 7); tiny = []
    for n in range(1, 8):
        for rep in range(2):
            q = rng.choice([1, 7, 65536])
            c = [rng.randrange(q + 1) for _ in range(n)]
            for d in range(n): c[d] = c[(-d) % n] if d > n - d else c[d]
            C = [[c[min((j - i) % n, (i - j) % n)] for j in range(n)] for i in range(n)]
            er, eb = brute(C, q); res = rooted(binary, C, q, small, [0])
            ok = (n * res[0][0], n * res[0][1]) == (er, eb); tiny.append(dict(kind="circulant", n=n, q=q, ok=ok)); assert ok
            A = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1): A[i][j] = A[j][i] = rng.randrange(q + 1)
            er, eb = brute(A, q); res = rooted(binary, A, q, small, list(range(n)))
            ok = (sum(v[0] for v in res.values()), sum(v[1] for v in res.values())) == (er, eb)
            tiny.append(dict(kind="all-roots-arbitrary", n=n, q=q, ok=ok)); assert ok
    t_tiny = time.monotonic()

    bound = N ** 4 * Q ** 6
    primes = small; m = 1
    for p in primes: m *= p
    assert m > bound
    roots = [0] + [r for r in a.extra_roots if r != 0]
    res = rooted(binary, M, Q, primes, roots)
    t_count = time.monotonic()
    assert len({(v[0], v[1]) for v in res.values()}) == 1
    red, blue = N * res[0][0], N * res[0][1]
    assert red <= bound and blue <= bound
    dens = Fraction(red + blue, bound)
    rep = dict(
        schema="round4-P-transitive-rooted-crt-audit-v1", status="completed",
        evidence="independent_group_verified_rooted_multiprime_crt_recount",
        candidate=dict(path=a.candidate, sha256=sha, order=N, denominator=Q, unit_masses=True, symmetric=True, in_range=True),
        group=dict(generators_file=a.generators, generators_sha256=hashlib.sha256(gens_raw).hexdigest(),
                   generator_count=len(gens), entrywise_invariance=inv_checks, transitive=transitive,
                   note="generator images produced by E4 code as data; invariance and transitivity verified here"),
        tiny_oracle=dict(status="passed", cases=len(tiny), detail=tiny),
        roots=roots, rooted_counts={str(r): [str(v[0]), str(v[1])] for r, v in res.items()},
        primes=primes, crt_modulus_bits=m.bit_length(), count_bound_bits=bound.bit_length(),
        recount=dict(red=str(red), blue=str(blue), total=str(red + blue), denominator=str(bound),
                     density=str(dens), decimal_from_fraction=float(dens)),
        seconds=dict(validate=t_valid - t_start, group=t_group - t_valid, tiny=t_tiny - t_group,
                     rooted_count=t_count - t_tiny, total=time.monotonic() - t_start),
        scope="Exact under (verified) vertex-transitivity: total = N * rooted(0). Native C++/Accelerate/Python. "
              "Not a full O(N^4) recount, not Lean, no optimality or novelty claim.")
    (out / "report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({k: rep[k] for k in ("status", "recount", "seconds", "roots")}, indent=2))


if __name__ == "__main__":
    main()
