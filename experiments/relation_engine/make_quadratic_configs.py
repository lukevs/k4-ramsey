"""Generate explicit config-only replay fixtures for the two tested refinements."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/"configs";OUT.mkdir(exist_ok=True)
Q=65536;N=192
diff=[]
for a in range(3):
 for x in range(64):diff.append([((b-a)%3)*64+(x^y) for b in range(3) for y in range(64)])
def qm(z):
 q=((z>>0)&1)^((z>>1)&1)
 for i in range(0,6,2):q^=((z>>i)&1)&((z>>(i+1))&1)
 return q
def old(e,z):return e*14+2*z.bit_count()+qm(z)
def mi(a,b):
 if a>b:a,b=b,a
 return [(x,y) for x in range(4) for y in range(x,4)].index((a,b))
def r80(e,z):return e*40+(z&3)*10+mi((z>>2)&3,(z>>4)&3)
parent28=json.loads((ROOT/"reports/quadratic-scheme-001/report.json").read_text())["rationalized_parameters"]
parent80=json.loads((ROOT/"reports/quadratic-next-002/report.json").read_text())["rationalized_parameters"]
cases=[
 ("quadratic80",80,[r80(a!=0,z) for a in range(3) for z in range(64)],
  [parent28[old(e,z)] for e in range(2) for z in range(64) if r80(e,z)==r80(e,z)],None),
]
# Build dense relation vectors without relying on ordering coincidences.
p80=[0]*80;g80=[0]*80
for e in range(2):
 for z in range(64):p80[r80(e,z)]=parent28[old(e,z)];g80[r80(e,z)]=old(e,z)
configs=[("quadratic80",80,[r80(a!=0,z) for a in range(3) for z in range(64)],p80,g80,
          "16901897618722474829755212952533952/560768060721761383881293603555770368"),
         ("quadratic128",128,[(a!=0)*64+z for a in range(3) for z in range(64)],
          [parent80[r80(e,z)] for e in range(2) for z in range(64)],
          [r80(e,z) for e in range(2) for z in range(64)],
          "16901715161505423885044215944464856/560768060721761383881293603555770368")]
for name,r,relations,p,groups,expected in configs:
 d={"schema":"relation-engine-config-v1","mode":"translated","n":N,"q":Q,"relation_count":r,
    "difference_table":diff,"relation_of_difference":relations,"probability_numerators":p,
    "constraint_group_ids":groups,"integer_direction":[0]*r,"expected_parent_fraction":expected,
    "materialize_candidate":False}
 (OUT/f"{name}.json").write_text(json.dumps(d,separators=(",",":"))+"\n")
