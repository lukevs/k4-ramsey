"""Independent exact triangle census of each rooted neighbor graph.
Search sums ordered common-neighbor edges. This checker enumerates distinct
triangles by vertex order, then adds explicit equality-partition contributions.
"""
import json,hashlib,time,sys,signal,itertools
from pathlib import Path
signal.alarm(175)
root=Path('reports/assumption-discrete_basins-001')
def count(s,group):
 n=len(s);diff=(lambda a,b:a^b) if group=='F2' else (lambda a,b:(b-a)%n)
 total=0;parts=[]
 for color in (0,1):
  vertices=[a for a in range(n) if s[a]==color]
  rows={a:sum(1<<b for b in vertices if s[diff(a,b)]==color and a!=b) for a in vertices}
  triangles=0;edges=sum(x.bit_count() for x in rows.values());loop=int(s[0]==color)
  for a in vertices:
   bs=rows[a]>>(a+1)<<(a+1)
   while bs:
    bit=bs&-bs;b=bit.bit_length()-1;bs-=bit
    triangles+=(rows[a]&rows[b]>>(b+1)<<(b+1)).bit_count()
  value=6*triangles+3*loop*edges+loop*len(vertices)
  parts.append(dict(color=color,distinct_triangles=triangles,ordered_edges=edges,loops=loop*len(vertices),rooted_count=value));total+=value
 return total,parts
if __name__=='__main__':
 results=[]
 for p in root.glob('*.json'):
  d=json.loads(p.read_text())
  if 'generators' not in d:continue
  st=time.time();v,parts=count(d['generators'],d['group'])
  results.append(dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),count=v,expected=d['best_rooted_count'],passed=v==d['best_rooted_count'],parts=parts,seconds=time.time()-st))
  print(p.name,v,v==d['best_rooted_count'],flush=True)
 (root/(sys.argv[1] if len(sys.argv)>1 else 'audit.json')).write_text(json.dumps(dict(checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),results=results),indent=2))
 assert all(r['passed'] for r in results)
