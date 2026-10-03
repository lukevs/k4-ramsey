"""Thin JSON-to-native adapter for the relation signature engine."""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,time
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
SOURCE=HERE/"engine.cpp";BINARY=HERE/"engine"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def normalize(d):
    schema=d.get("schema")
    if schema=="relation-engine-input-v1":
        n=d["order"];q=d["denominator"];r=d["relation_count"];matrix=d["relation_ids"]
        p=d["parent_probability_numerators"];groups=[-1]*r
        variables=set(d.get("variable_relations",[]));frozen=set(d.get("frozen_relations",[]))
        if variables&frozen or variables|frozen!=set(range(r)):raise ValueError("variable/frozen partition")
        oriented=[0]*r
        for row in matrix:
            for relation in row:oriented[relation]+=1
        used=set()
        for row in d.get("neutral_constraint_rows",[]):
            support=[j for j,x in enumerate(row) if x]
            if not support or any(type(row[j]) is not int or row[j]<=0 for j in support):raise ValueError("constraint row coefficients")
            if used&set(support):raise ValueError("overlapping constraint rows unsupported")
            ratios={Fraction(row[j],oriented[j]) for j in support}
            if len(ratios)!=1:raise ValueError("constraint row not proportional to native relation mass")
            if support:
                used.update(support)
        # Safe first pass: exact gradient/Hessian only. The supplied neutral
        # rows are not activated until the consumer checks the exact parent
        # gradient relation and returns an explicit direction/config.
        direction=d.get("integer_direction",[0]*r)
        return dict(mode="matrix",n=n,q=q,r=r,matrix=matrix,p=p,groups=groups,direction=direction,
                    materialize=d.get("materialize_candidate",False),expected=d.get("expected_parent_fraction"),source_schema=schema,
                    deferred_constraint_rows=d.get("neutral_constraint_rows",[]))
    if schema!="relation-engine-config-v1":raise ValueError(f"unsupported schema {schema!r}")
    mode=d["mode"];n=d["n"];q=d["q"];r=d["relation_count"]
    answer=dict(mode=mode,n=n,q=q,r=r,p=d["probability_numerators"],groups=d.get("constraint_group_ids",[-1]*r),
                direction=d.get("integer_direction",[0]*r),materialize=d.get("materialize_candidate",False),
                expected=d.get("expected_parent_fraction"),source_schema=schema)
    if mode=="matrix":answer["matrix"]=d["relation_ids"]
    elif mode=="translated":answer.update(diff=d["difference_table"],rel=d["relation_of_difference"])
    else:raise ValueError("mode must be matrix or translated")
    return answer

def validate(x):
    n,r,q=x["n"],x["r"],x["q"]
    if not(1<=n<=256 and 1<=r<=512 and q>0):raise ValueError("bad dimensions")
    if len(x["p"])!=r or len(x["groups"])!=r or len(x["direction"])!=r:raise ValueError("vector length")
    if any(type(v)is not int or not 0<=v<=q for v in x["p"]):raise ValueError("probability")
    if any(type(v)is not int or v < -2 for v in x["groups"]):raise ValueError("constraint group id")
    if x["mode"]=="matrix":
        m=x["matrix"]
        if len(m)!=n or any(len(row)!=n for row in m):raise ValueError("matrix shape")
        if any(type(m[i][j])is not int or not 0<=m[i][j]<r or m[i][j]!=m[j][i] for i in range(n) for j in range(n)):raise ValueError("relation matrix")
    else:
        d=x["diff"]
        if len(d)!=n or any(len(row)!=n for row in d) or len(x["rel"])!=n:raise ValueError("translated shape")
        if any(type(d[i][j])is not int or not 0<=d[i][j]<n for i in range(n) for j in range(n)):raise ValueError("difference table")
        if any(type(v)is not int or not 0<=v<r for v in x["rel"]):raise ValueError("relation vector")

def fixture_text(x):
    mode=1 if x["mode"]=="matrix" else 0
    rows=[f"RELATION_ENGINE_V1 {mode} {x['n']} {x['r']} {x['q']}"]
    table=x["matrix"] if mode else x["diff"]
    rows.extend(" ".join(map(str,row)) for row in table)
    if not mode:rows.append(" ".join(map(str,x["rel"])))
    rows.extend((" ".join(map(str,x["p"]))," ".join(map(str,x["groups"]))," ".join(map(str,x["direction"]))))
    return "\n".join(rows)+"\n"

def materialize(x,probabilities):
    n=x["n"]
    if x["mode"]=="matrix":ids=x["matrix"]
    else:ids=[[x["rel"][x["diff"][i][j]] for j in range(n)] for i in range(n)]
    return {"schema":"rational-step-graphon-v1","block_weights":[1]*n,"edge_probability_denominator":x["q"],
            "red_probability_numerators":[[probabilities[ids[i][j]] for j in range(n)] for i in range(n)]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);config=args.config.resolve();raw=json.loads(config.read_text());x=normalize(raw);validate(x)
    fixture=out/"fixture.txt";fixture.write_text(fixture_text(x));native=out/"native-report.json"
    if x["materialize"] and x["expected"] is None:raise ValueError("materialized production run requires expected_parent_fraction")
    source_snapshot=out/"engine_snapshot.cpp";binary_snapshot=out/"engine_snapshot";adapter_snapshot=out/"run_snapshot.py"
    shutil.copy2(SOURCE,source_snapshot);shutil.copy2(BINARY,binary_snapshot);shutil.copy2(Path(__file__),adapter_snapshot)
    before={"config":sha(config),"fixture":sha(fixture),"source":sha(source_snapshot),"binary":sha(binary_snapshot),"adapter":sha(adapter_snapshot)}
    subprocess.run([str(binary_snapshot),str(fixture),str(native)],check=True,timeout=300)
    after={"config":sha(config),"fixture":sha(fixture),"source":sha(source_snapshot),"binary":sha(binary_snapshot),"adapter":sha(adapter_snapshot)}
    if before!=after:raise RuntimeError("input or executable snapshot changed during run")
    report=json.loads(native.read_text());fraction=Fraction(int(report["parent_numerator"]),int(report["parent_denominator"]))
    if x["expected"] is not None and fraction!=Fraction(x["expected"]):raise RuntimeError(f"expected parent {x['expected']} != {fraction}")
    report.update(config_path=str(config),config_sha256=before["config"],fixture_sha256=before["fixture"],engine_source_sha256=before["source"],engine_binary_sha256=before["binary"],
                  adapter_source_sha256=before["adapter"],source_schema=x["source_schema"],adapter_seconds=time.monotonic()-started,
                  expected_parent_bound=x["expected"] is not None,deferred_constraint_rows=x.get("deferred_constraint_rows",[]),
                  trust="Native exact relation-signature search evidence. Candidate promotion still requires a separate candidate-bound independent checker.")
    if x["materialize"]:
        candidate=out/"graphon-candidate.json";write(candidate,materialize(x,report["rounded_probabilities"]));report["candidate"]={"path":str(candidate),"sha256":sha(candidate),"order":x["n"],"unit_masses":True,"indexing":"input relation matrix order"}
    write(out/"report.json",report);print(json.dumps({k:report[k] for k in ("parent_decimal","constraint_dimension","hessian_min_eigenvalue_basis_coordinates","rounded_decimal","timings")},sort_keys=True))
if __name__=="__main__":main()
