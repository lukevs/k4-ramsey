"""Readable rational parameters, selected from the two-parameter profile."""
import json
from fractions import Fraction
from class_graphon import ROOT
OUT=ROOT/'reports/literature-simple-graphon-001'
def main():
    OUT.mkdir(exist_ok=False,parents=True);parent=ROOT/'reports/literature-two-parameter-001'
    old=json.loads((parent/'report.json').read_text());classes=json.loads((parent/'classes.json').read_text())
    den=41;a,b=32,22;n=len(classes)
    numerator=sum(c*(a if color==0 else den-a)**x*(b if color==0 else den-b)**y*den**(6-x-y)for color,x,y,c in old['profile'])
    denominator=den**6*n**4;value=Fraction(numerator,denominator)
    report=dict(parameters=[a,b],parameter_denominator=den,numerator=numerator,denominator=denominator,density=str(value),decimal=float(value),
      evidence='Exact profile evaluation; separate ordered-index audit required',hypothesis='Small-denominator readable representative below the announced decimal threshold',profile=old['profile'])
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'classes.json').write_text(json.dumps(classes)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
