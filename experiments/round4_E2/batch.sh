#!/bin/bash
# usage: batch.sh outdir budget "cfg1;cfg2;..."  cfg = "m k dZ dF frob"
OUT=$1; B=$2; CFGS=$3; LEVEL=${4:-2}; NIT=${5:-100}
mkdir -p $OUT; BIN=$(dirname $0)/nrpa_cayley
IFS=';' read -ra A <<< "$CFGS"
for c in "${A[@]}"; do
  tag=$(echo $c | tr ' ' '_')
  for mode in ${MODES:-nrpa random greedy}; do
    for seed in 1; do
      echo -n "$tag $mode s$seed: " >> $OUT/summary.txt
      $BIN $c $mode $B $seed $LEVEL $NIT 1.0 $OUT/${tag}_${mode}_s$seed >> $OUT/summary.txt
    done
  done
done
echo DONE >> $OUT/summary.txt
