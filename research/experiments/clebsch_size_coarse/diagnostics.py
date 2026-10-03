from pilot import *
import scipy
out=ROOT/'reports/clebsch-size-coarse-002'
co=np.load(OUT/'coefficients.npy'); rows=json.load(open(OUT/'runs.json'))+json.load(open(out/'runs.json'))
x=np.array(rows[0]['x']); rec=[]
seen=set()
for row in rows:
    if row['k']!=13 or row['name'] in seen or 'control' in row['name']:continue
    seen.add(row['name']); model=Model(np.array(row['types']),co)
    endpoint=np.r_[x[:12],0,x[-2:]]; f,g=model.fg(endpoint)
    rec.append({'name':row['name'],'parent_endpoint_F':f,'derivative_transfer_copy0_to_new':float(g[12]-g[0])})
json.dump({'invasion_slopes':rec,'scipy_version':scipy.__version__,'seconds':time.time()-start,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},open(out/'diagnostics.json','w'),indent=2)
print(json.dumps(rec,indent=2))
