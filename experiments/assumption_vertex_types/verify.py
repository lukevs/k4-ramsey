"""Independent full-root and literal ordered-tuple audit, plus fixed-mass replay."""
import os,signal,time
signal.signal(signal.SIGALRM,signal.SIG_DFL); signal.alarm(175); START=time.time()
import json,sys,hashlib,itertools,math
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from experiments.clebsch_bowl.audit_weighted import density,selfcheck
from experiments.assumption_vertex_types.pair import PairModel
signal.alarm(max(1,int(175-(time.time()-START))))
OUT=ROOT/'reports/assumption-vertex_types-001'
def dump(n,d): (OUT/n).write_text(json.dumps(d,indent=2)+'\n')
source=ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json'; d=json.loads(source.read_text()); W=np.array(d['red_probability_numerators'],float)/d['edge_probability_denominator']; m=np.array([float(Fraction(v)) for v in d['block_weights']]); m/=sum(m)

def main():
    dump('active.json',{'pid':os.getpid(),'start_unix':START,'hard_deadline_unix':START+175,'stage':'independent audit and positive mass replay'})
    checks=selfcheck(); base=density(W,m); roots=json.loads((OUT/'rooted-runs.json').read_text())
    # Independent explicit triangle tensor, not search's matrix-product derivative contraction.
    tensors=[]
    for A in [W,1-W]: tensors.append(A[:,:,None]*A[:,None,:]*A[None,:,:]*m[:,None,None]*m[None,:,None]*m[None,None,:])
    root_audits=[]
    for r in roots:
        q=np.array(r['q']); val=np.einsum('ijk,i,j,k->',tensors[0],q,q,q)+np.einsum('ijk,i,j,k->',tensors[1],1-q,1-q,1-q)
        dist=np.sqrt(np.sum(m*(W-q)**2,axis=1)); comp=np.sqrt(np.sum(m*(1-W-q)**2,axis=1))
        root_audits.append({'name':r['name'],'R_independent':float(val),'error':float(val-r['R']),'closest_row':int(dist.argmin()),'row_rms':float(dist.min()),'closest_complement_row':int(comp.argmin()),'complement_row_rms':float(comp.min())})
    del tensors
    # Exact rational literal fixture, all repeats and nonzero probability diagonals.
    T=[[Fraction(2,7),Fraction(5,7)],[Fraction(5,7),Fraction(3,7)]]; w=[Fraction(2,5),Fraction(3,5)]
    qs=[[Fraction(1,3),Fraction(4,5)],[Fraction(2,3),Fraction(1,5)]]; B=[[Fraction(2,9),Fraction(7,9)],[Fraction(7,9),Fraction(4,9)]]
    e=Fraction(2,11); V=[T[0]+[qs[0][0],qs[1][0]],T[1]+[qs[0][1],qs[1][1]],qs[0]+B[0],qs[1]+B[1]]; mw=[(1-e)*a for a in w]+[e/2,e/2]
    exact=Fraction(0); repeats=Fraction(0); contributions=[Fraction(0)]*5
    for ids in itertools.product(range(4),repeat=4):
        ps=[V[ids[i]][ids[j]] for i,j in itertools.combinations(range(4),2)]
        term=math.prod(mw[i] for i in ids)*(math.prod(ps)+math.prod(1-p for p in ps)); exact+=term; contributions[sum(i>=2 for i in ids)]+=term
        if len(set(ids))<4: repeats+=term
    pm=PairModel(np.array(T,float),np.array(w,float)); xx=np.r_[np.array(qs,float).ravel(),float(B[0][0]),float(B[0][1]),float(B[1][1])]; got=pm.evaluate(xx,float(e))[0]
    checks.update(exact_fixture=str(exact),exact_repeat_contribution=str(repeats),exact_by_new_multiplicity=list(map(str,contributions)),exact_pair_error=abs(got-float(exact)))
    audits=[]
    for fn in sorted(OUT.glob('*witness-*.json')):
        d=json.loads(fn.read_text()); v=np.array(d['W']); ww=np.array(d['m']); value=density(v,ww); new=v[-2:,:-2]
        # Compare replacement profiles also against deleted rows, on shared remaining coordinates.
        if d['mode'] in ['replace-split','one-to-two']: old=np.arange(1,192)
        elif d['mode']=='two-to-two': old=np.array([i for i in range(192) if i not in [0,37]])
        else: old=np.arange(192)
        mm=m[old]/sum(m[old]); dist=np.sqrt(np.sum(mm*(W[:,old][None,:,:]-new[:,None,:])**2,axis=2))
        audits.append({'path':fn.name,'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'F_independent':value,'error':value-d['F_search'],'mass_sum':float(sum(ww)),'min_mass':float(min(ww)),'new_profile_min_rms_including_deleted':dist.min(axis=1).tolist(),'nearest_rows_including_deleted':dist.argmin(axis=1).tolist()})
    dump('audit-candidates.json',audits); dump('audit-roots.json',root_audits)
    # Reproduce fixed positive-mass optima and retain materialized witnesses omitted by first screen.
    pm=PairModel(W,m); fixed=[]
    for row in json.loads((OUT/'pair-runs.json').read_text()):
        if row['mode']!='insert': continue
        e=row['fixed_e']; x0=np.array(row['initial_x'])
        def fg(x):
            f,g,_,_=pm.evaluate(x,e); return f*1e4,g*1e4
        r=minimize(fg,x0,jac=True,bounds=[(0,1)]*len(x0),method='L-BFGS-B',options={'maxiter':250,'ftol':1e-14,'gtol':1e-8})
        v,mw=pm.materialize(r.x,e); val=density(v,mw); fn=f'fixed-positive-{row["id"]:02d}.json'; dump(fn,{'W':v.tolist(),'m':mw.tolist(),'F_search':pm.evaluate(r.x,e)[0],'e':e,'seed':930193})
        fixed.append({'path':fn,'sha256':hashlib.sha256((OUT/fn).read_bytes()).hexdigest(),'F_independent':val,'search_error':val-pm.evaluate(r.x,e)[0],'original_replay_error':val-row['fixed_mass_F'],'delta_vs_B192':val-base})
    dump('audit-fixed-positive.json',fixed)
    assert max(abs(r['error']) for r in audits)<2e-13
    assert max(abs(r['error']) for r in root_audits)<2e-13
    assert max(abs(r['search_error']) for r in fixed)<2e-13
    assert checks['exact_pair_error']<1e-13
    report={'base_F':base,'checks':checks,'max_candidate_error':max(abs(r['error']) for r in audits),'max_root_error':max(abs(r['error']) for r in root_audits),'max_fixed_error':max(abs(r['search_error']) for r in fixed),'counts':{'roots':len(roots),'final_witnesses':len(audits),'fixed_positive_witnesses':len(fixed)},'pid':os.getpid(),'start_unix':START,'end_unix':time.time(),'seconds':time.time()-START,'termination':'completed','checker_sha256':hashlib.sha256((ROOT/'experiments/clebsch_bowl/audit_weighted.py').read_bytes()).hexdigest(),'audit_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'independent float64 all-root recount of every saved candidate; literal exact rational tiny fixture; independent triangle tensor root check; no full-size rational or formal certificate'}
    dump('audit.json',report); dump('active.json',{'pid':None,'stage':'audit completed','end_unix':time.time()}); print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
