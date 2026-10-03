"""C1: B192 base in explicit coordinates (vertex (s,x), s block in [12], x in F2^4)."""
import sys, json, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'research/experiments/round4_E11'))
from family import build, f2, T12, F

def base(p, h):
    elems, sub, C = f2(4, [1, 2, 4, 8, 15])
    W = build(T12, elems, sub, C, p, h)
    # type matrix per entry and difference class
    n = 192; q = 16
    typ = np.empty((n, n), dtype='<U1'); cls = np.empty((n, n), dtype=int)
    for s in range(12):
        for t in range(12):
            typ[s*q:(s+1)*q, t*q:(t+1)*q] = T12[s][t] if s != t else 'D'
    D = np.array([[x ^ y for y in range(q)] for x in range(q)])
    cc = np.where(D == 0, 0, np.where(np.isin(D, [1, 2, 4, 8, 15]), 1, 2))
    cls = np.tile(cc, (12, 12))
    return W, typ, cls

def Fval(W):
    return F(W, [0], [len(W)])

def rootedK4e(U):
    # R[u,v] = sum_{c,d} U_uc U_vc U_ud U_vd U_cd
    X = U[:, None, :] * U[None, :, :]
    return np.einsum('uvc,cd,uvd->uv', X, U, X, optimize=True)
