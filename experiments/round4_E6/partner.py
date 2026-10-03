"""Optimise a small fractional XOR partner W2 (k classes) against a fixed big factor profile.
Objective: mono(W1 xor W2) = (1/32) sum_S n_S a_S t_S(sigma2). Also enumerate +-1 partners."""
import sys, json, itertools, time, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, 'experiments/round4_E6')
from sprofile import profile, load, mono, mono_xor, MULT

def prof_small(w, s):
    return profile(w, s, k4=True)

def unpack(x, k):
    th = x[:k]; w = np.exp(th - th.max()); w /= w.sum()
    S = np.zeros((k, k)); iu = np.triu_indices(k)
    S[iu] = np.tanh(x[k:]); S = S + S.T - np.diag(np.diag(S))
    return w, S

def run(a, ks, starts, seed=0, tlimit=400):
    rng = np.random.default_rng(seed); best = (mono_xor(a, np.ones(6)), None)
    t0 = time.time(); results = {}
    for k in ks:
        bk = (9, None)
        for r in range(starts):
            if time.time() - t0 > tlimit: break
            x0 = np.concatenate([rng.normal(0, .5, k), rng.normal(0, 2, k * (k + 1) // 2)])
            f = lambda x: mono_xor(a, prof_small(*unpack(x, k)))
            res = minimize(f, x0, method='L-BFGS-B', options={'maxiter': 3000})
            if res.fun < bk[0]: bk = (res.fun, res.x)
        w, S = unpack(bk[1], k)
        results[k] = bk[0]
        print(f'k={k} best mono(xor)={bk[0]:.12f} weights={np.round(w,3).tolist()}', flush=True)
        print('  sigma2=', np.round(S, 3).tolist(), flush=True)
    return results

def enum_pm(a, kmax):
    out = {}
    for k in range(1, kmax + 1):
        iu = list(zip(*np.triu_indices(k))); best = 9
        w = np.ones(k) / k
        for bits in itertools.product([1, -1], repeat=len(iu)):
            S = np.zeros((k, k))
            for (i, j), b in zip(iu, bits): S[i, j] = S[j, i] = b
            v = mono_xor(a, prof_small(w, S)); best = min(best, v)
        out[k] = best; print(f'+-1 uniform k={k}: best {best:.12f}', flush=True)
    return out

if __name__ == '__main__':
    w, s = load(sys.argv[1]); a = profile(w, s)
    print('big profile', a.tolist(), 'mono', mono(a), flush=True)
    # sanity: xor with trivial == mono; bilinear check against explicit product on tiny random case
    rng = np.random.default_rng(1)
    w1 = rng.random(3); w1 /= w1.sum(); s1 = rng.uniform(-1, 1, (3, 3)); s1 = (s1 + s1.T) / 2
    w2 = rng.random(2); w2 /= w2.sum(); s2 = rng.uniform(-1, 1, (2, 2)); s2 = (s2 + s2.T) / 2
    direct = mono(profile(np.kron(w1, w2), np.kron(s1, s2)))
    print('bilinear check', direct, mono_xor(profile(w1, s1), profile(w2, s2)), flush=True)
    enum_pm(a, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    run(a, [2, 3, 4, 6, 8], starts=int(sys.argv[3]) if len(sys.argv) > 3 else 20)
