"""Assemble immutable run/check summary and content manifest; no search."""
import signal,time,json,hashlib,subprocess
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/assumption-symmetry_insertion-001'
rows=json.loads((OUT/'runs.json').read_text())+json.loads((OUT/'boundary-runs.json').read_text())
summary={}
for label in sorted(set(r['label'] for r in rows)):
 rr=[r for r in rows if r['label']==label];summary[label]={'starts':len(rr),'best_R':min(r['R'] for r in rr),'worst_R':max(r['R'] for r in rr),'evaluation_budget_per_start':rr[0]['budget'],'dimension':rr[0]['dimension'],'statuses':[r['status'] for r in rr]}
chars=np.array([[(-1)**((x&s).bit_count()) for s in range(16)] for x in range(16)],float)/4
ev=np.array([sum((-1)**((x&s).bit_count()) for x in [1,2,4,8,15]) for s in range(16)])
residual=[]
for row in rows:
 q=np.array(row['q']);assert np.min(q)>=0 and np.max(q)<=1
 if 'guided' in row['label'] and 'release' not in row['label']:
  eig=-3 if '-3' in row['label'] else 1;B=np.kron(np.eye(12),chars[:,np.r_[0,np.where(ev==eig)[0]]]);residual.append(float(np.max(abs(q-.5-B@(B.T@(q-.5))))))
assert max(residual)<1e-9
fin=json.loads((OUT/'finite-runs.json').read_text());F=json.loads((OUT/'receipt.json').read_text())['F']
checks={'affine_guided_max_residual':max(residual),'all_profiles_feasible':True,'total_search_oracle_calls':sum(r['total_evaluations'] for r in rows),'total_search_runs':len(rows),'finite_variable_mass_best_delta':min(r['best']['F']-F for r in fin),'forced_mass_best_delta':min(x['delta'] for r in fin for x in r['forced_positive_mass']),'finite_profile_families':len(fin)}
(OUT/'summary.json').write_text(json.dumps({'families':summary,'checks':checks},indent=2)+'\n')
# Supervisor fixture checks (success/failure/timeout) and independent candidate audit under175s hard wall timeout.
import sys
fixtures={}
for label,code,timeout in [('success','pass',1),('failure','raise SystemExit(3)',1),('timeout','import time; time.sleep(1)',.02)]:
 try:r=subprocess.run([sys.executable,'-c',code],timeout=timeout,capture_output=True);fixtures[label]=r.returncode
 except subprocess.TimeoutExpired:fixtures[label]='terminated/reaped'
assert fixtures=={'success':0,'failure':3,'timeout':'terminated/reaped'}
args=[sys.executable,str(ROOT/'experiments/clebsch_bowl/audit_weighted.py'),'--candidate',str(OUT/'checked-positive-mass-witness.json'),'--out',str(OUT/'independent-candidate-audit-175.json')]
r=subprocess.run(args,timeout=175,capture_output=True,text=True);assert r.returncode==0,r.stderr
(OUT/'supervisor-check.json').write_text(json.dumps({'fixtures':fixtures,'audit_command':args,'audit_hard_timeout_seconds':175,'returncode':r.returncode,'all_children_reaped':True},indent=2)+'\n')
paths=list((ROOT/'experiments/assumption_symmetry_insertion').glob('*.py'))+list(OUT.glob('*.json'))+list(OUT.glob('*.log'))+[ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json',ROOT/'experiments/clebsch_bowl/audit_weighted.py']
manifest={'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'created_unix':time.time(),'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.name!='manifest.json'},'command_prefix':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python','scripts_in_order':['pilot.py','boundary.py','obstruction.py','finite_check.py','check_obstruction.py','finalize.py'],'status':'all local jobs completed and reaped; no promotion; parent owns incumbent','limitation':'Original standalone audit inherited180s alarm and completed in<.1s; independently rerun here under175s parent timeout. Other numerical jobs set175s alarm internally.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(checks,indent=2))
