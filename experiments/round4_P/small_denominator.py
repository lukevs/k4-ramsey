"""Round4-P: smallest-denominator (p, h) for the four-symbol 192-class base B192.

Uses the exact two-variable profile polynomial stored in
reports/literature-two-parameter-001/report.json (search-side object; every
retained candidate is recounted independently afterwards).  For each
denominator d <= DMAX, exhaustively minimises over integer 0 <= p, h <= d.
Writes rational-step-graphon-v1 candidates for selected (p, h, d).
"""
import json, sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "reports/literature-two-parameter-001"
DMAX = 64
PPSS = Fraction(4551721, 150994944)
MCKAY = Fraction(10486266368, 768 ** 4)
ANNOUNCE = Fraction(30139, 10 ** 6)


def value(profile, n, d, p, h):
    tot = 0
    for color, ep, eh, c in profile:
        a, b = (p, h) if color == 0 else (d - p, d - h)
        tot += c * a ** ep * b ** eh * d ** (6 - ep - eh)
    return Fraction(tot, d ** 6 * n ** 4)


def main(out_dir):
    rep = json.loads((PARENT / "report.json").read_text())
    profile = rep["profile"]
    B = json.loads((PARENT / "graphon-candidate.json").read_text())["red_probability_numerators"]
    n = len(B)
    assert value(profile, n, 65536, 51064, 35015) == Fraction(rep["density"])
    rows = []
    for d in range(1, DMAX + 1):
        best = min((value(profile, n, d, p, h), p, h) for p in range(d + 1) for h in range(d + 1))
        v, p, h = best
        rows.append(dict(d=d, p=p, h=h, density=str(v), decimal=float(v),
                         beats_ppss=v < PPSS, beats_mckay=v < MCKAY, below_0_030139=v < ANNOUNCE))
    first = next(r for r in rows if r["below_0_030139"])
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=False)
    for r in rows:
        if r is first or r["d"] in (4, 8, 16, 32, 41, 64):
            d, p, h = r["d"], r["p"], r["h"]
            M = [[0 if x == 0 else d if x == 65536 else p if x == 51064 else h for x in row] for row in B]
            assert all(x in (0, 65536, 51064, 35015) for row in B for x in row)
            (out / f"b192-d{d}-p{p}-h{h}.json").write_text(json.dumps(dict(
                schema="rational-step-graphon-v1", block_weights=[1] * n,
                edge_probability_denominator=d, red_probability_numerators=M)) + "\n")
    (out / "table.json").write_text(json.dumps(dict(
        note="profile-polynomial predictions (search side); recount independently",
        ppss=float(PPSS), mckay=float(MCKAY), rows=rows, first_below_0_030139=first), indent=1) + "\n")
    for r in rows:
        print(r["d"], r["p"], r["h"], r["decimal"], r["beats_mckay"], r["below_0_030139"])


if __name__ == "__main__":
    main(sys.argv[1])
