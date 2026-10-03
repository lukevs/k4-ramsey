"""F4 task 2 (float exploration, search-side): reduced Newton on the 23 free orbital params of E4-3840,
float gradient signs on bound params, FD Hessian eigenvalues. Saves x_newton.npy and setup cache."""
import json, sys, time, os
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; HERE = Path(__file__).parent
sys.path.insert(0, str(ROOT/'experiments/round4_E4'))
from coset_action import Base, CosetAction, density_grad_fast, orbit_reps
T0 = time.time()
rep = json.load(open(ROOT/'reports/round4-E4-exact-3840-001/exact-report.json'))
b = Base(); A = CosetAction(b, rep['K']).build(); A.verify_invariance()
reps, cnt = orbit_reps(A); rep_pid = A.pid[np.arange(A.norb)]
assert A.npar == 456
num = np.array(rep['param_numerators']); x0 = num / 65536
np.savez(HERE/'setup3840.npz', P=A.P.astype(np.int16), reps=reps, cnt=cnt, rep_pid=rep_pid, sizes=A.sizes, num=num)
print('built', A.n, A.norb, time.time()-T0, flush=True)
fun = lambda x: density_grad_fast(x[A.P], reps, cnt, rep_pid, A.npar)
f0, g0 = fun(x0); print('f(stored)=%.17g' % f0, 'exact', rep['exact_decimal'])
free = np.where((num > 0) & (num < 65536))[0]; print('free', len(free))
x = x0.copy()
def hess(x, tau=1e-5):
    Hm = np.zeros((len(free), len(free)))
    for jj, j in enumerate(free):
        xp = x.copy(); xp[j] += tau; xm = x.copy(); xm[j] -= tau
        Hm[:, jj] = (fun(xp)[1][free] - fun(xm)[1][free]) / (2*tau)
    return (Hm + Hm.T) / 2
for it in range(4):
    f, g = fun(x); Hm = hess(x)
    step = np.linalg.solve(Hm, g[free]); x[free] -= step
    print(it, '%.17g' % f, 'max|g_free|', abs(g[free]).max(), 'step', abs(step).max(), time.time()-T0, flush=True)
f, g = fun(x); Hm = hess(x)
ev = np.linalg.eigvalsh(Hm)
print('final f %.17g  max|g_free| %.3e' % (f, abs(g[free]).max()))
print('Hessian eigenvalues', ev)
bound = np.setdiff1d(np.arange(456), free)
at0 = bound[num[bound] == 0]; at1 = bound[num[bound] == 65536]
print('bound at0', len(at0), 'min g', g[at0].min(), ' at1', len(at1), 'max g', g[at1].max())
print('sizes free', A.sizes[free], 'max size', A.sizes.max())
np.save(HERE/'x_newton.npy', x); np.save(HERE/'free.npy', free)
