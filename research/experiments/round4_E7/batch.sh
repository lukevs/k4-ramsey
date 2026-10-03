#!/bin/bash
# sequential single-threaded batch: lns vs flip (matched time), then fractional polish of lns seed
R=$1; shift; T=$1; shift; IT=$1; shift
mkdir -p $R
for G in "$@"; do
  timeout 600 ./cay g/$G lns 1 18 $T $R/$G.lns.json 2>>$R/$G.log | tee -a $R/summary.txt
  timeout 600 ./cay g/$G flip 1 1 $T $R/$G.flip.json 2>>$R/$G.log | tee -a $R/summary.txt
  python3 -c "import json;print(' '.join(map(str,json.load(open('$R/$G.lns.json'))['x'])))" > $R/$G.x0
  timeout 600 ./cay g/$G frac $R/$G.x0 $IT $R/$G.frac.json 1 0.05 2>>$R/$G.log | sed "s/^/$G /" | tee -a $R/summary.txt
done
