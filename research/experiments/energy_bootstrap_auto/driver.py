"""Best-first exact-certificate queue, bounded campaign, reusable SDP worker."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,subprocess,signal,select,datetime,hashlib
from pathlib import Path
from fractions import Fraction as F
ROOT=Path('research/experiments/energy_bootstrap_auto');OUT=Path('reports/energy-bootstrap-auto-001');OLD=Path('reports/energy-bootstrap-joint-001');deadline=datetime.datetime(2026,9,30,6,29,tzinfo=datetime.timezone.utc).timestamp();events=[]
def emit(event):
 events.append(event);(OUT/'events.json').write_text(json.dumps(events,indent=2)+'\n');print(json.dumps(event),flush=True)
def remaining():return deadline-time.time()
def checked(node):
 p=node['folder']/(node['name']+'-check.json');r=json.loads(p.read_text());cert=node['folder']/(node['name']+'-certificate.json');assert hashlib.sha256(cert.read_bytes()).hexdigest()==r['certificate_sha256'];return F(r['bound'])
leaves=[]
for name in ['LL','HH','LH_left','LH_rl','LH_rrhi','fine_low','fine_high']:
 cfg=json.loads((OLD/(name+'-config.json')).read_text());node={'name':name,'folder':OLD,'config':cfg};node['bound']=checked(node);leaves.append(node)
stderr=open(OUT/'worker-stderr.log','w');worker=subprocess.Popen([sys.executable,str(ROOT/'worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,bufsize=1,start_new_session=True)
def receive(limit):
 timeout=min(limit,max(0,remaining()));ready=select.select([worker.stdout],[],[],timeout)[0]
 if not ready:raise TimeoutError('worker response deadline')
 line=worker.stdout.readline()
 if not line:raise RuntimeError('worker exited '+str(worker.poll()))
 return json.loads(line)
def request(payload):
 worker.stdin.write(json.dumps(payload)+'\n');worker.stdin.flush();r=receive(178);emit({'kind':'worker_result',**r});return r
def command(script,name=None):
 args=[sys.executable,str(ROOT/script)]+([name] if name else [])
 label=script.replace('.py','')+('-'+name if name else '')
 with open(OUT/(label+'.log'),'w') as log:run=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=min(175,max(1,remaining())),check=False)
 if run.returncode:raise RuntimeError(label+' failed; see log')
def save_state(reason):
 data={'status':reason,'deadline_utc':'2026-09-30T06:29:00Z','worker_pid':worker.pid,'leaves':[{'name':n['name'],'folder':str(n['folder']),'config':n['config'],'bound':str(n['bound'])} for n in leaves],'frontier_min':str(min(n['bound'] for n in leaves)),'frontier_min_decimal':float(min(n['bound'] for n in leaves)),'events':len(events)}
 (OUT/'queue.json').write_text(json.dumps(data,indent=2)+'\n')
try:
 emit(receive(60));save_state('running')
 diag=request({'kind':'diagnostic'});emit({'kind':'diagnostic_interpretation','note':'Numerical moment-model target only; not a construction or exact upper certificate.'})
 for iteration in range(30):
  if remaining()<160:emit({'kind':'stop','reason':'reserve time for audit and handoff','remaining_seconds':remaining()});break
  parent=min(leaves,key=lambda n:n['bound']);cfg=parent['config'];grid=cfg['grid']
  if grid>=4096:emit({'kind':'stop','reason':'finest supported dyadic grid reached'});break
  box=cfg['box'];axis=0 if box[1]-box[0]>=box[3]-box[2] else 1
  scaled=[2*v for v in box];k=axis*2;mid=box[k]+box[k+1];children=[]
  emit({'kind':'split','iteration':iteration,'parent':parent['name'],'axis':axis,'parent_bound':float(parent['bound']),'box':box,'grid':grid})
  for side in range(2):
   b=scaled.copy();b[k+1 if side==0 else k]=mid;name=f'auto_{iteration:02d}_{side}';cc={'name':name,'box':b,'grid':2*grid,'cross':True,'ordered':True,'parent':parent['name']};(OUT/(name+'-config.json')).write_text(json.dumps(cc,indent=2))
   result=request({'kind':'solve','config':cc})
   if 'error' in result or not (OUT/(name+'-dual.npz')).exists():raise RuntimeError('No usable dual for '+name)
   command('certify.py',name);command('check.py',name);node={'name':name,'folder':OUT,'config':cc};raw=checked(node);node['bound']=max(parent['bound'],raw);children.append(node);emit({'kind':'checked','name':name,'raw_bound':float(raw),'effective_bound':float(node['bound'])})
  leaves.remove(parent);leaves.extend(children);command('combine.py');save_state('running');emit({'kind':'frontier','iteration':iteration,'bound':float(min(n['bound'] for n in leaves)),'leaves':len(leaves),'remaining_seconds':remaining()})
 else:emit({'kind':'stop','reason':'iteration cap'})
 save_state('completed')
except Exception as e:
 emit({'kind':'error','error':repr(e),'note':'Existing checked parents remain valid; partial children do not replace parent.'});save_state('stopped_with_error')
finally:
 if worker.poll() is None:
  worker.stdin.close()
  try:worker.wait(timeout=3)
  except subprocess.TimeoutExpired:os.killpg(worker.pid,signal.SIGTERM);worker.wait(timeout=5)
 stderr.close();emit({'kind':'worker_reaped','returncode':worker.returncode});q=json.loads((OUT/'queue.json').read_text());q['processes_active']=False;(OUT/'queue.json').write_text(json.dumps(q,indent=2)+'\n')
