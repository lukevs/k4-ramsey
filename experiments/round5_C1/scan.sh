#!/bin/sh
# sequential level scan of the SDP ceiling
for PH in "0.7791808266653855 0.5342650498652971" "0.77 0.534265" "0.79 0.534265" "0.779181 0.51" "0.779181 0.56" "0.76 0.52" "0.80 0.55"; do
  set -- $PH; d=../../reports/round5-C1-scan-002/p$1_h$2; mkdir -p $d
  P=$1 H=$2 uv run --with cvxpy --with numpy --with scipy python sdp2.py $d | grep -E '"(p|h|F_base|gain_ceiling|F_floor)"' | tr -d '\n'; echo
done
