from pilot import *
rows=json.load(open(OUT/'runs.json'))+json.load(open(ROOT/'reports/clebsch-size-coarse-002/runs.json'))
results=[]
for r in rows:
    if not r['free'] or r['k']<13:continue
    w=np.array(r['x'][:-2]); t=np.array(r['types']); support=np.flatnonzero(w>1e-7)
    groups=[]
    for i in support:
        for group in groups:
            if np.array_equal(t[i,support],t[group[0],support]):group.append(int(i));break
        else:groups.append([int(i)])
    results.append({'name':r['name'],'F':r['F'],'weights':w.tolist(),'new_copy_weights':w[12:].tolist(),'exact_zero_indices':np.flatnonzero(w==0).tolist(),'below_1e-7_indices':np.flatnonzero(w<=1e-7).tolist(),'identical_profile_groups_on_active_support':groups,'effective_groups_threshold_1e-7':len(groups)})
path=ROOT/'reports/clebsch-size-coarse-002/support.json';path.write_text(json.dumps(results,indent=2))
for r in results:print(r['name'], 'new',r['new_copy_weights'],'small',r['below_1e-7_indices'],'groups',r['effective_groups_threshold_1e-7'], 'merge',[g for g in r['identical_profile_groups_on_active_support'] if len(g)>1])
