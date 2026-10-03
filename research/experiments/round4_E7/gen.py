"""E7 group generator: additive group of F_{p^m} (or Z_p) with orbits under a
multiplicative subgroup H <= F^* (optionally extended by Frobenius), closed
under negation. Writes binary file: n, K, orbit[n] (int32), table D[x][y]=y-x
(int16/int32), plus JSON metadata.

usage: gen.py p m h frob out_prefix
"""
import sys, json, itertools
import numpy as np

def find_irreducible(p, m):
    # monic poly coeffs c0..c_{m-1} (x^m + ...), test irreducibility by brute root/factor check
    if m == 1:
        return []
    for coeffs in itertools.product(range(p), repeat=m):
        if coeffs[0] == 0:
            continue
        f = list(coeffs) + [1]
        if is_irreducible(f, p):
            return list(coeffs)
    raise RuntimeError

def polymod(a, f, p):
    a = a[:]
    while len(a) >= len(f):
        c = a[-1] % p
        if c:
            sh = len(a) - len(f)
            for i in range(len(f)):
                a[sh + i] = (a[sh + i] - c * f[i]) % p
        a.pop()
    return a

def polymul(a, b, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] = (r[i + j] + x * y) % p
    return r

def is_irreducible(f, p):
    m = len(f) - 1
    # brute force: no factor of degree <= m//2 (small cases)
    for d in range(1, m // 2 + 1):
        for coeffs in itertools.product(range(p), repeat=d):
            g = list(coeffs) + [1]
            # division remainder
            if not any(polymod(f, g, p)):
                return False
    return True

def main():
    p, m, h, frob = map(int, sys.argv[1:5])
    out = sys.argv[5]
    r = int(sys.argv[6]) if len(sys.argv) > 6 else 1  # extra cyclic factor Z_r
    n = p ** m
    f = find_irreducible(p, m)
    fpoly = f + [1]
    def enc(v):
        return sum(int(v[i]) * p ** i for i in range(m))
    def dec(x):
        return [(x // p ** i) % p for i in range(m)]
    def mul(x, y):
        if m == 1:
            return (x * y) % p
        r = polymod(polymul(dec(x), dec(y), p), fpoly, p) if m > 1 else None
        r = r + [0] * (m - len(r))
        return enc(r)
    # primitive element
    order = n - 1
    fac = [q for q in range(2, order + 1) if order % q == 0 and all(q % r for r in range(2, int(q ** .5) + 1))]
    def power(x, e):
        r = 1
        while e:
            if e & 1:
                r = mul(r, x)
            x = mul(x, x)
            e >>= 1
        return r
    g = None
    for cand in range(2, n):
        if all(power(cand, order // q) != 1 for q in fac):
            g = cand
            break
    if g is None and n == 2:
        g = 1
    assert order % h == 0
    gen_h = power(g, order // h)
    # multiplication-by-gen_h permutation
    perms = [[mul(gen_h, x) for x in range(n)]]
    neg = [enc([(-c) % p for c in dec(x)]) for x in range(n)]
    perms.append(neg)
    if frob:
        perms.append([power(x, p ** frob) if x else 0 for x in range(n)])
    nf = n
    if r > 1:
        lifted = [[P[x // r] * r + (x % r) for x in range(nf * r)] for P in perms]
        lifted.append([(x // r) * r + ((-(x % r)) % r) for x in range(nf * r)])
        perms = lifted
        n = nf * r
    # union-find
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for P in perms:
        for x in range(n):
            a, b = find(x), find(P[x])
            if a != b:
                parent[max(a, b)] = min(a, b)
    roots = sorted(set(find(x) for x in range(n)))
    rid = {r: i for i, r in enumerate(roots)}
    orbit = np.array([rid[find(x)] for x in range(n)], dtype=np.int32)
    assert orbit[0] == 0 and (orbit == 0).sum() == 1
    K = len(roots)
    # D[x][y] = y - x
    V = np.array([dec(x // r) for x in range(n)], dtype=np.int64)  # n x m
    T = np.array([x % r for x in range(n)], dtype=np.int64)
    pw = np.array([p ** i for i in range(m)], dtype=np.int64)
    D = np.zeros((n, n), dtype=np.int32)
    for x in range(n):
        D[x] = ((((V - V[x]) % p) @ pw) * r + (T - T[x]) % r).astype(np.int32)
    with open(out + ".bin", "wb") as fh:
        np.array([n, K], dtype=np.int32).tofile(fh)
        orbit.tofile(fh)
        D.tofile(fh)
    sizes = np.bincount(orbit).tolist()
    json.dump({"r": r, "p": p, "m": m, "h": h, "frob": frob, "n": n, "K": K, "irreducible_low_coeffs": f,
               "primitive": g, "orbit_sizes": sizes}, open(out + ".json", "w"))
    print(f"n={n} K={K} sizes={sorted(set(sizes))}")

main()
