"""Recover and certify a regular C2^6 x C3 subgroup on the 192 quotient."""

from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import time

from research.experiments.group_recovery.refinement_diagnostic import relation_matrix
from research.experiments.group_recovery.recover_quotient import CORE, QUOTIENT, verify


ROOT = Path(__file__).resolve().parents[3]
REPS = ROOT / "reports/group-recovery-quotient-001/quotient-automorphisms.json"
STABILIZER = ROOT / "reports/group-recovery-stabilizer-001/stabilizer.json"
OUT = ROOT / "reports/group-recovery-regular-001"


def compose(left, right):
    return tuple(left[right[i]] for i in range(len(left)))


def commute(left, right):
    return compose(left, right) == compose(right, left)


def closure(generators):
    identity = tuple(range(len(generators[0])))
    found = {identity}
    queue = deque([identity])
    while queue:
        value = queue.popleft()
        for generator in generators:
            fresh = compose(generator, value)
            if fresh not in found:
                found.add(fresh); queue.append(fresh)
    return found


def components(adjacency):
    unseen = set(range(len(adjacency))); answer=[]
    while unseen:
        root=min(unseen); unseen.remove(root); todo=[root]; cell=[]
        while todo:
            u=todo.pop(); cell.append(u)
            for v in adjacency[u]:
                if v in unseen: unseen.remove(v); todo.append(v)
        answer.append(sorted(cell))
    return sorted(answer,key=lambda c:(len(c),c))


def main():
    started=time.monotonic()
    rows=json.loads(CORE.read_text())["red_rows"]
    fibers=json.loads(QUOTIENT.read_text())["fibers"]
    rel=relation_matrix(rows,fibers)
    reps=[tuple(p) for p in json.loads(REPS.read_text())]
    stabilizer=[tuple(p) for p in json.loads(STABILIZER.read_text())]
    identity=tuple(range(192))
    assert len(reps)==192 and len(stabilizer)==240
    defect=[{j for j in range(192) if rel[i][j]==3} for i in range(192)]
    cells=components(defect)
    cell0=next(set(cell) for cell in cells if 0 in cell)

    candidates=[]
    by_target=Counter()
    for target in sorted(cell0):
        for h in stabilizer:
            candidate=compose(reps[target],h)
            if compose(candidate,candidate)==identity:
                candidates.append(candidate); by_target[target]+=1
    candidates=sorted(set(candidates),key=lambda p:(p[0],p))
    generators=[]
    subgroup={identity}
    orbit={0}
    for candidate in candidates:
        if candidate in subgroup or not all(commute(candidate,g) for g in generators):
            continue
        fresh=closure(generators+[candidate])
        fresh_orbit={p[0] for p in fresh}
        if len(fresh)==2*len(subgroup) and len(fresh_orbit)==2*len(orbit):
            generators.append(candidate); subgroup=fresh; orbit=fresh_orbit
            if len(subgroup)==64: break
    if len(subgroup)!=64 or {p[0] for p in subgroup}!=cell0:
        raise RuntimeError(f"greedy elementary subgroup failed: subgroup={len(subgroup)} orbit={len(orbit)} candidates={len(candidates)} by_target={dict(sorted(by_target.items()))}")

    ternary=None
    ternary_target=None
    normalizing=False
    for target in range(192):
        if target in cell0: continue
        for h in stabilizer:
            candidate=compose(reps[target],h)
            if compose(candidate,compose(candidate,candidate))!=identity:
                continue
            if candidate==identity:
                continue
            if all(commute(candidate,g) for g in generators):
                ternary=candidate; ternary_target=target; normalizing=True; break
        if ternary is not None: break
    if ternary is None:
        # Accept a nontrivial semidirect action if it normalizes the recovered N.
        for target in range(192):
            if target in cell0: continue
            for h in stabilizer:
                candidate=compose(reps[target],h)
                if compose(candidate,compose(candidate,candidate))!=identity or candidate==identity:
                    continue
                inverse=compose(candidate,candidate)
                if all(compose(candidate,compose(g,inverse)) in subgroup for g in generators):
                    ternary=candidate; ternary_target=target; normalizing=True; break
            if ternary is not None: break
    if ternary is None:
        raise RuntimeError("no order-three normalizer found")

    group=closure(generators+[ternary])
    assert len(group)==192 and len({p[0] for p in group})==192
    assert all(verify(rel,p) for p in group)
    abelian=all(commute(ternary,g) for g in generators)

    # Explicit base-major coordinates: z in C3, mask in C2^6.
    binary=[]
    for mask in range(64):
        value=identity
        for bit,generator in enumerate(generators):
            if mask>>bit&1: value=compose(generator,value)
        binary.append(value)
    coordinates={}
    elements={}
    powers=[identity,ternary,compose(ternary,ternary)]
    for z in range(3):
        for mask in range(64):
            element=compose(powers[z],binary[mask])
            vertex=element[0]
            assert vertex not in coordinates
            coordinates[vertex]=[z,mask]
            elements[(z,mask)]=element
    assert len(coordinates)==192

    relation_by_difference={}
    for z in range(3):
        for mask in range(64):
            relation_by_difference[f"{z},{mask}"]=rel[0][elements[(z,mask)][0]]
    # For the abelian recovered group, inverse difference is (-z, xor mask).
    if abelian:
        for u in range(192):
            zu,mu=coordinates[u]
            for v in range(192):
                zv,mv=coordinates[v]
                key=f"{(zv-zu)%3},{mu^mv}"
                assert rel[u][v]==relation_by_difference[key]

    OUT.mkdir(parents=True,exist_ok=False)
    coords_path=OUT/"coordinates.json"
    coords_path.write_text(json.dumps({str(v):coordinates[v] for v in range(192)},indent=2,sort_keys=True)+"\n")
    generators_path=OUT/"generators.json"
    generators_path.write_text(json.dumps({"binary_involutions":generators,"ternary":ternary},separators=(",",":"))+"\n")
    relation_path=OUT/"relation-by-difference.json"
    relation_path.write_text(json.dumps(relation_by_difference,indent=2,sort_keys=True)+"\n")
    report={"schema":"regular-colored-quotient-certificate-v1",
            "status":"regular_c2_6_times_c3_recovered" if abelian else "regular_c2_6_semidirect_c3_recovered",
            "group_order":len(group),"binary_rank":len(generators),"binary_order":len(subgroup),
            "ternary_target":ternary_target,"abelian":abelian,
            "involution_candidates":len(candidates),"involution_candidates_by_target":dict(sorted(by_target.items())),
            "coordinates":str(coords_path.relative_to(ROOT)),"coordinates_sha256":hashlib.sha256(coords_path.read_bytes()).hexdigest(),
            "generators":str(generators_path.relative_to(ROOT)),"generators_sha256":hashlib.sha256(generators_path.read_bytes()).hexdigest(),
            "relation_by_difference":str(relation_path.relative_to(ROOT)),"relation_sha256":hashlib.sha256(relation_path.read_bytes()).hexdigest(),
            "verification":"Six pairwise commuting involutions generate64 elements and act regularly on one defect component; an order-three automorphism commutes with/normalizes them; the generated192 permutations are entrywise color-preserving and regular. Coordinates are assigned by their unique image of vertex0; every192^2 relation entry is rechecked from group difference when abelian.",
            "seconds":time.monotonic()-started,
            "scope":"Exact colored192-fiber quotient coordinates. Full768 sheet lift remains separate."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__": main()
