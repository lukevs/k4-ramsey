"""Round4-P: relate B192 symbols to PPSS 768 Cayley block densities (reads data only)."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rows = json.loads((ROOT / "data/published_cayley_768.json").read_text())["red_rows"]
fibers = json.loads((ROOT / "reports/pilot-algebraic-lift-001/quotient.json").read_text())["fibers"]
B = json.loads((ROOT / "reports/literature-two-parameter-001/graphon-candidate.json").read_text())["red_probability_numerators"]
n = len(fibers)
print("fibres consecutive quadruples:", fibers == [[4 * k + t for t in range(4)] for k in range(n)], fibers[:6], fibers[-2:])
D = [[sum(rows[u][v] == "1" for u in f for v in g) for g in fibers] for f in fibers]
sym = {0: "0", 65536: "F", 51064: "P", 35015: "H"}
joint = Counter((D[i][j], sym[B[i][j]]) for i in range(n) for j in range(n) if i < j)
print("unordered (red edges in 4x4 block /16, B192 symbol):", dict(joint))
# The P blocks that were complete (16/16) in PPSS: describe by local structure.
H = {i: j for i in range(n) for j in range(n) if B[i][j] == 35015}
promo = [(i, j) for i in range(n) for j in range(i + 1, n) if D[i][j] == 16 and B[i][j] == 51064]
feat = Counter()
for i, j in promo:
    feat[("i-j partners' block", D[H[i]][H[j]], sym[B[H[i]][H[j]]],
          "i~H[j]", D[i][H[j]], "j~H[i]", D[j][H[i]])] += 1
print("promoted complete->P blocks:", len(promo))
for k, v in feat.most_common(): print(v, k)
ctrl = Counter()
for i in range(n):
    for j in range(i + 1, n):
        if D[i][j] == 16 and B[i][j] == 65536:
            ctrl[(D[H[i]][H[j]], D[i][H[j]], D[j][H[i]])] += 1
print("remaining complete blocks (D[Hi][Hj], D[i][Hj], D[j][Hi]):", ctrl.most_common(8))
