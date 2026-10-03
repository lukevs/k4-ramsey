#!/bin/bash
# lns seed then fractional polish
R=$1; shift; T=$1; shift; IT=$1; shift
mkdir -p $R
for G in "$@"; do
  timeout 600 ./cay g/$G lns 1 18 $T $R/$G.lns.json 2>>$R/$G.log | sed "s/^/$G /" | tee -a $R/summary.txt
  python3 -c "import json;print(' '.join(map(str,json.load(open('$R/$G.lns.json'))['x'])))" > $R/$G.x0
  LR0=1e-2 LRD=1e-2 timeout 600 ./cay g/$G frac $R/$G.x0 $IT $R/$G.frac.json 1 0.05 2>>$R/$G.log | sed "s/^/$G /" | tee -a $R/summary.txt
done
