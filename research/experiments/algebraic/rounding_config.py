import json
from pathlib import Path
from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json

if __name__=='__main__':
    report=ROOT/'reports/literature-precision-graphon-001'
    info=json.loads((report/'report.json').read_text())
    q=json.loads((ROOT/'reports/pilot-algebraic-lift-001/quotient.json').read_text())
    write_json(ROOT/'research/experiments/algebraic/rounding.json',dict(fibers=q['fibers'],
        classes=json.loads((report/'classes.json').read_text()),parameters=info['parameters'],
        denominator=info['parameter_denominator'],source=str(report)))
