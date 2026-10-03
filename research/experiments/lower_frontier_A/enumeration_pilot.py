"""Independent small census validation and bounded N9 generator sample."""
import json,time,resource
from sage.all import graphs
start=time.monotonic()
def quotient_key(g):
    return min(g.canonical_label(algorithm='sage').graph6_string(),g.complement().canonical_label(algorithm='sage').graph6_string())
result={}
for n in (5,6,7,8):
    tm=time.monotonic(); keys=set(); total=0
    for g in graphs.nauty_geng(str(n)):
        total+=1; keys.add(quotient_key(g))
    result[str(n)]=dict(ordinary=total,colour_quotient=len(keys),seconds=time.monotonic()-tm)
    print(json.dumps(dict(n=n,**result[str(n)])),flush=True)
# Exhaust only this small edge-count sector, not all nine-vertex graphs.
tm=time.monotonic(); keys=set(); total=0
for g in graphs.nauty_geng('9 0:8'):
    total+=1; keys.add(quotient_key(g))
result['N9_sparse_sector']=dict(edge_count_max=8,ordinary=total,colour_quotient=len(keys),seconds=time.monotonic()-tm)
result['maxrss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
result['elapsed']=time.monotonic()-start
open('enumeration.json','w').write(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
