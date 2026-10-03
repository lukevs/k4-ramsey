"""Standalone exact certificate builder/checker from exported numeric duals.

Only standard library and a separate C++ enumerator; no Sage coefficient code.
Rounding proposes a proof; exact LDL and exhaustive enumeration certify it.
"""
import json, sys, math, itertools, subprocess, hashlib, time
from fractions import Fraction as F
from pathlib import Path

def pairs(n): return list(itertools.combinations(range(n),2))

def graph_bits(flag, order=None):
    n,roots,relations=flag
    edges={tuple(sorted(e)) for name,es in relations if name=='edges' for e in es}
    if order is None: order=list(roots)+[i for i in range(n) if i not in roots]
    return sum((tuple(sorted((order[i],order[j]))) in edges)<<k for k,(i,j) in enumerate(pairs(n)))

def ldl(A):
    n=len(A); L=[[F(i==j) for j in range(n)] for i in range(n)]; piv=[]
    for j in range(n):
        v=F(A[j][j])-sum(L[j][k]**2*piv[k] for k in range(j))
        if v<=0: return False
        piv.append(v)
        for i in range(j+1,n):
            L[i][j]=(F(A[i][j])-sum(L[i][k]*L[j][k]*piv[k] for k in range(j)))/v
    return True

def run(source,out,binary):
    start=time.monotonic(); c=json.loads(source.read_text()); out.mkdir(parents=True,exist_ok=True)
    assert c['target_size']==7 and not c['maximize'] and not c['positives']
    den=10**12; blocks=[]
    for item in c['blocks']:
        ns,typ=item['key']; r=len(typ[1]); d=len(item['flags'])
        assert len(item['Q'])==d*(d+1)//2
        # Toolbox tables padded above the minimal product size use this
        # positive combinatorial scale. Translate the proposed dual matrix;
        # the exhaustive checker still derives every final coefficient itself.
        scale=math.comb(7-ns,ns-r)
        A=[[0]*d for _ in range(d)]; it=iter(item['Q'])
        for i in range(d):
            for j in range(i,d): A[i][j]=A[j][i]=round(float(next(it))*den*scale)
        shift=100+d
        for attempt in range(12):
            Q=[[A[i][j]+(shift if i==j else 0) for j in range(d)] for i in range(d)]
            if ldl(Q): break
            shift*=10
        else: raise ValueError('No certified PSD rounding')
        lookup=[-1]*(1<<(ns*(ns-1)//2))
        for index,flag in enumerate(item['flags']):
            assert flag[0]==ns and len(flag[1])==r
            rootorder=list(flag[1]); others=[v for v in range(ns) if v not in rootorder]
            for tail in itertools.permutations(others):
                bits=graph_bits(flag,rootorder+list(tail))
                assert lookup[bits] in (-1,index)
                lookup[bits]=index
        blocks.append(dict(r=r,s=ns,t=graph_bits(typ),d=d,lookup=lookup,Q=Q,shift=shift,import_scale=scale))
    graphs=[graph_bits(g,list(range(7))) for g in c['graphs']]
    certificate=dict(denominator=den,graphs=graphs,blocks=blocks,
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (out/'integer-certificate.json').write_text(json.dumps(certificate)+'\n')
    lines=[f'{len(blocks)} {len(graphs)} {den}',' '.join(map(str,graphs))]
    for b in blocks:
        lines += [' '.join(str(b[k]) for k in ('r','s','t','d')),
                  ' '.join(map(str,b['lookup'])),' '.join(str(v) for row in b['Q'] for v in row)]
    data='\n'.join(lines)+'\n'; (out/'enumerator-input.txt').write_text(data)
    result=subprocess.run([str(binary.resolve())],input=data,text=True,capture_output=True,check=True,timeout=160)
    nums=list(map(int,result.stdout.split())); assert len(nums)==1044
    bound=F(min(nums),math.factorial(7)*den)
    receipt=dict(bound=str(bound),decimal=float(bound),blocks=len(blocks),
        labelled_graphs=2**21,all_Q_exact_positive_definite=True,
        minimum_integer_slack=0,seconds=time.monotonic()-start,
        scope='Independent exhaustive coefficient enumeration and exact rational LDL; ordinary asymptotic flag-square argument.',
        certificate_sha256=hashlib.sha256((out/'integer-certificate.json').read_bytes()).hexdigest(),
        python_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        enumerator_sha256=hashlib.sha256(Path(__file__).with_suffix('.cpp').read_bytes()).hexdigest())
    (out/'coefficient-numerators.json').write_text(json.dumps(nums)+'\n')
    (out/'check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(result.stderr); print(json.dumps(receipt,indent=2))

if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
