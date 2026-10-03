# Reproduction

Run from repository root with the existing cached environment:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 uv run --offline --with numpy --with scipy python experiments/family_mechanism_followup/run.py tiny
```

Use `run.py screen`, `check.py`, `exact_check.py`, and `decompose.py` in that
order for the remaining stages. These scripts are bounded by hard self-alarms
of 160 or 170 seconds and create no workers. For a rerun change the output
directory first: the original reports are immutable evidence, not a scratch
directory. One computational job per lane at a time.

`local_patch.py` supplies the weighted four-class objective and its derivatives.
`check.py` independently derives relative changes from endpoint multiplicities.
`exact_check.py` uses Python integers for that separate formula and recounts the
saved quantized patch. No global candidate file or incumbent is overwritten.

The exact relative count is conditional on the original first-layer baseline.
It is not an improvement to the depth-two incumbent or a novelty claim.
