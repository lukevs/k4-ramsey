"""Recount the Section 7 prism example from arXiv:2607.12461v1.

This is a triangle-free maximum-degree-five control, NOT a K4 construction.
"""
from itertools import combinations
import json
from pathlib import Path


def edge(A,i,j):
    A[i][j]=A[j][i]=1


def stats(A):
    n=len(A)
    degrees=list(map(sum,A))
    triangles=sum(A[i][j]*A[i][k]*A[j][k] for i,j,k in combinations(range(n),3))
    per_root=[0]*n
    for subset in combinations(range(n),5):
        # A simple five-vertex graph with all degrees two is a five-cycle.
        if all(sum(A[v][u] for u in subset)==2 for v in subset):
            for v in subset:
                per_root[v]+=1
    total=sum(per_root)//5
    path_formula=[]
    for v in range(n):
        outside=[x for x in range(n) if x!=v and not A[v][x]]
        k={x:sum(A[x][a]*A[v][a] for a in range(n)) for x in outside}
        path_formula.append(sum(k[x]*k[y]*A[x][y] for x,y in combinations(outside,2)))
    assert triangles==0 and max(degrees)==5
    assert path_formula==per_root
    codegrees=[sum(A[u][z]*A[v][z] for z in range(n)) for u,v in combinations(range(n),2) if not A[u][v]]
    return {"degrees":degrees,"triangles":triangles,"pentagons":total,
            "pentagons_per_root":per_root,"root_slacks_from_60":[60-x for x in per_root],
            "nonedge_codegrees":sorted(set(codegrees)),"attachment_formula_exact":True}


S={1,2,4,8,15}
clebsch=[[int((i^j) in S) for j in range(16)] for i in range(16)]
prism=[[0]*16 for _ in range(16)]
for a in range(1,6):
    edge(prism,0,a)
xlabels=[(1,2),(3,4),(5,1),(2,3),(4,5)]
ylabels=[(3,4),(1,5),(2,3),(4,5),(1,2)]
for i in range(5):
    edge(prism,6+i,6+(i+1)%5)
    edge(prism,11+i,11+(i+1)%5)
    edge(prism,6+i,11+i)
    for a in xlabels[i]:
        edge(prism,6+i,a)
    for a in ylabels[i]:
        edge(prism,11+i,a)
c,p=stats(clebsch),stats(prism)
assert c["pentagons"]==192 and c["pentagons_per_root"]==[60]*16
assert p["pentagons_per_root"][0]==60 and p["pentagons"]<192
report={"source":"https://arxiv.org/html/2607.12461v1#S7",
        "clebsch":c,"prism_counterexample":p,
        "interpretation":"One saturated root does not force Clebsch; other roots expose the deficit."}
out=Path("reports/global-overlap-pairs-001/local-example.json")
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
