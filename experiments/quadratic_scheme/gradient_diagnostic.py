"""Unrestricted off-diagonal box-KKT diagnostic for the k=6 candidate."""
import hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/"reports/quadratic-scheme-001"
candidate=OUT/"graphon-candidate.json";data=json.loads(candidate.read_text());q=data["edge_probability_denominator"];m=data["red_probability_numerators"];n=len(m)
payload=str(n)+"\n"+"\n".join(" ".join(str(x/q) for x in row) for row in m)+"\n"
binary=ROOT/"reports/literature-graphon-gradient-001/gradient";start=time.monotonic();text=subprocess.check_output([str(binary)],input=payload,text=True,timeout=30)
boundary=[];fractional=[];records=[]
for line in text.splitlines():
 i,j,g=line.split();i=int(i);j=int(j);g=float(g)
 v=m[i][j];r={"i":i,"j":j,"numerator":v,"gradient":g};records.append(r)
 if (v==0 and g<0) or (v==q and g>0):boundary.append(r)
 if 0<v<q and abs(g)>1e-12:fractional.append(r)
report={"schema":"quadratic-unrestricted-gradient-v1","candidate_sha256":hashlib.sha256(candidate.read_bytes()).hexdigest(),"symmetric_coordinates_including_diagonal":len(records),
 "boundary_violations":len(boundary),"strongest_boundary_violation_magnitude":max((abs(x["gradient"]) for x in boundary),default=0),
 "fractional_nonstationary":len(fractional),"strongest_fractional_gradient_magnitude":max((abs(x["gradient"]) for x in fractional),default=0),
 "strongest_boundary_violations":sorted(boundary,key=lambda x:-abs(x["gradient"]))[:50],"seconds":time.monotonic()-start,
 "evidence":"Double-precision unrestricted analytic derivative diagnostic; proposal guide only","gradient_binary_sha256":hashlib.sha256(binary.read_bytes()).hexdigest()}
(OUT/"gradient-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
(OUT/"gradients.json").write_text(json.dumps(records,separators=(",",":"))+"\n")
print(json.dumps({k:report[k] for k in ("boundary_violations","strongest_boundary_violation_magnitude","fractional_nonstationary","strongest_fractional_gradient_magnitude","seconds")},sort_keys=True))
