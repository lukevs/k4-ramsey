"""Rational feasible old-level moment vector, proving strict strengthening."""
import json
from pathlib import Path
import cvxpy as cp
import numpy as np

folder = Path("reports/global-coupled-pilot-003")
cert = json.loads((folder/"full-certificate.json").read_text())
meta = json.loads((folder/"coefficient-metadata.json").read_text())
y = cp.Variable(len(cert["objective_numerators"]))
margin = cp.Variable()
c = np.array(cert["objective_numerators"])/720
constraints = [cp.sum(y)==1, y>=margin, c@y<=0.0282]
for block in cert["blocks"][:len(meta["base"])]:
    C = np.array(block["C_integer"])/720
    d = C.shape[1]
    M = cp.reshape(C.reshape(len(C),d*d).T@y,(d,d),order="C")
    constraints.append(M-margin*np.eye(d) >> 0)
problem = cp.Problem(cp.Maximize(margin),constraints)
problem.solve(solver="CLARABEL",tol_gap_abs=1e-10,tol_feas=1e-10,max_iter=150,time_limit=120)
assert y.value is not None and margin.value>1e-9
scale = 10**12
integer = np.rint(y.value*scale).astype(np.int64)
integer[int(np.argmax(integer))] += scale-int(integer.sum())
assert min(integer)>0
out = {"denominator":scale,"probability_numerators":integer.tolist(),
       "numerical_margin":float(margin.value),"solver_status":problem.status,
       "claim":"Feasible for N5 plus nonnegative N6 extension; not a graphon witness."}
(folder/"baseline-feasible-witness.json").write_text(json.dumps(out,indent=2)+"\n")
print({k:v for k,v in out.items() if k!="probability_numerators"})
