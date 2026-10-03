"""Materialize the retained k=6 nonsplit quadratic/Hamming relation."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"reports/quadratic-scheme-001"
Q=65536;K=6;M=1<<K

def qf(z):
    value=((z>>0)&1)^((z>>1)&1)
    for i in range(0,K,2): value^=((z>>i)&1)&((z>>(i+1))&1)
    return value

def rid(za,z): return (za!=0)*2*(K+1)+2*z.bit_count()+qf(z)

report=json.loads((OUT/"report.json").read_text())
p=report["rationalized_parameters"]
matrix=[[p[rid((b-a)%3,x^y)] for b in range(3) for y in range(M)] for a in range(3) for x in range(M)]
candidate={"schema":"rational-step-graphon-v1","block_weights":[1]*(3*M),
           "edge_probability_denominator":Q,"red_probability_numerators":matrix}
path=OUT/"graphon-candidate.json"
path.write_text(json.dumps(candidate,separators=(",",":"))+"\n")
(OUT/"matrix.txt").write_text(f"{3*M} {Q}\n"+"\n".join(" ".join(map(str,row)) for row in matrix)+"\n")
meta={"candidate_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"order":3*M,
      "indexing":"Z3-major then F2^6 integer", "quadratic_form":"nonsplit Arf-1",
      "density":report["rationalized_density"],"exact_numerator":report["rationalized_exact_numerator"],
      "exact_denominator":report["rationalized_exact_denominator"]}
(OUT/"candidate-metadata.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
print(json.dumps(meta,sort_keys=True))
