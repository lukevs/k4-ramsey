"""Fast exact factor audit for the archived 768 core and its 192 fibers."""

from collections import Counter, deque
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/published_cayley_768.json"
QUOTIENT = ROOT / "reports/pilot-algebraic-lift-001/quotient.json"
GRAPHON = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
OUT = ROOT / "reports/latent-precision-factor-audit-001"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(adjacency):
    unseen = set(range(len(adjacency)))
    result = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = []
        while queue:
            u = queue.popleft()
            component.append(u)
            for v in adjacency[u]:
                if v in unseen:
                    unseen.remove(v)
                    queue.append(v)
        result.append(sorted(component))
    return sorted(result, key=lambda cell: (len(cell), cell))


def main():
    archived = json.loads(DATA.read_text())
    quotient = json.loads(QUOTIENT.read_text())
    graphon = json.loads(GRAPHON.read_text())
    rows = archived["red_rows"]
    fibers = quotient["fibers"]
    probabilities = graphon["red_probability_numerators"]
    assert len(rows) == 768 and len(fibers) == len(probabilities) == 192

    relation = [[0] * 192 for _ in range(192)]
    degree_probability = Counter()
    for i in range(192):
        for j in range(i):
            degree = sum(rows[u][v] == "1" for u in fibers[i] for v in fibers[j]) // 4
            assert degree in (0, 2, 3, 4)
            relation[i][j] = relation[j][i] = degree
            degree_probability[(degree, probabilities[i][j])] += 1

    defect = [{j for j in range(192) if relation[i][j] == 3} for i in range(192)]
    defect_components = components(defect)
    assert [len(cell) for cell in defect_components] == [64, 64, 64]
    component_of = {u: index for index, cell in enumerate(defect_components) for u in cell}

    component_pair_histograms = {}
    component_pair_constant = {}
    for a, left in enumerate(defect_components):
        for b in range(a + 1):
            right = defect_components[b]
            values = [relation[u][v] for u in left for v in right if u != v]
            key = f"{a},{b}"
            histogram = Counter(values)
            component_pair_histograms[key] = dict(sorted(histogram.items()))
            component_pair_constant[key] = len(histogram) == 1

    half_edges = [(i, j) for i in range(192) for j in range(i) if relation[i][j] == 2]
    half_component_pairs = Counter(tuple(sorted((component_of[i], component_of[j])))
                                   for i, j in half_edges)
    assert len(half_edges) == 96
    assert all(sum(relation[i][j] == 2 for j in range(192)) == 1 for i in range(192))

    # A composition factor on the three intrinsic 64-cells would require each
    # off-diagonal outer-cell pair to have a constant relation.  Record exact
    # witnesses showing failure, rather than constructing a profile operator.
    nonconstant_witnesses = {}
    for a in range(3):
        for b in range(a):
            seen = {}
            for u in defect_components[a]:
                for v in defect_components[b]:
                    seen.setdefault(relation[u][v], [u, v])
            nonconstant_witnesses[f"{a},{b}"] = seen

    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "cayley-factor-audit-v1",
        "status": "no_stationary_composition_factor_detected",
        "inputs": {
            "archived_core": str(DATA.relative_to(ROOT)),
            "archived_core_sha256": sha256(DATA),
            "four_sheet_quotient": str(QUOTIENT.relative_to(ROOT)),
            "four_sheet_quotient_sha256": sha256(QUOTIENT),
            "graphon_parent": str(GRAPHON.relative_to(ROOT)),
            "graphon_parent_sha256": sha256(GRAPHON),
        },
        "metadata_obstruction": {
            "archived_core_keys": sorted(archived),
            "has_vertex_group_labels": False,
            "has_generator_set": False,
            "note": "The archive stores only adjacency rows and weights. The known Z3 x F2^8 abstract group description has no vertex-to-group-element map in the repository; documented mixed-radix interpretations do not match this labeling.",
        },
        "exact_intrinsic_structure": {
            "four_sheet_fibers": len(fibers),
            "fiber_size": 4,
            "interfiber_degree_probability_counts": {
                f"degree={degree},p={probability}": count
                for (degree, probability), count in sorted(degree_probability.items())
            },
            "degree3_defect_component_sizes": [len(cell) for cell in defect_components],
            "degree3_component_vertices": defect_components,
            "degree2_edges_form_perfect_matching": True,
            "degree2_component_pair_counts": {
                f"{a},{b}": count for (a, b), count in sorted(half_component_pairs.items())
            },
            "component_pair_relation_histograms": component_pair_histograms,
        },
        "composition_test": {
            "partition": "the unique connected components of the degree-3 defect relation (three cells of size 64)",
            "constant_relation_by_component_pair": component_pair_constant,
            "offdiagonal_nonconstant_witnesses": nonconstant_witnesses,
            "result": "fail: every cross-component 64x64 block contains multiple exact relation types, so this intrinsic 3-by-64 partition is not an outer composition with one internal profile",
        },
        "xor_tensor_test": {
            "necessary_condition": "After independent relabeling inside the three outer cells, a one-kernel XOR factor has equal-or-complementary block-value multisets, while a one-kernel tensor factor has constant-zero blocks or repeated copies of one block-value multiset.",
            "observed": "Each internal 64-cell block contains degree/probability relations 0,2,3,4 including fractional h and p, whereas every cross-cell block contains only deterministic degrees 0 and 4 (1792 and 2304 ordered pairs respectively). Relabeling cannot change these multisets.",
            "result": "fail for the obvious three-cell one-kernel XOR/tensor factors; a heterogeneous graph-directed factor is not excluded",
        },
        "decision": "Do not build an 11-profile stationary operator: no actual composition factor was established. The exact four-sheet voltage lift is real but has four inter-fiber relation types and edge-dependent permutation voltages; it is a graph-directed cover, not a repeated terminal composition kernel.",
        "scope": "Fast metadata and obvious intrinsic-factor audit only. Without a vertex-to-group-element map, this does not enumerate abstract low-index subgroups of Z3 x F2^8 or rule out an alternative partition induced by missing group labels; it also does not rule out a multi-type graph-directed substitution.",
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": report["status"],
        "components": report["exact_intrinsic_structure"]["degree3_defect_component_sizes"],
        "half_component_pairs": report["exact_intrinsic_structure"]["degree2_component_pair_counts"],
        "constant_relation_by_component_pair": component_pair_constant,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
