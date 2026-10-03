"""Enumerate the exact point stabilizer of the colored 192 quotient."""

from collections import Counter
import json
from pathlib import Path
import time

from experiments.group_recovery.refinement_diagnostic import relation_matrix, refine
from experiments.group_recovery.recover_quotient import BASE, CORE, QUOTIENT, verify


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/group-recovery-stabilizer-001"


def recover_all(rel, target_root, source_colors):
    n = len(rel)
    answers = []
    nodes = 0

    def visit(prefix):
        nonlocal nodes
        nodes += 1
        depth = len(prefix)
        colors = refine(rel, prefix)
        expected = source_colors[depth]
        if Counter(colors) != Counter(expected):
            return
        if depth == len(BASE):
            if len(set(colors)) != n:
                return
            inverse = {color: vertex for vertex, color in enumerate(colors)}
            permutation = tuple(inverse[color] for color in expected)
            if verify(rel, permutation):
                answers.append(permutation)
            return
        wanted = expected[BASE[depth]]
        for candidate, color in enumerate(colors):
            if color == wanted and candidate not in prefix:
                visit(prefix + (candidate,))

    visit((target_root,))
    return sorted(set(answers)), nodes


def permutation_order(permutation):
    identity = tuple(range(len(permutation)))
    power = identity
    for order in range(1, 10000):
        power = tuple(permutation[power[i]] for i in range(len(permutation)))
        if power == identity:
            return order
    raise RuntimeError("unexpected order")


def main():
    started = time.monotonic()
    rows = json.loads(CORE.read_text())["red_rows"]
    fibers = json.loads(QUOTIENT.read_text())["fibers"]
    rel = relation_matrix(rows, fibers)
    source_colors = [None] * (len(BASE) + 1)
    for depth in range(1, len(BASE) + 1):
        source_colors[depth] = refine(rel, BASE[:depth])
    stabilizer, nodes = recover_all(rel, 0, source_colors)
    orders = Counter(permutation_order(p) for p in stabilizer)
    OUT.mkdir(parents=True, exist_ok=False)
    path = OUT / "stabilizer.json"
    path.write_text(json.dumps(stabilizer, separators=(",", ":")) + "\n")
    report = {"schema":"colored-quotient-point-stabilizer-v1",
              "status":"exact_point_stabilizer_enumerated",
              "order":len(stabilizer), "nodes":nodes,
              "element_order_distribution":dict(sorted(orders.items())),
              "seconds":time.monotonic()-started,
              "verification":"IR base is discrete; every leaf is a full permutation and is checked on all 192^2 colored relation entries. Exhaustive branching over every compatible image of each base point enumerates the point stabilizer.",
              "scope":"Point stabilizer only; regular subgroup search remains separate."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__ == "__main__": main()
