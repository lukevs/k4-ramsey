"""Convert our own Sage pickle to portable data, without any product tables."""
import sys, pickle, json
from pathlib import Path
from sage.all import *

source=Path(sys.argv[1]); c=pickle.loads(source.read_bytes())
blocks=[]
for (key,flags),Q in zip(c['typed flags'].items(),c['X matrices']):
    blocks.append(dict(key=key,flags=flags,Q=[float(x) for x in Q]))
out=dict(target_size=int(c['target size']),maximize=bool(c['maximize']),
         positives=c['positives'],graphs=c['base flags'],blocks=blocks)
Path(sys.argv[2]).write_text(json.dumps(out,default=int)+'\n')
print('Exported',len(blocks),'blocks and',len(out['graphs']),'graphs')
