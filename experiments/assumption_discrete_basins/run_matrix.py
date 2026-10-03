import subprocess,time,json,hashlib,sys,signal
from pathlib import Path
signal.alarm(175)
root=Path('reports/assumption-discrete_basins-001');exe='experiments/assumption_discrete_basins/unrestricted'
mode,seed,steps,init=sys.argv[1:];name=f'matrix-{init}-s{seed}-k{steps}-{mode}'
cmd=[exe,mode,'1024',seed,steps,init,str(root/(name+'.json'))]
st=time.time();p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(root/'running.json').write_text(json.dumps(dict(pid=p.pid,command=cmd,start_utc=time.strftime('%FT%TZ',time.gmtime(st)),deadline=st+175)))
print('RUNNING',p.pid,name,flush=True)
try:out,_=p.communicate(timeout=170)
except subprocess.TimeoutExpired:p.kill();out,_=p.communicate()
r=dict(command=cmd,pid=p.pid,start=st,end=time.time(),returncode=p.returncode,output=out,source_sha256=hashlib.sha256(Path(exe+'.cpp').read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(Path(exe).read_bytes()).hexdigest(),threads=1)
(root/(name+'-receipt.json')).write_text(json.dumps(r,indent=2));(root/'running.json').write_text(json.dumps(dict(pid=None,status='finished and reaped')));print(out,flush=True)
