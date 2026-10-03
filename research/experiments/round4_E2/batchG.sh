#!/bin/bash
OUT=$1; mkdir -p $OUT; B=$(dirname $0)/nrpa_cayley_v2
run(){ echo -n "$* : " >> $OUT/summary.txt; $B "$@" >> $OUT/summary.txt; }
run 1 8 1 3 0 nrpa 160000 1 4 20 1.0 $OUT/f256_d3_L4
run 1 8 1 1 0 nrpa 160000 1 4 20 1.0 $OUT/f256_d1_L4
run 1 8 1 5 0 nrpa 160000 1 4 20 1.0 $OUT/f256_d5_L4
SEED_RED=$(dirname $0)/../../../reports/round4-E2-batchF-001/d5_L3.red SEED_BIAS=3 run 3 8 2 1 0 seeded 50000 1 2 100 1.0 $OUT/d1_seeded_from_d5
run 3 8 2 5 0 nrpa 160000 1 4 20 1.0 $OUT/d5_L4
echo DONE >> $OUT/summary.txt
