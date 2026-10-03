"""Fast regression checks for the frozen relation engine and adapter."""
from __future__ import annotations
import argparse,itertools,json,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
ENGINE=HERE/"engine";RUN=HERE/"run.py"

def fixture(mode,n,r,q,table,p,groups=None,direction=None,rel=None):
    rows=[f"RELATION_ENGINE_V1 {mode} {n} {r} {q}"]
    rows.extend(" ".join(map(str,row)) for row in table)
    if mode==0:rows.append(" ".join(map(str,rel)))
    rows.extend((" ".join(map(str,p))," ".join(map(str,groups or [-1]*r))," ".join(map(str,direction or [0]*r))))
    return "\n".join(rows)+"\n"

def call(text,tmp,name="case"):
    inp=tmp/f"{name}.txt";out=tmp/f"{name}.json";inp.write_text(text)
    p=subprocess.run([str(ENGINE),str(inp),str(out)],capture_output=True,text=True)
    return p,out

def literal(matrix,p,q):
    total=0
    for v in itertools.product(range(len(matrix)),repeat=4):
        red=blue=1
        for i,j in itertools.combinations(range(4),2):
            x=p[matrix[v[i]][v[j]]];red*=x;blue*=q-x
        total+=red+blue
    return total

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--skip-replays",action="store_true");args=ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td);matrix=[[0,1],[1,0]];p=[1,3];q=5
        proc,out=call(fixture(1,2,2,q,matrix,p),tmp,"tiny")
        assert proc.returncode==0,proc.stderr
        report=json.loads(out.read_text());assert int(report["parent_numerator"])==literal(matrix,p,q)
        assert report["controls"].startswith("internal tiny literal exact objective/gradient/Hessian")

        proc,_=call("RELATION_ENGINE_V1 1 2 2 5\n0 1\n",tmp,"truncated")
        assert proc.returncode!=0 and "short table" in proc.stderr

        asymmetric=[[0,1],[0,0]]
        proc,_=call(fixture(1,2,2,5,asymmetric,p),tmp,"asymmetric")
        assert proc.returncode!=0 and "asymmetric" in proc.stderr

        n=256;overflow=[[0]*n for _ in range(n)]
        proc,_=call(fixture(1,n,1,10**9,overflow,[1]),tmp,"overflow")
        assert proc.returncode!=0 and "exact bound overflow" in proc.stderr

        if not args.skip_replays:
            expected=[
                ("quadratic80","16901897618722474829755212952533952"),
                ("quadratic128","16901715161505423885044215944464856"),
            ]
            for name,numerator in expected:
                outdir=tmp/name
                subprocess.run(["python3",str(RUN),"--config",str(HERE/"configs"/f"{name}.json"),"--out",str(outdir)],check=True,capture_output=True,text=True)
                replay=json.loads((outdir/"report.json").read_text())
                assert replay["parent_numerator"]==numerator
                assert replay["expected_parent_bound"] is True
    print("relation engine regression: PASS")
if __name__=="__main__":main()
