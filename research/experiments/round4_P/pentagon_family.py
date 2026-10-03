"""Round4-P: three-parameter twisted-pentagon lift of B192 (search side).

C(Q; p0, x, y): fine classes (i, a), i in B192, a in Z5, index 5i + a.
  - B192 zero / full / diagonal blocks: 0 / Q / 0 (unchanged);
  - inactive p-edge {i,j} (phase table -1): p0 everywhere;
  - active p-edge with phase g (i<j; -g for i>j): x if a-b-g = +-1 mod 5 else Q;
  - h-edge (all active, phase 1): 0 if a-b-g = +-1 mod 5 else y.
b93 (reports/joint-coarse-boundary-face-001) is C(65536; 51064, 29356, 58565).
Search-side evaluation uses the Z5-strided CRT evaluator; retained candidates
are recounted by the generic checkers.
"""
import hashlib, json, os, subprocess, sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
PHASE = ROOT / "reports/association-scheme-phase-two-amplitude-001/phase-assignment.json"
BIN = Path(os.environ.get("CRT_EVAL_BIN", "crt_eval_strided"))
R = 5


def build(Q, p0, x, y):
    B = json.loads(BASE.read_text())["red_probability_numerators"]
    ph = json.loads(PHASE.read_text())
    n = len(B)
    W = [[0] * (R * n) for _ in range(R * n)]
    for i in range(n):
        for j in range(n):
            v = B[i][j]
            for a in range(R):
                for b in range(R):
                    if v == 0 or i == j:
                        e = 0
                    elif v == 65536:
                        e = Q
                    else:
                        s = ph[f"{min(i,j)},{max(i,j)}"]
                        g = s if i < j else -s
                        on = (a - b - g) % R in (1, 4)
                        if v == 51064:
                            e = p0 if s < 0 else (x if on else Q)
                        else:
                            assert v == 35015 and s >= 0
                            e = 0 if on else y
                    W[R * i + a][R * j + b] = e
    return W


def evaluate(W, Q):
    N = len(W)
    for i in range(N):  # verify Z5 shift invariance before using the stride
        for j in range(N):
            assert W[i][j] == W[j][i]
            assert W[i][j] == W[(i // R) * R + (i + 1) % R][(j // R) * R + (j + 1) % R]
    primes, n = [], (1 << 21) - 1
    bound = N ** 4 * Q ** 6
    m = 1
    while m <= bound:
        if all(n % d for d in range(2, int(n ** .5) + 1)):
            primes.append(n); m *= n
        n -= 1
    payload = f"{N} {Q} {len(primes)} {R}\n" + " ".join(map(str, primes)) + "\n"
    payload += "\n".join(" ".join(map(str, r)) for r in W) + "\n"
    env = dict(os.environ, VECLIB_MAXIMUM_THREADS="1")
    rows = [list(map(int, l.split())) for l in subprocess.run(
        [str(BIN)], input=payload, capture_output=True, text=True, check=True, env=env).stdout.split("\n") if l.strip()]
    def crt(rs):
        x, mm = 0, 1
        for r, p in zip(rs, primes):
            t = ((r - x) * pow(mm, -1, p)) % p; x, mm = x + mm * t, mm * p
        return x
    tot = R * (crt([r[1] for r in rows]) + crt([r[2] for r in rows]))
    return Fraction(tot, bound)


def write(W, Q, path):
    path.write_text(json.dumps(dict(schema="rational-step-graphon-v1", block_weights=[1] * len(W),
                                    edge_probability_denominator=Q, red_probability_numerators=W)) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    Q, p0, x, y = map(int, sys.argv[2:6])
    W = build(Q, p0, x, y)
    v = evaluate(W, Q)
    rec = dict(Q=Q, p0=p0, x=x, y=y, density=str(v), decimal=float(v))
    if len(sys.argv) > 6:
        rec["sha256"] = write(W, Q, out / f"pent-Q{Q}-{p0}-{x}-{y}.json")
    with open(out / "evaluations.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))
