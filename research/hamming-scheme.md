# Randomized Z3 x F2^k Hamming-shell screen

Date: 2026-09-27. This tests M-ADJ-1 from
`research/adjacent-structural-mechanisms.md`. It is a strict association-scheme
subfamily and does not contain arbitrary PPSS Cayley generators.

For each difference `(a,z)`, the red probability depends only on whether
`a=0` and on the Hamming weight of `z`, giving `2(k+1)` variables. Translation
fixes the first of four coarse samples. Counts of the eight binary coordinate
columns `(u_r,v_r,w_r)` give an exact census with
`27*binom(k+7,7)` states and normalization `27*8^k`. Repeated relation bins
remain repeated factors; `q[0,0]` is the within-class fine-edge probability.

The census exactly matched literal enumeration for `k=0,1,2,3`, including
all repeated-index cases and a rational objective check. At `k=8`, 173,745
census states aggregate to only 3,662 six-relation multisets. This compression
made the dependency-free pure-Python gradient evaluator adequate: census build
took 0.127 seconds, each 600-step projected-Adam start took 3.87--4.01 seconds,
and all 15 starts over `k=6,7,8` completed in 37.99 seconds.

No tested basin was competitive. The best densities were

    k=6  0.03125002044584832
    k=7  0.03125002044584978
    k=8  0.03125002044584976.

They are near the constant-random value `1/32` and far above the current
approximately `0.0301389044224` construction. Other starts ended between
approximately 0.031251 and 0.031256. Therefore no rational point was produced
or sent for independent checking.

The first attempt, `reports/hamming-scheme-001`, failed before building any
state because NumPy/SciPy were unavailable. The successful dependency-free
run is `reports/hamming-scheme-002`. Its copied preregistration incorrectly
retained the originally planned label “L-BFGS-B,” although the run records and
source use projected Adam; `correction.json` preserves that metadata correction
without rewriting evidence. Its stored comparison also names the then-weaker
S3 candidate; using the stronger final comparison does not change rejection.

The historical Franek--Rödl control required a separate `k=10` run.  The first
control in `reports/hamming-scheme-k10-001` incorrectly made distance zero
blue; it is retained as a blue-diagonal variant, not as a reproduction of the
paper.  The corrected red-clique blow-up in
`reports/hamming-scheme-k10-002` sets both Z3 rows to red at distance zero and
uses the shell set `{1,3,4,7,8,10}` at positive distances.  Its exact density is

    32765943 / 1073741824 = 0.030515662394464016...

and hence `32F = 0.9765011966...`, agreeing with the paper's rounded
`0.976501`.  This is a strong end-to-end validation of the census.  One
700-step projected-Adam trajectory from that exact historical basin reached
`0.030504819428485975` numerically, still far above the current
`0.0301389044224` construction, so it was not rationalized or admitted.

Decision: retire only the tested starts and trajectories, including the
correct historical `k=10` basin.  The planned shell projection of a strong PPSS
core was not executed because no compatible labeling/projection was available;
the `k=6,7,8` screen therefore does not falsify that proposed direction.  These
results are also not evidence against other basins in the uniform shell family,
quadratic-form/code-syndrome refinements, unequal masses, or general structured
stochastic graphons.
