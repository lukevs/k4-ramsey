"""Entrywise check: sym[pi(s,x), pi(t,y)] == rule(T[s][t], x^y) with pi(s,x)=lab[s][x^b_s]."""
import json, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
B = np.array(json.loads((ROOT/"reports/literature-two-parameter-001/graphon-candidate.json").read_text())["red_probability_numerators"])
D=json.load(open(ROOT/'experiments/round4_E11/coords.json')); R=json.load(open(ROOT/'experiments/round4_E11/rule.json'))
C={0,1,2,4,8,15}; P,H=51064,35015
def val(ty,z):
    c=z in C
    return {'Z':0 if c else 65536,'X':65536 if c else 0,'P':P if c else 0,'H':(H if z==0 else 65536) if c else 0}[ty]
pi={}
for s in range(12):
    for x in range(16): pi[(s,x)]=D['labels'][s][str(x^R['b'][s])]
assert len(set(pi.values()))==192
bad=0
for (s,x),u in pi.items():
    for (t,y),v in pi.items():
        if u==v: continue
        bad+= B[u,v]!=val(R['types'][s][t],x^y)
print('mismatches:',bad,'of',192*191)
json.dump({'vertex_of':{f'{s},{x}':int(u) for (s,x),u in pi.items()}},open(ROOT/'experiments/round4_E11/perm.json','w'))
