"""Convert a .red file (m k n / red elements) from nrpa_cayley to rational-step-graphon-v1 JSON."""
import hashlib, json, sys
from fractions import Fraction
src, dst = sys.argv[1], sys.argv[2]
lines = open(src).read().split("\n")
m, k, n = map(int, lines[0].split())
K2 = 1 << k
red = set(int(t) for t in lines[1].split())
def sub(x, y):
    return (((x // K2) - (y // K2)) % m) * K2 + ((x % K2) ^ (y % K2))
mat = [[1 if sub(y, x) in red else 0 for y in range(n)] for x in range(n)]
assert all(mat[i][j] == mat[j][i] for i in range(n) for j in range(n)) and all(mat[i][i] == 0 for i in range(n))
d = {"schema": "rational-step-graphon-v1", "block_weights": [1] * n,
     "edge_probability_denominator": 1, "red_probability_numerators": mat}
s = json.dumps(d)
open(dst, "w").write(s)
print("sha256", hashlib.sha256(s.encode()).hexdigest())
