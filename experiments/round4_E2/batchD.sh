#!/bin/bash
OUT=$1; mkdir -p $OUT; B=$(dirname $0)/nrpa_cayley
run(){ echo -n "$* : " >> $OUT/summary.txt; $B "$@" >> $OUT/summary.txt; }
run 3 8 2 3 0 nrpa 160000 1 4 20 1.0 $OUT/d3_L4_s1
run 3 8 2 1 0 nrpa 60000 1 3 39 1.0 $OUT/d1_L3_s1
run 3 8 2 3 0 nrpa 60000 2 3 39 1.0 $OUT/d3_L3_s2
run 3 8 2 1 1 nrpa 60000 1 3 39 1.0 $OUT/frob_L3_s1
echo DONE >> $OUT/summary.txt
