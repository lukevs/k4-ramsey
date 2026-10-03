"""Find explicit Schur-bound violations in saved relaxation moments."""
import ast
import json
from pathlib import Path
import re
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/round5_C1'))
from base import base


def canon(walk):
    out=[]
    for seq in (walk,walk[::-1]):
        for r in range(len(walk)):
            s=seq[r:]+seq[:r]; shift=s[0]%16
            out.append(tuple((v//16)*16+((v%16)^shift) for v in s))
    return min(out)


source=Path(sys.argv[1]); output=Path(sys.argv[2])
report=json.loads((source/'sdp.json').read_text())
W,_,_=base(report['p'],report['h'])
z=np.load(source/'z.npy')
idx={ast.literal_eval(re.sub(r'np.int64\((-?\d+)\)',r'\1',k)):i
     for k,i in json.loads((source/'idx.json').read_text()).items()}
rows=[]
for key,i in idx.items():
    if len(key)!=4 or key[0]=='D': continue
    if key[1]==key[3]: x,c,b,_=key
    elif key[0]==key[2]: c,x,_,b=key
    else: continue
    q=float(z[i])
    for left,right in (((x,c),(c,b)),((c,b),(x,c))):
        density=float(W[left]); op=min(density,1-density)
        hs=float(z[idx[canon(right)]])
        allowed=op**2*hs
        rows.append(dict(path=[x,c,b],contracted_edge=list(left),edge_mean=density,
                         requested_path_norm_squared=q,other_edge_HS_squared=hs,
                         valid_upper=allowed,excess=q-allowed,
                         ratio=q/allowed if allowed>0 else None))
rows.sort(key=lambda v:v['excess'],reverse=True)
result=dict(source=str(source),tested_inequalities=len(rows),
            violations_above_1e_8=sum(r['excess']>1e-8 for r in rows),
            worst=rows[0],top_ten=rows[:10])
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='top_ten'},indent=2))
