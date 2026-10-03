"""Round4-P second independent exact recount (pair-quadratic-form, multi-prime CRT).

Reads only a rational-step-graphon-v1 JSON with unit block weights.  Computes
    red  = sum over ordered (a,b,c,d) in [N]^4 of prod_{6 pairs} R_xy
    blue = same with Q - R_xy
exactly (as integers, via CRT over primes < 2^21), and density
    (red + blue) / (N^4 Q^6).
Repeated indices are included and use the diagonal entries R_aa.

Algorithmically independent of research/experiments/association_scheme/ordered_graphon_u256.cpp:
different decomposition (sum_ab M_ab x_ab^T M x_ab), modular arithmetic + CRT
instead of U256, BLAS dgemm (Accelerate) with an exactness bound, and a pure
Python brute-force oracle on tiny cases.
"""
import argparse, hashlib, itertools, json, os, random, shutil, subprocess, sys, time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "crt_pair_quadratic.cpp"


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def primes_below(limit, k):
    out, n = [], limit - 1
    while len(out) < k:
        if is_prime(n):
            out.append(n)
        n -= 1
    return out


def crt(residues, moduli):
    x, m = 0, 1
    for r, p in zip(residues, moduli):
        t = ((r - x) * pow(m, -1, p)) % p
        x, m = x + m * t, m * p
    return x, m


def brute(matrix, Q):
    n = len(matrix)
    red = blue = 0
    for v in itertools.product(range(n), repeat=4):
        pr = pb = 1
        for i, j in itertools.combinations(range(4), 2):
            x = matrix[v[i]][v[j]]
            pr *= x
            pb *= Q - x
        red += pr
        blue += pb
    return red, blue


def run_binary(binary, matrix, Q, primes):
    n = len(matrix)
    payload = f"{n} {Q} {len(primes)}\n" + " ".join(map(str, primes)) + "\n"
    payload += "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
    env = dict(os.environ, VECLIB_MAXIMUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    out = subprocess.run([str(binary)], input=payload, capture_output=True, text=True,
                         check=True, env=env).stdout.split("\n")
    rows = [list(map(int, line.split())) for line in out if line.strip()]
    assert [r[0] for r in rows] == primes
    red, m = crt([r[1] for r in rows], primes)
    blue, _ = crt([r[2] for r in rows], primes)
    return red, blue, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    started = time.monotonic()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    raw = Path(args.candidate).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == args.expected_sha256, sha
    (out / "candidate_snapshot.json").write_bytes(raw)
    shutil.copy2(SRC, out / "crt_pair_quadratic_snapshot.cpp")
    shutil.copy2(__file__, out / "driver_snapshot.py")
    binary = out / "crt_pair_quadratic"
    subprocess.run(["c++", "-O3", "-std=c++17", str(SRC), "-framework", "Accelerate",
                    "-o", str(binary)], check=True)

    cand = json.loads(raw)
    assert cand["schema"] == "rational-step-graphon-v1"
    M = cand["red_probability_numerators"]
    Q = cand["edge_probability_denominator"]
    N = len(M)
    assert cand["block_weights"] == [1] * N
    assert all(len(r) == N for r in M)
    assert all(M[i][j] == M[j][i] for i in range(N) for j in range(N))
    assert all(isinstance(x, int) and 0 <= x <= Q for r in M for x in r)
    assert Q <= 65536 and N <= 4096

    # Tiny oracle: arbitrary symmetric matrices, arbitrary diagonals, repeats.
    rng = random.Random(20260927)
    tiny = []
    small_primes = primes_below(1 << 21, 3)
    for n in range(1, 8):
        for rep in range(3):
            q = rng.choice([1, 2, 7, 65536])
            A = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1):
                    A[i][j] = A[j][i] = rng.randrange(q + 1)
            er, eb = brute(A, q)
            primes = small_primes if max(er, eb) < small_primes[0] ** 3 else primes_below(1 << 21, 7)
            r, b, m = run_binary(binary, A, q, primes)
            assert max(er, eb) < m
            ok = (r, b) == (er, eb)
            tiny.append(dict(n=n, q=q, primes=len(primes), red=er, blue=eb, ok=ok))
            assert ok, (n, q, r, b, er, eb)

    bound = N ** 4 * Q ** 6  # each of red, blue <= N^4 Q^6
    k = 1
    while True:
        primes = primes_below(1 << 21, k)
        m = 1
        for p in primes:
            m *= p
        if m > bound:
            break
        k += 1
    t0 = time.monotonic()
    red, blue, m = run_binary(binary, M, Q, primes)
    t1 = time.monotonic()
    assert red <= bound and blue <= bound and m > bound
    density = Fraction(red + blue, bound)
    report = dict(
        schema="round4-P-crt-pair-quadratic-audit-v1",
        status="completed",
        evidence="independent_generic_pair_quadratic_multiprime_crt_recount",
        candidate=dict(path=args.candidate, sha256=sha, order=N, denominator=Q,
                       unit_masses=True, symmetric=True, in_range=True),
        method="sum_{a,b} M_ab * x_ab^T M x_ab with x_ab = M_a o M_b; mod primes < 2^21 via "
               "Accelerate dgemm (exact: all partial sums integers < 2^53); CRT; "
               "red and blue (Q-M, including diagonal) counted separately",
        primes=primes, crt_modulus_bits=m.bit_length(), count_bound_bits=bound.bit_length(),
        tiny_literal_oracle=dict(status="passed", cases=len(tiny), detail=tiny),
        recount=dict(red=str(red), blue=str(blue), total=str(red + blue),
                     denominator=str(bound), density=str(density),
                     decimal_from_fraction=float(density)),
        seconds=dict(full_recount=t1 - t0, total=time.monotonic() - started),
        scope="Native exact computation (C++ + Accelerate BLAS + Python CRT). Not a Lean proof, "
              "not an optimality or novelty claim.",
    )
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "recount", "seconds", "primes")}, indent=2))


if __name__ == "__main__":
    main()
