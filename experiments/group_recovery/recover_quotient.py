"""Recover exact color-preserving automorphisms of the 192-fiber quotient."""

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import time

from experiments.group_recovery.refinement_diagnostic import relation_matrix, refine


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "data/published_cayley_768.json"
QUOTIENT = ROOT / "reports/pilot-algebraic-lift-001/quotient.json"
BASE = (0, 18, 4, 3, 7)
OUT = ROOT / "reports/group-recovery-quotient-001"


def verify(rel, permutation):
    n = len(rel)
    return sorted(permutation) == list(range(n)) and all(
        rel[permutation[i]][permutation[j]] == rel[i][j]
        for i in range(n) for j in range(n)
    )


def recover(rel, target_root, source_colors):
    n = len(rel)
    nodes = 0

    def visit(prefix):
        nonlocal nodes
        nodes += 1
        depth = len(prefix)
        colors = refine(rel, prefix)
        expected = source_colors[depth]
        if Counter(colors) != Counter(expected):
            return None
        if depth == len(BASE):
            if len(set(colors)) != n:
                return None
            inverse = {color: vertex for vertex, color in enumerate(colors)}
            permutation = tuple(inverse[color] for color in expected)
            return permutation if verify(rel, permutation) else None
        source_vertex = BASE[depth]
        wanted = expected[source_vertex]
        for candidate, color in enumerate(colors):
            if color == wanted and candidate not in prefix:
                answer = visit(prefix + (candidate,))
                if answer is not None:
                    return answer
        return None

    answer = visit((target_root,))
    return answer, nodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=192)
    args = parser.parse_args()
    rows = json.loads(CORE.read_text())["red_rows"]
    fibers = json.loads(QUOTIENT.read_text())["fibers"]
    rel = relation_matrix(rows, fibers)
    source_colors = [None] * (len(BASE) + 1)
    for depth in range(1, len(BASE) + 1):
        source_colors[depth] = refine(rel, BASE[:depth])
    assert len(set(source_colors[-1])) == len(rel)
    started = time.monotonic()
    records = []
    permutations = []
    for target in range(min(args.limit, len(rel))):
        tick = time.monotonic()
        permutation, nodes = recover(rel, target, source_colors)
        records.append({"target": target, "found": permutation is not None,
                        "nodes": nodes, "seconds": time.monotonic() - tick})
        if permutation is not None:
            assert permutation[0] == target
            permutations.append(permutation)
    summary = {"targets": len(records), "found": len(permutations),
                      "nodes": sum(record["nodes"] for record in records),
                      "seconds": time.monotonic()-started,
                      "worst_seconds": max(record["seconds"] for record in records),
                      "failed": [record["target"] for record in records if not record["found"]],
                      "sample_orders": []}
    if args.limit == len(rel) and len(permutations) == len(rel):
        group = {permutation: index for index, permutation in enumerate(permutations)}
        assert len(group) == len(rel)
        identity = tuple(range(len(rel)))
        assert identity in group
        closed = True
        commutative = True
        for left in permutations:
            for right in permutations:
                lr = tuple(left[right[i]] for i in range(len(rel)))
                rl = tuple(right[left[i]] for i in range(len(rel)))
                if lr not in group:
                    closed = False
                if lr != rl:
                    commutative = False
        orders = Counter()
        for permutation in permutations:
            power = identity
            for order in range(1, 193):
                power = tuple(permutation[power[i]] for i in range(len(rel)))
                if power == identity:
                    orders[order] += 1
                    break
            else:
                raise RuntimeError("order exceeds group size")
        summary.update({"closed": closed, "commutative": commutative,
                        "order_distribution": dict(sorted(orders.items())),
                        "regular": closed and all(len({p[v] for p in permutations}) == len(rel)
                                                  for v in range(len(rel)))})
        OUT.mkdir(parents=True, exist_ok=False)
        automorphisms_path = OUT / "quotient-automorphisms.json"
        automorphisms_path.write_text(json.dumps(permutations, separators=(",", ":")) + "\n")
        automorphisms_sha = hashlib.sha256(automorphisms_path.read_bytes()).hexdigest()
        report = {"schema":"exact-quotient-regular-action-v1",
                  "status":"regular_subgroup_recovered" if summary["regular"] else "transitive_representatives_only",
                  "core":str(CORE.relative_to(ROOT)), "quotient":str(QUOTIENT.relative_to(ROOT)),
                  "individualization_base":list(BASE), "summary":summary,
                  "automorphisms":str(automorphisms_path.relative_to(ROOT)),
                  "automorphisms_sha256":automorphisms_sha,
                  "verification":"Every permutation is checked entrywise on the full 192x192 inter-fiber degree relation; closure, commutativity, element orders, and free/transitive action are then checked exactly.",
                  "scope":"Exact regular action on the colored 192-fiber quotient. Lifting these permutations to automorphisms of all 768 vertices is a separate voltage-consistency problem."}
        (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
