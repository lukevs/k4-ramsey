import os, signal, time
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(max(1,min(170,int(1790745600-time.time()))))
from pathlib import Path
import json,hashlib,math,statistics,sys,platform
from evaluator import evaluate
out=Path('reports/unrestricted-bowl-challenge-001'); records=[];st=time.monotonic()
for p in sorted(out.glob('*.json')):
 d=json.loads(p.read_text())
 if 'W' not in d:continue
 q=evaluate(d['W'],d['m']);err=abs(q['objective']-d['objective']);assert err<1e-12
 n=len(d['m']);weighted_rms=math.sqrt(sum(d['m'][i]*d['m'][j]*(d['W'][i][j]-.5)**2 for i in range(n) for j in range(n)))
 records.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'n':n,'variable':d['variable'],'kind':d['start_kind'],'oracle_error':err,**q,'effective_mass_classes':d['effective_mass_classes'],'tiny_masses':d['tiny_masses'],'weighted_rms_from_half':weighted_rms,'min_mass':min(d['m']),'success':d['success'],'search_seconds':d['seconds'],'nearly_identical_row_pairs':d['nearly_identical_row_pairs']})
paired=[]
for r in records:
 if '-equal' in r['file'] and 'rebuild' not in r['file'] and not r['file'].startswith('control'):
  v=next(x for x in records if x['file']==r['file'].replace('-equal','-variable'))
  paired.append({'equal':r['file'],'variable':v['file'],'variable_minus_equal':v['objective']-r['objective']})
best=min(records,key=lambda x:x['objective']); report={'label':'independent numerical ordered-tuple recount, not formal or exact candidate certificate','records':records,'pairs':paired,'best':best,'max_oracle_error':max(r['oracle_error'] for r in records),'audit_seconds':time.monotonic()-st,'incumbent':.030138887566497220,'gap':best['objective']-.030138887566497220,'python':sys.version,'platform':platform.platform(),'pid':os.getpid()}
with (out/'audit.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k not in ('records','pairs')},indent=2))
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in (Path('research/experiments/unrestricted_bowl_challenge'),out) for p in sorted(folder.glob('*')) if p.is_file()}
with (out/'manifest.json').open('x') as f:json.dump(manifest,f,indent=2)
