"""Refine probability classes by gradient evidence, retaining exact evaluation."""
import argparse,collections,hashlib,json,time
from fractions import Fraction
from pathlib import Path
from class_graphon import Counter,ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=ROOT/args.out;out.mkdir(exist_ok=False,parents=True);start=time.monotonic()
    parent=ROOT/'reports/literature-class-graphon-001';report=json.loads((parent/'report.json').read_text());n=192;den=4096
    records=json.loads((ROOT/'reports/literature-graphon-gradient-001/gradients.json').read_text())
    classes=[[-1]*n for _ in range(n)];keys={};initial=[];counts=collections.Counter()
    for r in records:
        i,j,c,g=r['i'],r['j'],r['class_id'],r['gradient']
        if c==-1 or c==3:label=-1
        elif c==-2 and g<=0:label=-2
        else:
            key=(c,round(g,5))
            if key not in keys:keys[key]=len(keys);initial.append(round(r['probability']*den))
            label=keys[key];counts[label]+=1
        classes[i][j]=classes[j][i]=label
    counter=Counter(parent/'counter',classes,len(initial));cache={};trials=[]
    def evaluate(x):
        key=tuple(x)
        if key not in cache:
            value=counter(den,x);cache[key]=value;trials.append(dict(parameters=list(x),numerator=value))
        return cache[key]
    assert Fraction(evaluate(initial),den**6*n**4)==Fraction(report['density'])
    best=list(initial)
    for step in [512,256,128,64,32,16,8,4,2,1]:
        for sweep in range(20):
            old=list(best)
            for coordinate in range(len(best)):
                candidates=[]
                for value in sorted(set([best[coordinate],max(0,best[coordinate]-step),min(den,best[coordinate]+step)])):
                    x=list(best);x[coordinate]=value;candidates.append((evaluate(x),x))
                best=min(candidates)[1]
            if best==old:break
    numerator=evaluate(best);counter.close();denominator=den**6*n**4
    answer=dict(hypothesis='Free boundary-unstable full blocks and split heterogeneous defect gradients',
      parameters=best,parameter_denominator=den,initial_parameters=initial,class_keys=[list(k)for k in keys],class_counts=dict(counts),
      numerator=numerator,denominator=denominator,density=str(Fraction(numerator,denominator)),decimal=float(Fraction(numerator,denominator)),
      equivalent_768_numerator=str(Fraction(numerator*768**4,denominator)),trials=len(trials),seconds=time.monotonic()-start,
      evidence='Exact128-bit class search; kernel tiny-audited in parentrun; gradient used only for hypothesis selection; no Lean certificate')
    (out/'report.json').write_text(json.dumps(answer,indent=2)+'\n');(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
    (out/'classes.json').write_text(json.dumps(classes)+'\n');(out/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(answer,indent=2))
if __name__=='__main__':main()
