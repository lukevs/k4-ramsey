import argparse,hashlib,json,subprocess,time
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[3]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);args=parser.parse_args()
    run=ROOT/args.input;report=json.loads((run/'report.json').read_text());classes=json.loads((run/'classes.json').read_text())
    den=report['parameter_denominator'];ps=report['parameters'];n=len(classes)
    matrix=[[0 if c==-1 else den if c==-2 else ps[c]for c in row]for row in classes]
    source=ROOT/'research/experiments/literature/ordered_graphon_check.cpp';binary=run/'ordered_counter'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True)
    payload=f'{n} {den}\n'+'\n'.join(' '.join(map(str,r))for r in matrix)+'\n';start=time.monotonic()
    red,blue,total=map(int,subprocess.check_output([str(binary)],input=payload,text=True,timeout=120).split())
    assert total==report['numerator'] and Fraction(total,den**6*n**4)==Fraction(report['density'])
    answer=dict(status='independent_ordered_index_exact_recount_passed',red=red,blue=blue,total=total,
      denominator=den**6*n**4,density=str(Fraction(total,den**6*n**4)),seconds=time.monotonic()-start,
      source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
      trust='Independent C++128-bit exhaustive ordered quadruples; no Lean proof or checker; graphon realization argument remains prose')
    (run/'graphon-candidate.json').write_text(json.dumps(dict(schema='rational-step-graphon-v1',block_weights=[1]*n,edge_probability_denominator=den,red_probability_numerators=matrix))+'\n')
    answer['candidate_sha256']=hashlib.sha256((run/'graphon-candidate.json').read_bytes()).hexdigest()
    (run/'independent-audit.json').write_text(json.dumps(answer,indent=2)+'\n');(run/'ordered_checker_snapshot.cpp').write_bytes(source.read_bytes())
    print(json.dumps(answer,indent=2))
if __name__=='__main__':main()
