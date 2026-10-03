"""Round4-P independent check of lane E11's closed form for B192 (own code).
(1) Build the difference design T0 on Z3 x Z2 x Z2 from the verbal rule and find
    (by backtracking) a bijection to E11's 12x12 type matrix (rule.json).
(2) Using E11's vertex map (perm.json, data), check every entry of B192 against
    W((x,s),(y,t)) = g_{T[s,t]}(x xor y), C = {0,e1,e2,e3,e4,1111}, own g.
(3) Build B192' purely from the closed form in canonical coordinates and recount
    its exact density with the CRT checker (separately, by the caller)."""
import json, itertools, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
B = json.loads((ROOT/"reports/literature-two-parameter-001/graphon-candidate.json").read_text())["red_probability_numerators"]
R = json.loads((ROOT/"experiments/round4_E11/rule.json").read_text())["types"]
V = json.loads((ROOT/"experiments/round4_E11/perm.json").read_text())["vertex_of"]
Q, P, H = 65536, 51064, 35015
S = {1, 2, 4, 8, 15}
def g(ty, z):
    if z == 0: return {"Z": 0, "X": Q, "P": P, "H": H}[ty]
    if z in S: return {"Z": 0, "X": Q, "P": P, "H": Q}[ty]
    return {"Z": Q, "X": 0, "P": 0, "H": 0}[ty]
blocks = [(a, e, s) for a in range(3) for e in range(2) for s in range(2)]
def T0(u, v):
    da, de, ds = (u[0]-v[0]) % 3, u[1] ^ v[1], u[2] ^ v[2]
    if ds == 0:
        if da == 0: return "Z" if de == 0 else "H"
        return "X" if de == 0 else "Z"
    return "P" if da == 0 else "Z"
# (1) backtracking isomorphism rule.json T -> T0
def search(assign):
    k = len(assign)
    if k == 12: return list(assign)
    for c in range(12):
        if c in assign: continue
        if all(R[k][j] == T0(blocks[c], blocks[assign[j]]) for j in range(k)) and R[k][k] == T0(blocks[c], blocks[c]):
            r = search(assign + [c])
            if r: return r
    return None
iso = search([])
print("design isomorphism found:", iso is not None)
# (2) entrywise
bad = 0; seen = set()
for s in range(12):
    for x in range(16):
        u = V[f"{s},{x}"]; seen.add(u)
for s, t in itertools.product(range(12), repeat=2):
    for x in range(16):
        for y in range(16):
            u, v = V[f"{s},{x}"], V[f"{t},{y}"]
            if u != v and B[u][v] != g(R[s][t], x ^ y): bad += 1
print("vertex map bijective:", len(seen) == 192, " off-diagonal mismatches:", bad, "of", 192*191,
      " diagonal zero:", all(B[i][i] == 0 for i in range(192)))
# (3) canonical closed-form matrix
W = [[0 if (i == j) else g(T0(blocks[i // 16], blocks[j // 16]), (i % 16) ^ (j % 16)) for j in range(192)] for i in range(192)]
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=False)
(out / "b192-closed-form.json").write_text(json.dumps(dict(schema="rational-step-graphon-v1", block_weights=[1]*192,
    edge_probability_denominator=Q, red_probability_numerators=W)) + "\n")
print("degrees F/P/H:", sum(x == Q for x in W[0]), sum(x == P for x in W[0]), sum(x == H for x in W[0]))
