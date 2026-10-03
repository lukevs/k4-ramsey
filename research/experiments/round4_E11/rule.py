"""E11: extract (type, shift) rule from coords.json, gauge-fix, verify entrywise + value."""
import json, sys
import numpy as np
from pathlib import Path
from fractions import Fraction
ROOT = Path(__file__).resolve().parents[3]
D=json.load(open(ROOT/'research/experiments/round4_E11/coords.json'))
S=[1,2,4,8,15]; C=set([0]+S)
T={}; A={}
def classify(f):
    for a in range(16):
        Ca={c^a for c in C}
        pats={'Z':lambda z:'0' if z in Ca else 'F','X':lambda z:'F' if z in Ca else '0',
              'P':lambda z:'P' if z in Ca else '0','H':lambda z:('H' if z==a else 'F') if z in Ca else '0'}
        for k,fn in pats.items():
            if all(fn(z)==f[z] for z in range(16)): return k,a
    raise ValueError(f)
for s in range(12):
    for t in range(12):
        T[s,t],A[s,t]=classify(D['table'][f'{s},{t}'])
b=[A[0,t] for t in range(12)]
Ag={(s,t):A[s,t]^b[s]^b[t] for s in range(12) for t in range(12)}
print('types:'); [print(' '.join(T[s,t] for t in range(12))) for s in range(12)]
print('gauge-fixed shifts (hex):'); [print(' '.join('%x'%Ag[s,t] for t in range(12))) for s in range(12)]
json.dump({'types':[[T[s,t] for t in range(12)] for s in range(12)],'shifts':[[Ag[s,t] for t in range(12)] for s in range(12)],'b':b},open(ROOT/'research/experiments/round4_E11/rule.json','w'))
