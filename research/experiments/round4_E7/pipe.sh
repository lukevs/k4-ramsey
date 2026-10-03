#!/bin/bash
# seed pipeline: lns (seed S) on symmetric group G, frac, print
R=$1; G=$2; S=$3; T=$4
mkdir -p $R
timeout 600 ./cay g/$G lns $S 18 $T $R/$G.s$S.lns.json 2>>$R/$G.s$S.log | sed "s/^/$G s$S /" | tee -a $R/summary.txt
python3 -c "import json;print(' '.join(map(str,json.load(open('$R/$G.s$S.lns.json'))['x'])))" > $R/$G.s$S.x0
LR0=1e-2 LRD=1e-2 timeout 600 ./cay g/$G frac $R/$G.s$S.x0 1500 $R/$G.s$S.frac.json 1 0.05 2>>$R/$G.s$S.log | sed "s/^/$G s$S /" | tee -a $R/summary.txt
