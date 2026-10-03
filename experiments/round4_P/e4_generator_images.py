"""Emit E4 coset-action generator images as plain JSON permutations (data only;
round4-P verifies them independently against the candidate matrix)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from experiments.round4_E4.coset_action import Base, CosetAction
report, out = Path(sys.argv[1]), Path(sys.argv[2])
K = json.loads(report.read_text())["K"]
b = Base(); A = CosetAction(b, K)
pts = np.arange(A.n)
perms = [A.act_G(g, pts).tolist() for g in b.gens]
out.write_text(json.dumps(dict(n=A.n, K=K, generators=perms)) + "\n")
print(A.n, len(perms))
