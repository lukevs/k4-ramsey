#!/bin/bash
OUT=$1; mkdir -p $OUT; B=$(dirname $0)/nrpa_cayley_v2
run(){ echo -n "$* : " >> $OUT/summary.txt; $B "$@" >> $OUT/summary.txt; }
run 3 8 2 3 0 greedy 60000 2 3 39 1.0 $OUT/d3_greedy_s2
run 3 8 2 3 0 random 60000 2 3 39 1.0 $OUT/d3_random_s2
run 1 8 1 3 0 nrpa 60000 1 3 39 1.0 $OUT/f256_d3_L3
run 3 8 2 5 0 nrpa 60000 1 3 39 1.0 $OUT/d5_L3
run 3 8 2 15 0 nrpa 60000 1 3 39 1.0 $OUT/d15_L3
run 9 6 2 3 0 nrpa 60000 1 3 39 1.0 $OUT/z9f64_L3
echo DONE >> $OUT/summary.txt
