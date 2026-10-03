"""Lift quotient automorphisms through the exact four-sheet voltage cover."""

from itertools import permutations
import hashlib
import json
from pathlib import Path
import time

from experiments.group_recovery.recover_quotient import CORE, QUOTIENT


ROOT = Path(__file__).resolve().parents[2]
REPS = ROOT / "reports/group-recovery-quotient-001/quotient-automorphisms.json"
STABILIZER = ROOT / "reports/group-recovery-stabilizer-001/stabilizer.json"
OUT = ROOT / "reports/group-recovery-lifted-action-001"
S4 = tuple(permutations(range(4)))


def compose(left, right):
    return tuple(left[right[i]] for i in range(len(left)))


def inverse(permutation):
    answer = [0] * len(permutation)
    for i, value in enumerate(permutation): answer[value] = i
    return tuple(answer)


def full_verify(rows, permutation):
    return sorted(permutation) == list(range(len(rows))) and all(
        rows[permutation[i]][permutation[j]] == rows[i][j]
        for i in range(len(rows)) for j in range(len(rows))
    )


def main():
    started = time.monotonic()
    rows = json.loads(CORE.read_text())["red_rows"]
    quotient = json.loads(QUOTIENT.read_text())
    fibers = quotient["fibers"]
    reps = [tuple(p) for p in json.loads(REPS.read_text())]
    stabilizer = [tuple(p) for p in json.loads(STABILIZER.read_text())]
    n = len(fibers)

    missing = {}
    adjacency = [set() for _ in range(n)]
    for i, j, p0 in quotient["complement_matching_blocks"]:
        p = tuple(p0); pinv = inverse(p)
        missing[(i, j)] = p; missing[(j, i)] = pinv
        adjacency[i].add(j); adjacency[j].add(i)
    components = []
    unseen = set(range(n))
    while unseen:
        root = min(unseen); unseen.remove(root); todo=[root]; cell=[]
        while todo:
            u=todo.pop(); cell.append(u)
            for v in adjacency[u]:
                if v in unseen: unseen.remove(v); todo.append(v)
        components.append(sorted(cell))
    assert sorted(map(len, components)) == [64,64,64]

    nonuniform = []
    for i in range(n):
        for j in range(i):
            block = tuple(tuple(int(rows[fibers[i][a]][fibers[j][b]]) for b in range(4)) for a in range(4))
            degree = sum(map(sum, block)) // 4
            if degree in (2,3): nonuniform.append((i,j,block))

    def derive_j(i, j, phi, sigma_i):
        source = missing[(i,j)]; target = missing[(phi[i],phi[j])]
        source_inv = inverse(source)
        return tuple(target[sigma_i[source_inv[b]]] for b in range(4))

    def component_solutions(phi, component):
        root = component[0]
        solutions=[]
        for root_sigma in S4:
            sigma={root:root_sigma}; todo=[root]; valid=True
            while todo and valid:
                i=todo.pop()
                for j in adjacency[i]:
                    proposal=derive_j(i,j,phi,sigma[i])
                    if j in sigma:
                        if sigma[j]!=proposal: valid=False; break
                    else:
                        sigma[j]=proposal; todo.append(j)
            if valid and set(sigma)==set(component):
                solutions.append(sigma)
        return solutions

    def block_ok(i,j,block,phi,sigma):
        target_i=fibers[phi[i]]; target_j=fibers[phi[j]]
        return all(block[a][b] == int(rows[target_i[sigma[i][a]]][target_j[sigma[j][b]]])
                   for a in range(4) for b in range(4))

    def lift(phi):
        choices=[]
        for component in components:
            valid=[]
            for sigma in component_solutions(phi,component):
                if all(block_ok(i,j,block,phi,sigma) for i,j,block in nonuniform
                       if i in sigma and j in sigma):
                    valid.append(sigma)
            if not valid: return None, None
            choices.append(valid)
        sigma={}
        for valid in choices: sigma.update(valid[0])
        permutation=[None]*len(rows)
        for i in range(n):
            for a in range(4):
                permutation[fibers[i][a]]=fibers[phi[i]][sigma[i][a]]
        permutation=tuple(permutation)
        return permutation, choices

    # Search the exact automorphism coset for one lift over every target fiber.
    quotient_lifts=[]; full_lifts=[]; trials=[]; identity_choices=None
    for target in range(n):
        found=None
        for h_index,h in enumerate(stabilizer):
            phi=compose(reps[target],h)
            permutation,choices=lift(phi)
            if permutation is not None:
                if not full_verify(rows,permutation):
                    raise RuntimeError("voltage lift failed full adjacency verification")
                found=(phi,permutation,choices,h_index); break
        if found is None: raise RuntimeError(f"no lift for quotient target {target}")
        phi,permutation,choices,h_index=found
        quotient_lifts.append(phi); full_lifts.append(permutation)
        trials.append(h_index+1)
        if target==0 and phi==tuple(range(n)): identity_choices=choices

    # Independently obtain identity-quotient kernel choices, then use four
    # root-sheet images to turn the192 fiber movers into768 vertex movers.
    identity_phi=tuple(range(n))
    _,kernel_choices=lift(identity_phi)
    assert kernel_choices is not None
    root_component=next(index for index,cell in enumerate(components) if 0 in cell)
    root_solutions=kernel_choices[root_component]
    by_sheet={sigma[0][0]:sigma for sigma in root_solutions}
    assert set(by_sheet)==set(range(4))
    kernel=[]
    for sheet in range(4):
        sigma={}
        for index,valid in enumerate(kernel_choices):
            sigma.update(by_sheet[sheet] if index==root_component else valid[0])
        permutation=[None]*len(rows)
        for i in range(n):
            for a in range(4): permutation[fibers[i][a]]=fibers[i][sigma[i][a]]
        permutation=tuple(permutation)
        assert full_verify(rows,permutation)
        kernel.append(permutation)
    movers=[]
    for lift_perm in full_lifts:
        for kernel_perm in kernel:
            mover=compose(lift_perm,kernel_perm)
            assert full_verify(rows,mover)
            movers.append(mover)
    assert len({mover[0] for mover in movers})==768

    OUT.mkdir(parents=True,exist_ok=False)
    movers_path=OUT/"vertex-transitive-movers.json"
    movers_path.write_text(json.dumps(movers,separators=(",",":"))+"\n")
    quotient_path=OUT/"lifted-quotient-automorphisms.json"
    quotient_path.write_text(json.dumps(quotient_lifts,separators=(",",":"))+"\n")
    report={"schema":"exact-lifted-transitive-action-v1",
            "status":"full_768_vertex_transitivity_certified",
            "fiber_targets":len(full_lifts),"kernel_root_sheet_images":len(kernel),
            "vertex_movers":len(movers),"distinct_images_of_vertex0":len({p[0] for p in movers}),
            "stabilizer_coset_trials":{"min":min(trials),"max":max(trials),"sum":sum(trials)},
            "root_component_kernel_solutions":len(root_solutions),
            "movers":str(movers_path.relative_to(ROOT)),"movers_sha256":hashlib.sha256(movers_path.read_bytes()).hexdigest(),
            "lifted_quotient_automorphisms":str(quotient_path.relative_to(ROOT)),"lifted_quotient_sha256":hashlib.sha256(quotient_path.read_bytes()).hexdigest(),
            "verification":"Every quotient map preserves the exact degree-colored192 relation; sheet maps are propagated through every degree-three voltage and filtered by every degree-two block; every retained768 permutation is then checked on all768^2 adjacency entries. The768 movers send vertex0 bijectively to all vertices.",
            "seconds":time.monotonic()-started,
            "scope":"Exact transitive automorphism action and four-sheet Schreier/voltage coordinates; the768 movers are a transversal, not claimed closed or a regular Cayley subgroup."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__": main()
