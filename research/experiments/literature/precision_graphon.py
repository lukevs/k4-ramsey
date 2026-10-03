import json,time
from fractions import Fraction
from class_graphon import Counter,ROOT
OUT=ROOT/'reports/literature-precision-graphon-001'
def main():
    OUT.mkdir(exist_ok=False,parents=True);start=time.monotonic();parent=ROOT/'reports/literature-refined-graphon-001'
    report=json.loads((parent/'report.json').read_text());classes=json.loads((parent/'classes.json').read_text());den=65536;n=len(classes)
    best=[x*16 for x in report['parameters']];counter=Counter(ROOT/'reports/literature-class-graphon-001/counter',classes,len(best));cache={};trials=[]
    def evaluate(x):
        key=tuple(x)
        if key not in cache:
            value=counter(den,x);cache[key]=value;trials.append(dict(parameters=list(x),numerator=value))
        return cache[key]
    assert Fraction(evaluate(best),den**6*n**4)==Fraction(report['density'])
    for step in [128,64,32,16,8,4,2,1]:
        for sweep in range(20):
            previous=list(best)
            for coordinate in range(1,len(best)):
                choices=[]
                for value in [best[coordinate]-step,best[coordinate],best[coordinate]+step]:
                    if 0<=value<=den:
                        x=list(best);x[coordinate]=value;choices.append((evaluate(x),x))
                best=min(choices)[1]
            if previous==best:break
    value=evaluate(best);counter.close();fraction=Fraction(value,den**6*n**4)
    result=dict(report,parameters=best,parameter_denominator=den,numerator=value,denominator=den**6*n**4,density=str(fraction),decimal=float(fraction),equivalent_768_numerator=str(fraction*768**4),trials=len(trials),seconds=time.monotonic()-start,hypothesis='Refine supported six-class stochastic graphon probabilities',evidence='Exact128-bit evaluation; no Lean certificate; independent ordered-index audit required')
    (OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'classes.json').write_text(json.dumps(classes)+'\n');(OUT/'trials.json').write_text(json.dumps(trials)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
