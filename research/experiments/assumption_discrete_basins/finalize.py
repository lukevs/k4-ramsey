import json,hashlib,time,subprocess
from pathlib import Path
root=Path('reports/assumption-discrete_basins-001');rows=[]
for p in sorted(root.glob('*.json')):
 d=json.loads(p.read_text())
 if 'best_rooted_count' in d or 'best_count' in d:
  count=d.get('best_count',d.get('best_rooted_count'));rows.append(dict(path=str(p),count=count,denominator=d['denominator'],density=count/d['denominator'],seconds=d['seconds'],seed=d['seed'],mode=d['mode'],initialization=d['initialization'],steps=d['steps'],accepted=d['accepted'],uphill=d['uphill']))
(root/'summary.json').write_text(json.dumps(dict(completed_utc=time.strftime('%FT%TZ',time.gmtime()),incumbent=0.030138887566497220,constant=1/32,results=rows),indent=2))
for r in rows:print(Path(r['path']).stem,format(r['density'],'.15f'),r['seconds'])
paths=list(Path('research/experiments/assumption_discrete_basins').glob('*'))+list(root.glob('*'))
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and p.name!='manifest-final.json'}
(root/'manifest-final.json').write_text(json.dumps(manifest,indent=2))
