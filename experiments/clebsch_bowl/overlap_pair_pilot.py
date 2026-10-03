"""Find small jointly useful rooted-type families, holding marginal data fixed."""
from itertools import combinations
from pathlib import Path
import json
import time
import hashlib
import numpy as np
import coupled_flag_pilot as core
from coupled_flag_followup import certify

start = time.monotonic()
out = Path("reports/global-overlap-pairs-001")
out.mkdir(exist_ok=True,parents=True)
g5,g6 = core.atlas(5),core.atlas(6)
b5 = sum((core.gram_coefficients(g5,r) for r in (1,3)),[])
b4 = core.gram_coefficients(g6,4)
groups = {}
for b in b4:
    t = b["type"]
    key = tuple(sorted({t,core.canonical_bits(t^63,4)}))
    groups.setdefault(key,[]).append(b)
keys = list(groups)
P = core.marginal(g6,g5)
c = np.array(list(map(core.objective,g6)))
runs=[]
for i,j in combinations(range(len(keys)),2):
    assert time.monotonic()-start<150, "pilot deadline"
    extra=groups[keys[i]]+groups[keys[j]]
    result=core.solve(f"pair_{keys[i]}_{keys[j]}",c,b5,extra,P=P)
    result["groups"]=[keys[i],keys[j]]
    runs.append(result)
    (out/"partial.json").write_text(json.dumps(runs,indent=2)+"\n")
best=max(runs,key=lambda r:r["objective"])
chosen=[tuple(k) for k in best["groups"]]
extra=sum((groups[k] for k in chosen),[])
data={}
rerun=core.solve("selected_pair_certificate",c,b5,extra,P=P,certificate=data)
cert=certify(c,data,out/"full-certificate.json")
meta={"base":[{k:b[k] for k in ("roots","type","flags")} for b in b5],
      "extra":[{k:b[k] for k in ("roots","type","flags")} for b in extra],
      "graphs6":np.array(g6).tolist()}
(out/"coefficient-metadata.json").write_text(json.dumps(meta)+"\n")
# Reuse the already rational feasible OLD-level point, not a graphon witness.
old=Path("reports/global-coupled-pilot-003/baseline-feasible-witness.json")
(out/old.name).write_bytes(old.read_bytes())
(out/"result.json").write_text(json.dumps({"runs":runs,"selected_groups":chosen,
    "certificate":cert,"seconds":time.monotonic()-start,
    "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+"\n")
print(json.dumps({"selected_groups":chosen,"certificate":cert}),flush=True)
