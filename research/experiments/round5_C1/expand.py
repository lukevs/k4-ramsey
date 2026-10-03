"""Exact moment expansion of Delta F for a latent lift D (dict (u,v)-> m x m array, D[(v,u)] = D[(u,v)].T)."""
import numpy as np
def expansion(W, D, m):
    n = len(W); Q = 1 - W
    fr = np.zeros((n, n), bool)
    for (u, v) in D: fr[u, v] = True
    nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
    T3 = T4 = T5 = T6 = 0.0
    for x in range(n):
        for y in nb[x]:
            Dxy = D[(x, y)]
            for z in nb[y]:
                Dxyz = Dxy @ D[(y, z)]
                if fr[z, x]:
                    c3 = (W[x]*W[y]*W[z] - Q[x]*Q[y]*Q[z]).sum()
                    T3 += c3 * np.trace(Dxyz @ D[(z, x)]) / m**3
                for w in nb[z]:
                    if fr[w, x]:
                        cf = W[x, z]*W[y, w] + Q[x, z]*Q[y, w]
                        T4 += cf * np.trace(Dxyz @ D[(z, w)] @ D[(w, x)]) / m**4
    for x in range(n):
        for y in nb[x]:
            cn = [z for z in nb[x] if fr[z, y]]
            Dxy = D[(x, y)]
            for z in cn:
                Mz = D[(x, z)] @ D[(z, y)]  # not used; diamond needs Hadamard
                Az = np.einsum('ik,jk->ijk', D[(x, z)], D[(y, z)])  # i=x latent, j=y latent, k=z latent
                sz = Az.sum(2)
                for w in cn:
                    sw = np.einsum('il,jl->ij', D[(x, w)], D[(y, w)])
                    T5 += (W[z, w] - Q[z, w]) * (Dxy * sz * sw).sum() / m**4
                    if z != w and fr[z, w]:
                        T6 += 2 * np.einsum('ij,ijk,il,jl,kl->', Dxy, Az, D[(x, w)], D[(y, w)], D[(z, w)]) / m**4
    return 4*T3/n**4, 3*T4/n**4, 6*T5/n**4, T6/n**4
