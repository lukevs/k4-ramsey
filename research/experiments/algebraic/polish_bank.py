"""Bounded two-job matched polish of predeclared structural seed representatives."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import time

from research.experiments.algebraic.lift import discover_fibers,decompose,half_blocks,materialize,materialize_half
from k4_ramsey.engine import ROOT,SEED,certificate,load
from k4_ramsey.lab import experiment,write_json


def selected_records(first,second):
    groups={}
    for index,r in enumerate(first['records']):
        family=r['family']
        if family=='random_voltage':
            if r['group']!='V4' or r['replace_probability']!=1.0: continue
            family='full_V4'
        key='phase1_'+family
        if key not in groups or r['numerator']<groups[key][2]['numerator']:
            groups[key]=(1,index,r)
    for index,r in enumerate(second['records']):
        key=f"phase2_{r['half_kind']}_{int(r['change_voltage'])}_{int(r['change_half'])}"
        if key not in groups or r['numerator']<groups[key][2]['numerator']:
            groups[key]=(2,index,r)
    return sorted(groups.items())


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--screen',type=Path)
    args=p.parse_args()
    args.out=args.out.resolve()
    args.out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    first_path=ROOT/'reports/pilot-algebraic-lift-001/search.json'
    second_path=ROOT/'reports/pilot-algebraic-lift-002/search.json'
    if args.screen:
        source_paths=(args.screen.resolve(),)
        source=json.loads(args.screen.read_text())
        selected=[(f"{r['group']}_{int(r['opposite'])}_{r['repetition']}",(3,index,r))
                  for index,r in enumerate(source['records'])]
    else:
        source_paths=(first_path,second_path)
        selected=selected_records(json.loads(first_path.read_text()),json.loads(second_path.read_text()))
    rows=load(SEED)['red_rows']
    fibers=discover_fibers(rows)
    blocks,_=decompose(rows,fibers)
    halves=half_blocks(rows,fibers)
    shutil.copy2(__file__,args.out/'source_snapshot.py')
    shutil.copy2(ROOT/'research/experiments/algebraic/lift.py',args.out/'lift_source_snapshot.py')
    config=dict(mode='star',per_color=16,max_moves=100000,checkpoint_moves=100)
    records=[]
    for number,(label,(phase,index,r)) in enumerate(selected):
        if args.screen:
            raw=load(Path(r['raw_path']))['red_rows']
        else:
            raw=materialize(rows,fibers,blocks,r['voltages'])
            raw=materialize_half(raw,fibers,halves,r.get('half_patterns',[p for _,_,p in halves]))
        path=args.out/f'raw-{number:02d}.json'
        write_json(path,certificate(raw))
        records.append(dict(case=number,label=label,phase=phase,source_record=index,
            input=str(path),input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            raw_numerator=r['numerator'],directory=str(args.out/f'polish-{number:02d}')))
    meta=dict(hypothesis='H-ALG-004',started_at=datetime.now(timezone.utc).isoformat(),
        prediction='Lift architecture and half-block shape influence polished basins; raw rank alone need not predict final rank',
        selection=('Every predefined anti-triangle/control assignment, without raw-score filtering' if args.screen else
                   'Minimum raw numerator in each of nine phase2 matched-factor groups, plus phase1 best global twist, constant voltage, full V4'),
        source_hashes={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths},
        strategy=str(ROOT/'src/k4_ramsey/strategies/fast_neighborhood.py'),config=config,
        seed=21,seconds=30,timeout=45,max_cpu_jobs=2,records=records)
    write_json(args.out/'selection.json',meta)
    def run(record):
        report=experiment(out=record['directory'],input_path=record['input'],strategy=meta['strategy'],
            hypothesis='H-ALG-004',prediction=meta['prediction'],seed=21,seconds=30,timeout=45,config=config)
        if report.get('baseline',{}).get('numerator')!=record['raw_numerator']:
            raise RuntimeError('Reconstruction or independently checked baseline mismatch')
        return report
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(run,r):r for r in records}
        for future in as_completed(futures):
            record=futures[future]
            try:
                report=future.result()
                record.update(status=report['status'],evidence=report['evidence'],
                    polished_numerator=report.get('verification',{}).get('numerator'),
                    candidate_sha256=report.get('candidate_sha256'),
                    actual_seconds=report.get('total_seconds'))
            except Exception as exc:
                record.update(status='failed',error=str(exc))
            print(json.dumps(record),flush=True)
            write_json(args.out/'progress.json',meta)
    meta['total_seconds']=time.monotonic()-started
    write_json(args.out/'report.json',meta)


if __name__=='__main__': main()
