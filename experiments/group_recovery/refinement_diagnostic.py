"""Individualization/refinement diagnostic for the exact colored 192 quotient."""

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "data/published_cayley_768.json"
QUOTIENT = ROOT / "reports/pilot-algebraic-lift-001/quotient.json"


def relation_matrix(rows, fibers):
    n = len(fibers)
    rel = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            degree = sum(rows[u][v] == "1" for u in fibers[i] for v in fibers[j]) // 4
            rel[i][j] = rel[j][i] = degree
    return rel


def refine(rel, individualized):
    n = len(rel)
    colors = [len(individualized)] * n
    for color, vertex in enumerate(individualized):
        colors[vertex] = color
    while True:
        count = max(colors) + 1
        signatures = []
        for u in range(n):
            histogram = Counter((colors[v], rel[u][v]) for v in range(n) if v != u)
            signatures.append((colors[u], tuple(sorted(histogram.items()))))
        palette = {signature: color for color, signature in enumerate(sorted(set(signatures)))}
        changed = [palette[signature] for signature in signatures]
        if changed == colors:
            return colors
        colors = changed


def sizes(colors):
    return sorted(Counter(colors).values(), reverse=True)


def main():
    rows = json.loads(CORE.read_text())["red_rows"]
    fibers = json.loads(QUOTIENT.read_text())["fibers"]
    rel = relation_matrix(rows, fibers)
    rooted = refine(rel, [0])
    root_sizes = sizes(rooted)
    base = [0]
    stages = []
    while sizes(refine(rel, base))[0] > 1:
        anchors = []
        for anchor in range(len(rel)):
            if anchor in base:
                continue
            coloring = refine(rel, base + [anchor])
            cell_sizes = sizes(coloring)
            anchors.append({"anchor": anchor, "relation_to_root": rel[0][anchor],
                            "cells": len(cell_sizes), "max_cell": cell_sizes[0],
                            "nonsingletons": sum(size > 1 for size in cell_sizes)})
        best = min(anchors, key=lambda record: (record["max_cell"], record["nonsingletons"], -record["cells"], record["anchor"]))
        base.append(best["anchor"])
        stages.append(best)
    print(json.dumps({"root_cells": len(root_sizes), "root_max_cell": root_sizes[0],
                      "root_cell_sizes": root_sizes, "greedy_base": base,
                      "stages": stages},
                     sort_keys=True))


if __name__ == "__main__":
    main()
