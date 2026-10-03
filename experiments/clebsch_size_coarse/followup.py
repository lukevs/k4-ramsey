from pilot import *
from fractions import Fraction
OUT2=ROOT/'reports/clebsch-size-coarse-002'; OUT2.mkdir(exist_ok=True)
co=np.load(OUT/'coefficients.npy'); old=json.load(open(OUT/'runs.json')); base=old[0]; x=np.array(base['x'])
ids=list(range(12))+[0]; dup=T[np.ix_(ids,ids)]; xd=np.r_[x[:12],x[0]/2,x[-2:]]; xd[0]/=2
rows=[]
# Representatives by old edge type: changes to the new copy only.
for oldtype,newtypes in [(0,[1,2,3]),(1,[0,3]),(2,[0,3]),(3,[0,1,2])]:
    j=next(j for j in range(1,12) if T[0,j]==oldtype)
    for newtype in newtypes:
        td=dup.copy(); td[j,12]=td[12,j]=newtype
        name=f'clone0_to{j}_{TYPES[oldtype]}to{TYPES[newtype]}'
        rows.append(fit(name,td,co,False))
        rows.append(fit(name,td,co,True,seed=704,x0=xd))
        json.dump(rows,open(OUT2/'runs.json','w'),indent=2)
# Independent starts for deletions, retain correct typed domains.
for row in [r for r in old if r['free'] and (r['k'] in [10,11] or r['name']=='parent12')]:
    rows.append(fit(row['name']+'_restart',np.array(row['types']),co,True,seed=918))
json.dump(rows,open(OUT2/'runs.json','w'),indent=2)
allrows=old+rows
selected={
 'weighted-k12':min((r for r in allrows if r['k']==12 and r['free']),key=lambda r:r['F']),
 'best-deletion-k11':min((r for r in allrows if r['k']==11),key=lambda r:r['F']),
 'best-deletion-k10':min((r for r in allrows if r['k']==10),key=lambda r:r['F']),
 'best-changed-k13':min((r for r in allrows if r['k']==13 and 'control' not in r['name']),key=lambda r:r['F']),
 'positive-equal-k13':min((r for r in allrows if r['k']==13 and 'control' not in r['name'] and not r['free']),key=lambda r:r['F']),
}
manifest=[]
for name,r in selected.items():
    xx=np.array(r['x']); t=np.array(r['types']); Q=10**12
    N=np.rint(matrix(t,*xx[-2:])*Q).astype(np.int64)
    weights=[str(Fraction(str(v))/16) for v in xx[:-2] for _ in range(16)]
    witness={'schema':'rational-step-graphon-v1','edge_probability_denominator':Q,'red_probability_numerators':N.tolist(),'block_weights':weights,'metadata':{'source_row':r,'rounding':'p,h rounded to denominator 10^12; masses exact rational interpretation of printed decimals','evidence':'search-side; independent parent audit requested'}}
    path=OUT2/(name+'.json'); path.write_text(json.dumps(witness))
    value=direct(N/Q,np.array([float(Fraction(w)) for w in weights])/sum(float(Fraction(w)) for w in weights))
    manifest.append({'name':name,'path':str(path.relative_to(ROOT)),'F':value,'search_F':r['F'],'min_coarse_mass':min(xx[:-2]),'max_coarse_mass':max(xx[:-2]),'p':xx[-2],'h':xx[-1],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
json.dump(manifest,open(OUT2/'witnesses.json','w'),indent=2)
meta={'seconds':time.time()-start,'termination':'completed','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'best_F':min(r['F'] for r in allrows),'rows':len(rows)}
json.dump(meta,open(OUT2/'meta.json','w'),indent=2)
print('WITNESSES',json.dumps(manifest),flush=True); print('DONE',json.dumps(meta),flush=True)
