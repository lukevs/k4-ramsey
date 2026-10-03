"""Generate frozen and four-variable odd-characteristic quadratic configs."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE/"configs"/"f3_quadratic";OUT.mkdir(parents=True,exist_ok=True)
QDEN=65536;PROBS=[32768,32768,6554,58982]
EXPECTED={
 (4,1):"5468204710270535331561437/174085318024506601157689344",
 (4,2):"11106914428182518352953519/348170636049013202315378688",
 (5,1):"1036040721916334689/31128880624384868352",
 (5,2):"1036040721916334689/31128880624384868352",
}
def digits(x,d):
 a=[]
 for _ in range(d):a.append(x%3);x//=3
 return a
def encode(a):
 x=0;m=1
 for v in a:x+=v*m;m*=3
 return x
def data(d,twist):
 n=3**d;vec=[digits(x,d) for x in range(n)];diff=[]
 for a in vec:diff.append([encode([(b[i]-a[i])%3 for i in range(d)]) for b in vec])
 rel=[]
 for z in vec:
  if all(v==0 for v in z):rel.append(0);continue
  q=(twist*z[0]*z[0]+sum(v*v for v in z[1:]))%3;rel.append(1+q)
 matrix=[[rel[diff[i][j]] for j in range(n)] for i in range(n)]
 return n,diff,rel,matrix
for d in (4,5):
 for twist in (1,2):
  name=f"f3d{d}_twist{twist}";n,diff,rel,matrix=data(d,twist)
  common={"schema":"relation-engine-config-v1","n":n,"q":QDEN,"relation_count":4,
          "probability_numerators":PROBS,"constraint_group_ids":[-1]*4,"integer_direction":[0]*4,
          "materialize_candidate":False}
  translated=dict(common,mode="translated",difference_table=diff,relation_of_difference=rel)
  full=dict(common,mode="matrix",relation_ids=matrix)
  (OUT/f"{name}_translated_frozen.json").write_text(json.dumps(translated,separators=(",",":"))+"\n")
  (OUT/f"{name}_matrix_frozen.json").write_text(json.dumps(full,separators=(",",":"))+"\n")
  free=dict(translated,constraint_group_ids=[-2]*4,
            expected_parent_fraction=EXPECTED[d,twist])
  (OUT/f"{name}_translated_free.json").write_text(json.dumps(free,separators=(",",":"))+"\n")
