"""Materialize maximal k=6 Z3-orbit/F2-difference Cayley probabilities."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/"reports/quadratic-full-cayley-001";Q=65536
r=json.loads((OUT/"report.json").read_text());p=r["rationalized_parameters"]
m=[[p[((b-a)%3!=0)*64+(x^y)] for b in range(3) for y in range(64)] for a in range(3) for x in range(64)]
c={"schema":"rational-step-graphon-v1","block_weights":[1]*192,"edge_probability_denominator":Q,"red_probability_numerators":m}
path=OUT/"graphon-candidate.json";path.write_text(json.dumps(c,separators=(",",":"))+"\n")
meta={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"order":192,"indexing":"Z3-major then F2^6 integer","density":r["rationalized_density"],"exact_numerator":r["exact_numerator"],"exact_denominator":r["exact_denominator"]}
(OUT/"candidate-metadata.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n");print(json.dumps(meta,sort_keys=True))
