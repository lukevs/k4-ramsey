"""check T12 (from B192) is isomorphic to types(3,2) Cayley design, by backtracking."""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import T12
from design import types
T2 = types(3, 2); n = 12
def bt(mp):
    k = len(mp)
    if k == n: return mp
    for c in range(n):
        if c in mp: continue
        if all(T12[k][i] == T2[c][mp[i]] for i in range(k)) and T12[k][k] == T2[c][c]:
            r = bt(mp + [c])
            if r: return r
    return None
print('block isomorphism T12 -> Z3xZ2xZ2 design:', bt([]))
