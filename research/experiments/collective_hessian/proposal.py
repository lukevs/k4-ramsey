"""Thin driver for the full 1,248-coordinate collective Hessian proposal."""

import hashlib,json,math,os,shutil,subprocess,time
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/"reports/literature-two-parameter-001/graphon-candidate.json"
SOURCE=Path(__file__).with_name("proposal.cpp")
OUT=ROOT/"reports/collective-hessian-proposal-006"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def payload(matrix,q):return f"{len(matrix)} {q}\n"+"\n".join(" ".join(map(str,row)) for row in matrix)+"\n"

def main():
 started=time.monotonic();record=json.loads(PARENT.read_text());p=record["red_probability_numerators"];q=record["edge_probability_denominator"]
 OUT.mkdir(parents=True,exist_ok=False);source_snapshot=OUT/"proposal.cpp";driver_snapshot=OUT/"proposal.py";shutil.copy2(SOURCE,source_snapshot);shutil.copy2(Path(__file__),driver_snapshot);binary=OUT/"proposal";subprocess.run(["/usr/bin/clang++","-O3","-std=c++17","-DACCELERATE_NEW_LAPACK",str(source_snapshot),"-framework","Accelerate","-o",str(binary)],check=True)
 thread_env={"VECLIB_MAXIMUM_THREADS":"1","OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"};run_env=os.environ.copy();run_env.update(thread_env)
 ran=time.monotonic();raw=subprocess.check_output([str(binary)],input=payload(p,q),text=True,timeout=300,env=run_env);compute=time.monotonic()-ran
 lines=raw.splitlines();head=lines[0].split();m,classes=int(head[0]),int(head[1]);assert len(lines)==m+1
 edges=[];members=defaultdict(list)
 for index,line in enumerate(lines[1:]):
  i,j,value,cls,gradient,direction=line.split();item={"i":int(i),"j":int(j),"p":int(value),"class":int(cls),"gradient":gradient,"direction":float(direction)};edges.append(item);members[item["class"]].append(index)
 assert m==1248 and len(members)==classes
 class_records=[]
 for cls,indices in sorted(members.items()):
  gradients={edges[e]["gradient"] for e in indices};assert len(gradients)==1
  class_records.append({"class":cls,"size":len(indices),"gradient":next(iter(gradients)),"probability_counts":dict(Counter(edges[e]["p"] for e in indices))})
 direction=[edge["direction"] for edge in edges]
 class_residual=max(abs(sum(direction[e] for e in indices)) for indices in members.values())
 report={"schema":"collective-fractional-hessian-proposal-v1","status":"negative_mode_proposed" if float(head[4])<0 else "no_negative_mode_proposed",
  "parent":str(PARENT.relative_to(ROOT)),"parent_sha256":sha(PARENT),"variables":m,"exact_gradient_classes":class_records,
  "symmetry_residual":float(head[2]),"row_sum_bound_twice":float(head[3]),"minimum_rayleigh":float(head[4]),"eigen_residual":float(head[5]),"selected_eigen_index":int(head[6]),"eigensystem_dimension":int(head[7]),"smallest_projected_eigenvalues":[float(x) for x in head[13:]],
  "exact_gradient_bound":head[8],"normalized_gradient_dot_residual":float(head[9]),"projector_gradient_annihilation_residual":float(head[10]),"projector_idempotence_residual":float(head[11]),"projected_matrix_symmetry_residual":float(head[12]),"diagnostic_class_sum_residual":class_residual,"edges":edges,
  "tiny_controls":"Exact formula (12 Adj + 3 Dis) equals literal ordered-quadruple c2 on n=2 diagonal/repeat, n=3 adjacent +/- and n=4 disjoint fixtures; complement control passed. The separate production-style dense incidence assembly matches literal c2 on three deterministic off-diagonal directions for each tiny fixture, including repeated tuple indices.",
  "source_sha256":sha(source_snapshot),"driver_sha256":sha(driver_snapshot),"binary_sha256":sha(binary),"thread_environment":thread_env,"compute_seconds":compute,"setup_to_gate_seconds":time.monotonic()-started,
  "scope":"Full dense symmetric LAPACK eigensolve of P C P on all 1248 coordinates, with P orthogonal to the complete exact gradient vector. Numerical spectral evidence on the full 1247-dimensional first-order-neutral tangent only, not an exact PSD certificate."}
 (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps({k:report[k] for k in ("status","variables","exact_gradient_classes","symmetry_residual","minimum_rayleigh","eigen_residual","normalized_gradient_dot_residual","projector_idempotence_residual","compute_seconds","setup_to_gate_seconds")},sort_keys=True))

if __name__=="__main__":main()
