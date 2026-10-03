"""Signed even-subgraph profile of a step graphon (H-R4-E6).

mono(W) = (1/32) sum_{S subset E(K4), |S| even} t(S, sigma), sigma = 1-2W.
Up to isomorphism: empty(1), matching(3)=e^2, cherry(12), C4(3), paw(12), K4(1).
XOR product (independent colours): sigma = sigma1 (x) sigma2, so t(S) multiplies:
mono(W1 xor W2) = (1/32) sum_S n_S t_S(1) t_S(2).
"""
import json, sys, time, numpy as np
MULT = np.array([1, 3, 12, 3, 12, 1], float)

def load(path):
    d = json.load(open(path))
    w = np.array(d['block_weights'], float); w /= w.sum()
    P = np.array(d['red_probability_numerators'], float) / d['edge_probability_denominator']
    return w, 1 - 2 * P

def profile(w, s, k4=True):
    e = w @ s @ w
    d = s @ w                      # degree-like
    cherry = w @ (d * d)
    A = s * w[None, :]             # A = sigma D
    A2 = A @ A
    c4 = np.trace(A2 @ A2)
    # paw: triangle a,b,c plus pendant d at a: sum_a w_a T_a d_a, T_a = sum_bc w_b w_c s_ab s_bc s_ca
    T = np.einsum('ab,ba->a', A2, A)   # (A^3)_aa
    paw = T @ d   # (A^3)_aa already carries w_a
    K = np.nan
    if k4:
        K = 0.0
        for i in range(len(w)):
            U = s[i][None, :] * s * w[None, :]    # U_jk = s_ik s_jk w_k
            Q = ((U @ s) * U).sum(1)              # sum_kl U_jk s_kl U_jl
            K += w[i] * (w * s[i] * Q).sum()
    return np.array([1.0, e * e, cherry, c4, paw, K])

def mono(prof):
    return (MULT * prof).sum() / 32

def mono_xor(p1, p2):
    return (MULT * p1 * p2).sum() / 32

if __name__ == '__main__':
    w, s = load(sys.argv[1])
    t = time.time(); p = profile(w, s, k4=len(sys.argv) < 3)
    print('profile', p.tolist(), 'mono', mono(p), 'time', time.time() - t)
