#!/bin/bash
# chain: class5 (960) from parent pullback -> class 8 (1920) warm start. Single-threaded, sequential.
set -e
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /Users/luke.vanseters/code/github.com/lukevs/k4-ramsey
R=reports/round4-E4-chain-001
timeout 200 uv run --with numpy --with scipy python research/experiments/round4_E4/opt2.py $R/c5 --cls 5 --starts 1 --sigma 0.05 --budget 150
timeout 390 uv run --with numpy --with scipy python research/experiments/round4_E4/opt2.py $R/c8 --cls 8 --from-cls 5 --from-x $R/c5/best_x.npy --starts 1 --sigma 0.02 --budget 300
