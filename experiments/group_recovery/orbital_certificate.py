"""Exact Schreier/orbital certificate and fractional-edge orbit basis."""

from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import time

from experiments.group_recovery.refinement_diagnostic import relation_matrix
from experiments.group_recovery.recover_quotient import CORE, QUOTIENT, verify


ROOT = Path(__file__).resolve().parents[2]
REPS = ROOT / "reports/group-recovery-quotient-001/quotient-automorphisms.json"
STABILIZER = ROOT / "reports/group-recovery-stabilizer-001/stabilizer.json"
PARENT = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
OUT = ROOT / "reports/group-recovery-orbitals-001"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compose(left, right):
    return tuple(left[right[i]] for i in range(len(left)))


def inverse(permutation):
    answer=[0]*len(permutation)
    for i,value in enumerate(permutation): answer[value]=i
    return tuple(answer)


def closure(generators, n):
    identity=tuple(range(n)); found={identity}; todo=deque([identity])
    while todo:
        value=todo.popleft()
        for generator in generators:
            fresh=compose(generator,value)
            if fresh not in found: found.add(fresh);todo.append(fresh)
    return found


def vertex_orbit(generators, root):
    expanded=list(generators)+[inverse(g) for g in generators]
    found={root}; todo=[root]
    while todo:
        u=todo.pop()
        for generator in expanded:
            v=generator[u]
            if v not in found: found.add(v);todo.append(v)
    return found


def preserves_matrix(matrix, permutation):
    n=len(matrix)
    return all(matrix[permutation[i]][permutation[j]]==matrix[i][j]
               for i in range(n) for j in range(n))


