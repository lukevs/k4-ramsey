"""Materialize the retained k=6 Witt-pair refined rational point."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/"reports/quadratic-next-002";Q=65536
def mi(a,b):
 if a>b:a,b=b,a
 return [(x,y) for x in range(4) for y in range(x,4)].index((a,b))
def rid(za,z):return (za!=0)*40+(z&3)*10+mi((z>>2)&3,(z>>4)&3)
r=json.loads((OUT/"report.json").read_text());p=r["rationalized_parameters"]
m=[[p[rid((b-a)%3,x^y)] for b in range(3) for y in range(64)] for a in range(3) for x in range(64)]
c={"schema":"rational-step-graphon-v1","block_weights":[1]*192,"edge_probability_denominator":Q,"red_probability_numerators":m}
path=OUT/"graphon-candidate.json";path.write_text(json.dumps(c,separators=(",",":"))+"\n")
meta={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"order":192,"indexing":"Z3-major then F2^6 integer","density":r["rationalized_density"],"exact_numerator":r["exact_numerator"],"exact_denominator":r["exact_denominator"]}
(OUT/"candidate-metadata.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n");print(json.dumps(meta,sort_keys=True))
