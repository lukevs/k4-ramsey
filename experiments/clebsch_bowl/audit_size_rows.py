"""Rebuild every coarse-size result and recount with independent all-root code."""
import os
for k in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'): os.environ[k]='1'
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from audit_weighted import density, selfcheck

source=Path(sys.argv[1]); dest=Path(sys.argv[2]); rows=json.loads(source.read_text())
audits=[]; C={0,1,2,4,8,15}
for row in rows:
    k=row['k']; T=row['types']; p,h=row['x'][-2:]; mass=np.asarray(row['x'][:-2])
    W=np.empty((16*k,16*k))
    for a in range(16*k):
        for b in range(16*k):
            relation=T[a//16][b//16]; diff=(a%16)^(b%16)
            if relation==0: value=float(diff not in C)
            elif relation==1: value=float(diff in C)
            elif relation==2: value=p if diff in C else 0.
            elif relation==3: value=h if diff==0 else float(diff in C)
            else: raise ValueError(relation)
            W[a,b]=value
    value=density(W,np.repeat(mass/16,16))
    error=value-row['F']
    assert abs(error)<3e-13,(row['name'],value,row['F'])
    audits.append(dict(name=row['name'],k=k,free=row['free'],density=value,
                       search_value=row['F'],difference=error,active_copies_above_1e_6=int((mass>1e-6).sum())))
result=dict(source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),validation=selfcheck(),
            runs=audits,max_abs_difference=max(abs(r['difference']) for r in audits),
            evidence='Independent matrix reconstruction and all-root weighted float64 recount; no search polynomial used')
dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(runs=len(audits),max_abs_difference=result['max_abs_difference']),indent=2))
