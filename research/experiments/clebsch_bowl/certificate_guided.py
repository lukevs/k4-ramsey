"""Bounded certificate diagnostics and coarse-model direction tests."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import numpy as np
import json,sys,struct,subprocess,hashlib,time
from pathlib import Path
from fractions import Fraction

OUT=Path('reports/certificate-guided-001')
CERT=Path('reports/toolbox-extension-001/pentagon-independent-v2')
BEST=Path('reports/round4-E5-depth2-001/graphon-candidate.json')

def write_matrix(path,W):
    with path.open('wb') as f:f.write(struct.pack('i',len(W)));f.write(np.asarray(W,dtype=np.float64).tobytes())

def coarse(levels):
    W=np.empty((192,192)); cats=np.empty((192,192),dtype=int)
    for i in range(192):
        a,x=divmod(i,16);ac,ae,as_=a//4,a//2%2,a%2
        for j in range(192):
            b,y=divmod(j,16);bc,be,bs=b//4,b//2%2,b%2;z=x^y
            t=(0 if ae==be else 3) if ac==bc and as_==bs else ((1 if ae==be else 0) if as_==bs else (2 if ac==bc else 0))
            c=0 if z==0 else (1 if z in (1,2,4,8,15) else 2)
            cats[i,j]=3*t+c;W[i,j]=levels[3*t+c]
    assert np.array_equal(W,W.T)
    return W,cats

LEVELS=np.array([0,0,1, 1,1,0, .779180833031354,.779180833031354,0, .5342651880306992,1,0])

def sample(name,path,N,seed,target=None):
    dest=OUT/(name+'.json');cmd=['/private/tmp/certificate_sample',str(OUT/'components.bin'),str(path),str(N),str(seed),str(dest)]
    if target is not None:cmd.append(str(target))
    t=time.monotonic();subprocess.run(cmd,check=True,timeout=180);r=json.loads(dest.read_text());r['seconds']=time.monotonic()-t;r['seed']=seed
    dest.write_text(json.dumps(r,indent=2)+'\n');print(name,r['seconds'],r['mean'],flush=True);return r

def prepare():
    OUT.mkdir(exist_ok=False,parents=True)
    with (CERT/'enumerator-input.txt').open() as inp:
        r=subprocess.run(['/private/tmp/check_toolbox_components',str(OUT/'components.bin')],stdin=inp,text=True,capture_output=True,check=True,timeout=180)
    assert list(map(int,r.stdout.split()))==json.loads((CERT/'coefficient-numerators.json').read_text())
    raw=(OUT/'components.bin').read_bytes();nb,ng,L=struct.unpack('iid',raw[:16]);assert nb==14 and ng==1044
    ids=np.frombuffer(raw,dtype=np.int32,count=2**21,offset=16);table=np.frombuffer(raw,dtype=np.float64,offset=16+4*2**21).reshape(ng,nb+2)
    expected=np.bincount(ids,minlength=ng)@table/(2**21)
    assert abs(expected[-1]-1/32)<1e-14
    assert np.max(abs(table[:,-1]-L-table[:,:-1].sum(axis=1)))<1e-14
    assert table[:,nb].min()>-1e-14
    (OUT/'component-table.json').write_text(json.dumps(dict(lower_bound=L,coefficients=table.tolist(),fair_coin_expected=expected.tolist()))+'\n')
    d=json.loads(BEST.read_text());assert len(set(d['block_weights']))==1
    W=np.asarray(d['red_probability_numerators'],dtype=float)/d['edge_probability_denominator'];write_matrix(OUT/'best.bin',W)
    B,cats=coarse(LEVELS);write_matrix(OUT/'base.bin',B);np.save(OUT/'categories.npy',cats)
    write_matrix(OUT/'fair.bin',np.array([[.5]]));write_matrix(OUT/'blue.bin',np.array([[0.]]))
    meta=dict(best=str(BEST),best_sha256=hashlib.sha256(BEST.read_bytes()).hexdigest(),certificate_sha256=hashlib.sha256((CERT/'integer-certificate.json').read_bytes()).hexdigest(),levels=LEVELS.tolist(),numpy=np.__version__)
    (OUT/'inputs.json').write_text(json.dumps(meta,indent=2)+'\n')

def rooted_objective(W,root=0):
    n=len(W);value=0.
    for U in (W,1-W):
        V=U*U[root][None,:]
        value+=np.dot(U[root],np.einsum('ij,ij->i',V@U,V))
    return value/n**3

def direction_test():
    diagnostic=json.loads((OUT/'base-P4-gradient.json').read_text())
    g=np.array(diagnostic['mean'][16:]);se=np.array(diagnostic['standard_error'][16:])
    D=-g;D[(LEVELS==0)&(D<0)]=0;D[(LEVELS==1)&(D>0)]=0
    D[abs(g)<3*se]=0
    assert np.max(abs(D))>0
    D/=np.max(abs(D))
    B,_=coarse(LEVELS);f0=rooted_objective(B)
    assert abs(f0-.030138977289665338)<1e-14
    # Translation transitivity checked by all-root objective values.
    root_values=[rooted_objective(B,i) for i in range(192)]
    assert max(root_values)-min(root_values)<1e-14
    eps=1e-5;eye=np.eye(12)
    fg=np.array([(rooted_objective(coarse(LEVELS+eps*e)[0])-rooted_objective(coarse(LEVELS-eps*e)[0]))/(2*eps) for e in eye])
    source=dict(direction=D.tolist(),term_gradient=g.tolist(),term_gradient_se=se.tolist(),objective_gradient=fg.tolist(),objective_slope=float(fg@D),parent_exact_family_value=f0,all_root_spread=max(root_values)-min(root_values))
    rows=[]
    for step in (0,.001,.005,.02,.05,.1):
        levels=np.clip(LEVELS+step*D,0,1);W,_=coarse(levels);name='path-directed-'+str(step)
        write_matrix(OUT/(name+'.bin'),W)
        r=sample(name,OUT/(name+'.bin'),10000000,7721)
        row=dict(step=step,levels=levels.tolist(),density=rooted_objective(W),diagnostic=name+'.json')
        rows.append(row)
    # Confirm selected child by separate full-root weighted evaluator.
    from audit_weighted import density
    chosen=rows[3];W,_=coarse(np.array(chosen['levels']))
    check=density(W,np.ones(192)/192)
    assert abs(check-chosen['density'])<1e-14
    base_batches=np.array(json.loads((OUT/rows[0]['diagnostic']).read_text())['batch_means'])
    for row in rows:
        r=json.loads((OUT/row['diagnostic']).read_text());delta=np.array(r['batch_means'])-base_batches
        row['P4_term_change']=float(delta[:,8].mean());row['P4_term_change_se']=float(delta[:,8].std(ddof=1)/np.sqrt(len(delta)))
        row['other_terms_change']=float(delta[:,:15].sum(axis=1).mean()-delta[:,8].mean())
        row['actual_density_change']=row['density']-f0
    source.update(rows=rows,independent_child_recount=check)
    (OUT/'direction-test.json').write_text(json.dumps(source,indent=2)+'\n')
    print(json.dumps(source,indent=2),flush=True)

def repair_test():
    # Does the certificate-directed excursion reach a different objective basin?
    from scipy.optimize import minimize
    previous=json.loads((OUT/'direction-test.json').read_text());rows=[]
    for seedrow in (previous['rows'][3],previous['rows'][-1]):
        def fun(x):return 1e5*rooted_objective(coarse(x)[0])
        result=minimize(fun,np.array(seedrow['levels']),method='L-BFGS-B',jac='3-point',
                        bounds=[(0,1)]*12,options=dict(maxiter=100,ftol=1e-14,gtol=1e-7,maxls=30))
        row=dict(start_step=seedrow['step'],start_density=seedrow['density'],final_density=result.fun/1e5,
                 levels=result.x.tolist(),success=bool(result.success),message=str(result.message),iterations=int(result.nit),evaluations=int(result.nfev))
        rows.append(row)
    (OUT/'repair-test.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2),flush=True)

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='test':direction_test()
    elif sys.argv[1]=='repair':repair_test()
    elif sys.argv[1]=='diagnose':
        expected=np.array(json.loads((OUT/'component-table.json').read_text())['fair_coin_expected'])
        r=sample('fair',OUT/'fair.bin',1000000,7701)
        assert np.max(abs(np.array(r['mean'])-expected)/(np.array(r['standard_error'])+1e-14))<7
        z=sample('blue',OUT/'blue.bin',4000,7702);assert abs(z['mean'][-1]-1)<1e-14
        for name in ('best','base'):
            r=sample(name,OUT/(name+'.bin'),10000000,7703)
            actual=.030138887566497220 if name=='best' else .030138977289665338
            assert abs(r['mean'][-1]-actual)<7*r['standard_error'][-1]
            assert abs(sum(r['mean'][:-1])+r['lower_bound']-r['mean'][-1])<1e-12
        (OUT/'validation.json').write_text(json.dumps(dict(fair_coin_pass=True,deterministic_blue_pass=True,known_objective_checks_pass=True,coefficient_identity_exact_numerators_match=True),indent=2)+'\n')