def main():
    started=time.monotonic()
    rows=json.loads(CORE.read_text())["red_rows"]
    fibers=json.loads(QUOTIENT.read_text())["fibers"]
    rel=relation_matrix(rows,fibers); n=len(rel)
    reps=[tuple(p) for p in json.loads(REPS.read_text())]
    stabilizer=[tuple(p) for p in json.loads(STABILIZER.read_text())]
    parent_record=json.loads(PARENT.read_text())
    probability=parent_record["red_probability_numerators"]
    denominator=parent_record["edge_probability_denominator"]
    assert len(probability)==n
    assert len(reps)==n and all(reps[u][0]==u for u in range(n))

    # Compact exact generators for the enumerated point stabilizer.
    h_generators=[]; h_group={tuple(range(n))}
    for candidate in stabilizer:
        if candidate in h_group: continue
        fresh=closure(h_generators+[candidate],n)
        if len(fresh)>len(h_group):
            h_generators.append(candidate);h_group=fresh
        if len(h_group)==len(stabilizer): break
    assert h_group==set(stabilizer)

    # Add root movers only when they enlarge the current vertex orbit. Since
    # the generated group contains the full point stabilizer and is transitive,
    # orbit-stabilizer proves it is the full color-automorphism group.
    generators=list(h_generators); orbit=vertex_orbit(generators,0)
    mover_targets=[]
    for candidate in reps:
        if candidate[0] in orbit: continue
        generators.append(candidate);mover_targets.append(candidate[0])
        orbit=vertex_orbit(generators,0)
        if len(orbit)==n: break
    assert len(orbit)==n and all(verify(rel,g) for g in generators)

    parent_preserved=all(preserves_matrix(probability,g) for g in generators)
    if not parent_preserved:
        raise RuntimeError("published two-parameter parent is not invariant under recovered full quotient action")

    # H-orbits are the directed orbitals viewed from vertex0.
    unseen=set(range(n)); h_orbits=[]
    expanded_h=h_generators+[inverse(g) for g in h_generators]
    while unseen:
        root=min(unseen); cell=vertex_orbit(expanded_h,root)
        unseen-=cell; h_orbits.append(sorted(cell))
    h_orbits=sorted(h_orbits,key=lambda cell:(min(cell),len(cell)))
    orbit_of={v:index for index,cell in enumerate(h_orbits) for v in cell}
    assert all(len({probability[0][v] for v in cell})==1 for cell in h_orbits)

    orbital_matrix=[]
    for u in range(n):
        undo=inverse(reps[u])
        orbital_matrix.append([orbit_of[undo[v]] for v in range(n)])
    orbital_probabilities={str(index):probability[0][cell[0]] for index,cell in enumerate(h_orbits)}
    assert all(probability[u][v]==orbital_probabilities[str(orbital_matrix[u][v])]
               for u in range(n) for v in range(n))

    # Direct unordered-pair orbits give the collective fractional Hessian basis.
    fractional={(i,j) for i in range(n) for j in range(i) if 0<probability[i][j]<denominator}
    unseen=set(fractional); pair_orbits=[]; pair_orbit_of={}
    expanded=generators+[inverse(g) for g in generators]
    while unseen:
        root=min(unseen); cell={root}; todo=[root]
        while todo:
            i,j=todo.pop()
            for generator in expanded:
                a,b=sorted((generator[i],generator[j]),reverse=True)
                edge=(a,b)
                assert edge in fractional
                if edge not in cell: cell.add(edge);todo.append(edge)
        orbit_index=len(pair_orbits)
        for edge in cell: pair_orbit_of[f"{edge[0]},{edge[1]}"]=orbit_index
        unseen-=cell;pair_orbits.append(sorted(cell))
    assert sum(map(len,pair_orbits))==1248
    pair_records=[]
    for index,cell in enumerate(pair_orbits):
        values={probability[i][j] for i,j in cell}
        assert len(values)==1
        pair_records.append({"orbit":index,"size":len(cell),"probability_numerator":next(iter(values)),
                             "representative":list(cell[0])})

    OUT.mkdir(parents=True,exist_ok=True)
    generators_path=OUT/"generators.json"
    generators_path.write_text(json.dumps({"point_stabilizer_generators":h_generators,
                                            "transitive_movers":generators[len(h_generators):]},separators=(",",":"))+"\n")
    orbital_path=OUT/"orbital-matrix.json"
    orbital_path.write_text(json.dumps(orbital_matrix,separators=(",",":"))+"\n")
    pair_path=OUT/"fractional-pair-orbits.json"
    pair_path.write_text(json.dumps({"records":pair_records,"edge_to_orbit":pair_orbit_of},indent=2,sort_keys=True)+"\n")
    report={"schema":"exact-schreier-orbital-certificate-v1",
            "status":"full_quotient_orbitals_and_fractional_basis_certified",
            "automorphism_group_order":n*len(stabilizer),"degree":n,
            "point_stabilizer_order":len(stabilizer),"point_stabilizer_generators":len(h_generators),
            "transitive_mover_targets":mover_targets,"generator_count":len(generators),
            "directed_orbitals":len(h_orbits),"orbital_sizes":[len(cell) for cell in h_orbits],
            "orbital_probability_numerators":orbital_probabilities,
            "fractional_unordered_edges":len(fractional),"fractional_pair_orbits":pair_records,
            "generators":str(generators_path.relative_to(ROOT)),"generators_sha256":hashlib.sha256(generators_path.read_bytes()).hexdigest(),
            "orbital_matrix":str(orbital_path.relative_to(ROOT)),"orbital_matrix_sha256":hashlib.sha256(orbital_path.read_bytes()).hexdigest(),
            "fractional_pair_orbit_map":str(pair_path.relative_to(ROOT)),"fractional_pair_orbit_sha256":hashlib.sha256(pair_path.read_bytes()).hexdigest(),
            "parent":str(PARENT.relative_to(ROOT)),"parent_preserved":parent_preserved,
            "inputs":{"core_sha256":sha256(CORE),"quotient_sha256":sha256(QUOTIENT),
                      "representatives_sha256":sha256(REPS),"stabilizer_sha256":sha256(STABILIZER),
                      "parent_sha256":sha256(PARENT),"source_sha256":sha256(Path(__file__))},
            "verification":"The exact240-element point stabilizer is exhaustively enumerated; compact generators close back to all240. Adding the recorded root movers gives a transitive color-preserving action, hence by orbit-stabilizer the full group has order192*240. H-orbits define orbitals; all192^2 parent probabilities are reconstructed from orbital IDs. Fractional unordered pairs are independently closed under the generators.",
            "seconds":time.monotonic()-started,
            "scope":"Exact symmetry/orbital basis of the published two-parameter192 graphon parent and its underlying four-sheet quotient; not a regular Cayley coordinate claim."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__": main()
