#!/bin/bash
OUT=$1; mkdir -p $OUT; B=$(dirname $0)/nrpa_cayley_v2
run(){ echo -n "$* : " >> $OUT/summary.txt; $B "$@" >> $OUT/summary.txt; }
SEED_RED=$(dirname $0)/../../reports/round4-E2-batchC-001/3_8_2_3_0_nrpa_s1.red SEED_BIAS=3 run 3 8 2 1 0 seeded 60000 1 2 100 1.0 $OUT/d1_seeded_s1
run 3 8 2 3 0 nrpa 60000 3 3 39 1.0 $OUT/d3_L3_s3
run 3 8 2 3 0 nrpa 60000 4 3 39 1.0 $OUT/d3_L3_s4
run 15 6 2 3 0 nrpa 60000 1 3 39 1.0 $OUT/z15f64_L3_s1
run 769 0 4 1 0 nrpa 60000 1 3 39 1.0 $OUT/z769_L3_s1
echo DONE >> $OUT/summary.txt
