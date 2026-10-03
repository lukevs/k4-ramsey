import subprocess,time,json,hashlib,os,sys,signal,platform
from pathlib import Path
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
root=Path('reports/assumption-discrete_basins-001');exe='research/experiments/assumption_discrete_basins/search'
mode=sys.argv[1]; runs=[]
if mode=='recovery':
 jobs=[['anneal',0,1024,901,8192,'damaged','recovery-covered-anneal']]
elif mode=='f2':
 jobs=[[m,0,1024,s,8192,'random',f'f2-s{s}-{m}'] for s in (1101,1102,1103) for m in ('downhill','anneal')]
else:
 jobs=[[m,1,257,s,12000,'random',f'z257-s{s}-{m}'] for s in (1201,1202,1203) for m in ('downhill','anneal')]
for m,k,n,seed,steps,init,name in jobs:
 cmd=[exe,m,str(k),str(n),str(seed),str(steps),init,str(root/(name+'.json'))]
 start=time.time();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (root/'running.json').write_text(json.dumps(dict(pid=p.pid,command=cmd,start_utc=time.strftime('%FT%TZ',time.gmtime(start)),deadline=start+175)))
 print('RUNNING',p.pid,name,flush=True)
 try: output,_=p.communicate(timeout=170)
 except subprocess.TimeoutExpired:p.kill();output,_=p.communicate()
 receipt=dict(command=cmd,pid=p.pid,returncode=p.returncode,start=start,end=time.time(),output=output,source_sha256=hashlib.sha256(Path('research/experiments/assumption_discrete_basins/search.cpp').read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(Path(exe).read_bytes()).hexdigest(),platform=platform.platform(),threads=1)
 (root/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2));print(output,flush=True)
 if p.returncode:break
(root/'running.json').write_text(json.dumps(dict(pid=None,status='batch finished and reaped')))
