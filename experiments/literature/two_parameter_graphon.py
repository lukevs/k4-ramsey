import json,subprocess,time
from fractions import Fraction as F
from class_graphon import ROOT,Counter
OUT=ROOT/'reports/literature-two-parameter-001'
def main():
    OUT.mkdir(exist_ok=False,parents=True);start=time.monotonic();parent=ROOT/'reports/literature-precision-graphon-001'
    classes=json.loads((parent/'classes.json').read_text());classes=[[(-2 if c==0 else 1 if c==4 else 0)if c>=0 else c for c in r]for r in classes]
    source=ROOT/'experiments/literature/two_parameter_profile.cpp';binary=OUT/'profile'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True)
    payload=str(len(classes))+'\n'+'\n'.join(' '.join(map(str,r))for r in classes)+'\n'
    profile=[list(map(int,line.split()))for line in subprocess.check_output([str(binary)],input=payload,text=True).splitlines()]
    den=65536;n=len(classes);cache={}
    def count(x):
        key=tuple(x)
        if key not in cache:
            total=0
            for color,p,h,c in profile:
                a,b=x if color==0 else [den-x[0],den-x[1]]
                total+=c*a**p*b**h*den**(6-p-h)
            cache[key]=total
        return cache[key]
    best=[51064,35014]
    for step in [256,128,64,32,16,8,4,2,1]:
        for rep in range(100):
            previous=list(best)
            for coordinate in [0,1]:
                choices=[]
                for value in [best[coordinate]-step,best[coordinate],best[coordinate]+step]:
                    if 0<=value<=den:
                        x=list(best);x[coordinate]=value;choices.append((count(x),x))
                best=min(choices)[1]
            if previous==best:break
    numerator=count(best);counter=Counter(ROOT/'reports/literature-class-graphon-001/counter',classes,2)
    assert counter(den,best)==numerator;counter.close();fraction=F(numerator,den**6*n**4)
    answer=dict(parameters=best,parameter_denominator=den,numerator=numerator,denominator=den**6*n**4,
      density=str(fraction),decimal=float(fraction),profile=profile,trials=len(cache),seconds=time.monotonic()-start,
      evidence='Exact two-variable polynomial from independent tuple-pattern histogram, agrees with partitioncounter; noLean')
    (OUT/'report.json').write_text(json.dumps(answer,indent=2)+'\n');(OUT/'classes.json').write_text(json.dumps(classes)+'\n')
    print(json.dumps(answer,indent=2))
if __name__=='__main__':main()
