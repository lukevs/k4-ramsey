"""Step (4): fix a small XOR factor b (profile of a +-1 or fractional colouring) and optimise the
BIG factor sigma1 (n classes) against the bilinear objective (1/32) sum_S n_S b_S t_S(sigma1).
Product = n*k-class graphon. Baseline: b = trivial (plain c4 problem) at n and n*k classes."""
import sys, itertools, time, json, numpy as np, torch
torch.set_num_threads(1); torch.set_default_dtype(torch.float64)
sys.path.insert(0, 'research/experiments/round4_E6')
from sprofile import profile
MULT = torch.tensor([1., 3, 12, 3, 12, 1])

def tprof(w, s):
    d = s @ w; e = w @ d; A = s * w[None, :]; A2 = A @ A
    T = (A2 * A.T).sum(1)
    U = s[:, None, :] * s[None, :, :] * w[None, None, :]          # U[i,j,k]
    Q = torch.einsum('ijk,kl,ijl->ij', U, s, U)
    K = (w[:, None] * w[None, :] * s * Q).sum()
    return torch.stack([torch.ones(()), e * e, w @ (d * d), torch.trace(A2 @ A2), T @ d, K])

def optimise(b, n, iters, restarts, seed, free_w=True):
    g = torch.Generator().manual_seed(seed); best = (9, None)
    bt = torch.tensor(b)
    for r in range(restarts):
        X = (torch.randn(n, n, generator=g) * 3).requires_grad_(); th = torch.zeros(n, requires_grad=True)
        opt = torch.optim.LBFGS([X, th] if free_w else [X], lr=1, max_iter=iters, history_size=50,
                                tolerance_grad=1e-12, tolerance_change=1e-15, line_search_fn='strong_wolfe')
        def closure():
            opt.zero_grad(); s = torch.tanh((X + X.T) / 2); w = torch.softmax(th, 0)
            f = (MULT * bt * tprof(w, s)).sum() / 32; f.backward(); return f
        opt.step(closure); f = closure()
        if f.item() < best[0]:
            best = (f.item(), (torch.softmax(th, 0).detach().numpy(), torch.tanh((X + X.T) / 2).detach().numpy()))
    return best

if __name__ == '__main__':
    # bank of distinct +-1 small-factor profiles (uniform weights, k<=4) plus K3xK3-type (tensor of two triangle colourings)
    bank = {}
    for k in range(2, 5):
        iu = list(zip(*np.triu_indices(k)))
        for bits in itertools.product([1, -1], repeat=len(iu)):
            S = np.zeros((k, k))
            for (i, j), x in zip(iu, bits): S[i, j] = S[j, i] = x
            p = profile(np.ones(k) / k, S); key = tuple(np.round(p, 9))
            if abs(p[5]) > 0.2 and key not in bank: bank[key] = (k, p)   # need |b_K| sizable to be competitive
    print('bank size', len(bank), flush=True)
    n = int(sys.argv[1]); iters = int(sys.argv[2]); t0 = time.time(); rows = []
    base = optimise([1.] * 6, n, iters, int(sys.argv[4]), 0)[0]
    print(f'baseline trivial n={n}: {base:.10f}', flush=True)
    for key, (k, p) in sorted(bank.items(), key=lambda kv: -kv[1][1][5]):
        if time.time() - t0 > 480: break
        val = optimise(p.tolist(), n, iters, int(sys.argv[4]), 1)[0]
        rows.append(dict(k=k, b=p.tolist(), value=val))
        print(f'k={k} b={np.round(p,4).tolist()} product value {val:.10f} (delta vs base {val-base:+.3e})', flush=True)
    json.dump(dict(n=n, baseline=base, rows=rows), open(sys.argv[3], 'w'), indent=1)
