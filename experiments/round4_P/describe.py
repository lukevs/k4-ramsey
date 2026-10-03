"""Round4-P structural description of d4763 (reads saved artifacts only).

Checks, entry by entry, that the 960-class candidate equals
    W[(i,a),(j,b)] = B'[i][j] + q_ij * kappa(a - b - g_ij)      (i != j, B' fractional, edge active)
    W[(i,a),(j,b)] = B'[i][j]                                   (otherwise)
with (i,a) -> 5*i + a, kappa(x) = 3 if x = +-1 mod 5 else -2, g_ji = -g_ij,
and reports the parameter counts of that description.
"""
import hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / "reports/association-scheme-per-edge-boundary-continuation-001"
BASE = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
PHASE = ROOT / "reports/association-scheme-phase-two-amplitude-001/phase-assignment.json"
R, Q = 5, 65536


def kappa(x):
    return 3 if x % R in (1, 4) else -2


def main():
    W = json.loads((C / "graphon-candidate.json").read_text())["red_probability_numerators"]
    B = json.loads(BASE.read_text())["red_probability_numerators"]
    phases = json.loads(PHASE.read_text())
    amps = json.loads((C / "per-edge-amplitudes.json").read_text())
    n = len(B)
    assert len(W) == R * n
    sym = Counter(x for r in B for x in r)
    # Recover B' (active h raised 35015 -> 35139) and check reconstruction.
    mism = 0
    active = Counter(); phase_hist = Counter(); amp_by_type = {"p": Counter(), "h": Counter()}
    for i in range(n):
        for j in range(n):
            base = B[i][j]
            if i != j and 0 < base < Q:
                e = f"{min(i,j)},{max(i,j)}"
                s = phases[e]
                typ = "p" if base == 51064 else "h"
                if s >= 0:
                    if typ == "h":
                        base = 35139
                    g = s if i < j else -s
                    q = amps.get(e, 0)
                    if i < j:
                        active[typ] += 1; phase_hist[(typ, s)] += 1; amp_by_type[typ][q] += 1
                else:
                    g, q = 0, 0
                    if i < j:
                        active[typ + "_inactive"] += 1
            else:
                g, q = 0, 0
            for a in range(R):
                for b in range(R):
                    if W[R*i+a][R*j+b] != base + q * kappa(a - b - g):
                        mism += 1
    # Degrees of the four-symbol base.
    deg = {v: Counter(sum(1 for x in r if x == v) for r in B) for v in sym}
    out = dict(
        candidate_sha256=hashlib.sha256((C / "graphon-candidate.json").read_bytes()).hexdigest(),
        base_order=n, lift=R, reconstruction_mismatches=mism,
        base_symbols={str(k): v for k, v in sym.items()},
        base_row_degree_by_symbol={str(k): dict(v) for k, v in deg.items()},
        fractional_pairs=active,
        phase_histogram={f"{t}:{s}": c for (t, s), c in sorted(phase_hist.items())},
        distinct_amplitudes={t: len(c) for t, c in amp_by_type.items()},
        amplitude_modal={t: c.most_common(3) for t, c in amp_by_type.items()},
        amplitude_nonmodal_edges={t: sum(c.values()) - c.most_common(1)[0][1] for t, c in amp_by_type.items()},
        distinct_matrix_values=len(set(x for r in W for x in r)),
        min_max=[min(x for r in W for x in r if x > 0), max(x for r in W for x in r if x < Q)],
    )
    print(json.dumps(out, indent=2, default=str))
    return out


if __name__ == "__main__":
    import sys
    res = main()
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(res, indent=2, default=str) + "\n")
