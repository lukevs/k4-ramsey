"""Independent bitmask-pair recount of every exported stationarity coefficient."""
from itertools import combinations
from fractions import Fraction as Q
from pathlib import Path
import json,hashlib,time
start=time.monotonic(); src=Path('reports/lower-frontier-C-cut-001/cut.json')
d=json.loads(src.read_text()); U=Q(d['U'])
inc=Q(8450462766487926638466333426306607129,280384030360880691940646801777885184000)
assert U>inc
pairs=list(combinations(range(7),2)); masks=[]
for S in combinations(range(7),4):
 masks.append((sum(1<<i for i in S),sum(1<<k for k,(a,b) in enumerate(pairs) if a in S and b in S)))
for row in d['coefficients']:
 edges={tuple(sorted(e)) for e in row['edges']}
 E=sum(1<<k for k,e in enumerate(pairs) if e in edges)
 good=[v for v,m in masks if (E&m) in (0,m)]
 count=sum((a&b).bit_count()==1 for a,b in combinations(good,2))
 F=Q(len(good),35); B=Q(count,70)
 assert F==Q(row['F']) and B==Q(row['B']) and B-U*F==Q(row['B_minus_UF'])
report=dict(rows=len(d['coefficients']),all_pass=True,U=str(U),incumbent=str(inc),
 scope='All coefficients independently recounted by unordered pairs of monochromatic four-sets intersecting at one vertex; U exceeds exact incumbent.',
 source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),seconds=time.monotonic()-start)
Path('reports/stationarity-cut-001/coefficient-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
