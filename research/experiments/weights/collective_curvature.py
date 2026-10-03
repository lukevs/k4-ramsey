"""Projected Hessian/CG proposal, certified only by exact weighted recounts."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from research.experiments.weights.collective_gradient import screen
from research.experiments.weights.pair_transfer import induced_edges


def hessian(f):
    n=len(f['rows'])
    matrix=[[0]*n for _ in range(n)]
    for i in range(n):
        matrix[i][i]=12+36*f['db'][i]+24*f['tb'][i]
        for j in range(i):
            blue=f['rows'][i][j]=='0'
            color=f['blue'] if blue else f['red']
            shared=induced_edges(color,color[i]&color[j])
            triangles=(f['blue'][i]&f['blue'][j]).bit_count() if blue else 0
            matrix[i][j]=matrix[j][i]=48*blue+60*triangles+24*shared
    return matrix


def project(vector):
    mean=sum(vector)/len(vector)
    return [v-mean for v in vector]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def projected_cg(matrix,gradient,iterations=60):
    """Float heuristic only. Stop on nonpositive curvature; never certify it."""
    n=len(gradient)
    rhs=project([-float(g) for g in gradient])
    x=[0.0]*n
    r=rhs[:]
    p=r[:]
    rr=dot(r,r)
    history=[]
    for iteration in range(iterations):
        if rr<1e-12:
            break
        hp=project([dot(row,p) for row in matrix])
        curvature=dot(p,hp)
        history.append(dict(iteration=iteration,residual_squared=rr,curvature=curvature))
        if curvature<=0:
            # Search can still test a descent-oriented nonpositive direction.
            if iteration==0: x=p[:]
            break
        step=rr/curvature
        x=[a+step*b for a,b in zip(x,p)]
        r=[a-step*b for a,b in zip(r,hp)]
        new_rr=dot(r,r)
        if new_rr<=dot(rhs,rhs)*1e-14:
            rr=new_rr
            break
        beta=new_rr/rr
        p=[a+beta*b for a,b in zip(r,p)]
        rr=new_rr
    return project(x),history


def quantize(vector,amplitude):
    peak=max(map(abs,vector),default=0)
    if not peak: return [0]*len(vector)
    ideal=[v*amplitude/peak for v in vector]
    direction=[math.floor(v) for v in ideal]
    remainder=-sum(direction)
    # Projected vector has sum0, so flooring leaves 0..n units to distribute.
    if not 0<=remainder<=len(vector): raise RuntimeError('nonzero projected direction')
    order=sorted(range(len(vector)),key=lambda i:ideal[i]-direction[i],reverse=True)
    for i in order[:remainder]: direction[i]+=1
    return direction


def build_direction(f,gradient,amplitude):
    started=time.monotonic()
    matrix=hessian(f)
    construction=time.monotonic()-started
    vector,history=projected_cg(matrix,gradient)
    direction=quantize(vector,amplitude)
    if dot(gradient,direction)>0: direction=[-v for v in direction]
    diagnostics=dict(hessian_seconds=construction,total_seconds=time.monotonic()-started,
                     cg_history=history,direction_gradient=dot(gradient,direction),
                     direction_curvature=dot(direction,[dot(row,direction) for row in matrix]),
                     source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     trust='Floating projected CG proposes a direction only; no PSD or convergence claim.')
    return direction,diagnostics


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--base',type=int,default=4096)
    parser.add_argument('--amplitude',type=int,default=64)
    parser.add_argument('--seconds',type=float,default=120)
    args=parser.parse_args()
    result=screen(args.input,args.out,base=args.base,amplitude=args.amplitude,
                  seconds=args.seconds,direction_builder=build_direction)
    # Snapshot our additional source alongside the common line-screen snapshot.
    (args.out/'curvature_source_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result,indent=2))
    raise SystemExit(result['status']!='completed')


if __name__=='__main__': main()
