import argparse,collections,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/literature-graphon-gradient-001'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',default='reports/literature-class-graphon-001');parser.add_argument('--out',default='reports/literature-graphon-gradient-001');args=parser.parse_args()
    OUT=ROOT/args.out
    OUT.mkdir(exist_ok=False,parents=True);start=time.monotonic()
    source=ROOT/'experiments/literature/graphon_gradient.cpp';binary=OUT/'gradient'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True)
    parent=ROOT/args.input;report=json.loads((parent/'report.json').read_text());classes=json.loads((parent/'classes.json').read_text())
    ps=[x/report['parameter_denominator']for x in report['parameters']];n=len(classes)
    matrix=[[0 if c==-1 else 1 if c==-2 else ps[c]for c in row]for row in classes]
    payload=str(n)+'\n'+'\n'.join(' '.join(map(str,r))for r in matrix)+'\n'
    result=subprocess.check_output([str(binary)],input=payload,text=True)
    records=[];groups=collections.defaultdict(list)
    for line in result.splitlines():
        i,j,g=line.split();i=int(i);j=int(j);g=float(g);c=classes[i][j]
        records.append(dict(i=i,j=j,gradient=g,probability=matrix[i][j],class_id=c));groups[c].append(g)
    summary={c:dict(min=min(gs),max=max(gs),mean=sum(gs)/len(gs),count=len(gs))for c,gs in groups.items()}
    improving=[r for r in records if (r['probability']==0 and r['gradient']<0)or(r['probability']==1 and r['gradient']>0)]
    out=dict(class_gradient_summary=summary,boundary_improving_coordinates=len(improving),seconds=time.monotonic()-start,
      evidence='Double-precision analytic derivative diagnostic, not candidate or certificate',strongest_boundary_directions=sorted(improving,key=lambda r:-abs(r['gradient']))[:20])
    (OUT/'report.json').write_text(json.dumps(out,indent=2)+'\n');(OUT/'gradients.json').write_text(json.dumps(records)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
