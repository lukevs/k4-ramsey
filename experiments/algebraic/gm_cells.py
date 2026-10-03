"""Exhaustive four-vertex Godsil-McKay cell feasibility via row-XOR collisions."""
import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import shutil
import time

from k4_ramsey.engine import load
from k4_ramsey.lab import write_json


def is_cell(rows, cell):
    selected = set(cell)
    if len(selected) != 4:
        return False
    degrees = {sum(rows[i][j]=='1' for j in cell) for i in cell}
    return len(degrees) == 1 and all(
        sum(rows[i][j]=='1' for j in cell) in (0,2,4)
        for i in range(len(rows)) if i not in selected)


def cells(rows):
    """Every regular degree d=0,1,2,3 is covered by diag=d mod 2.

    Let B=A+(d mod 2)I over F2. Cell indicator x satisfies Bx=0:
    outside coordinates have even cell-neighbor count, and inside coordinates
    have degree d plus diagonal parity. Symmetry makes Bx the XOR of four rows.
    Hence two disjoint pairs collide in row XOR. Test regularity explicitly.
    """
    n = len(rows)
    bits = [int(row[::-1],2) for row in rows]
    found = set()
    diagnostics = []
    for diagonal in (0,1):
        adjusted = [row ^ (diagonal << i) for i,row in enumerate(bits)]
        by_xor = {}
        parity_candidates = set()
        for i,j in combinations(range(n),2):
            key = adjusted[i] ^ adjusted[j]
            for u,v in by_xor.get(key,[]):
                candidate = tuple(sorted((i,j,u,v)))
                if len(set(candidate)) == 4:
                    parity_candidates.add(candidate)
            by_xor.setdefault(key,[]).append((i,j))
        accepted = {cell for cell in parity_candidates if is_cell(rows,cell)}
        found.update(accepted)
        diagnostics.append(dict(diagonal_parity=diagonal,pairs=n*(n-1)//2,
            xor_keys=len(by_xor),parity_candidates=len(parity_candidates),
            regular_cells=len(accepted)))
    return sorted(found), diagnostics


def gm_switch(rows, cell):
    if not is_cell(rows,cell):
        raise ValueError('not a valid regular size-four GM cell')
    selected = set(cell)
    result = [list(row) for row in rows]
    for v in range(len(rows)):
        if v not in selected and sum(rows[v][i]=='1' for i in cell)==2:
            for i in cell:
                result[v][i] = result[i][v] = str(1-int(rows[v][i]))
    return [''.join(row) for row in result]


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,args.out/'source_snapshot.py')
    start=time.monotonic()
    rows=load(args.input)['red_rows']
    found,diagnostics=cells(rows)
    report=dict(hypothesis='H-ALG-002',started_at=datetime.now(timezone.utc).isoformat(),
        prediction='A degree-preserving size-four GM switch supplies a distinct exact candidate',
        input=str(args.input.resolve()),input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        n=len(rows),cells=found,diagnostics=diagnostics,seconds=time.monotonic()-start,
        evidence='Exact Python exhaustive feasibility, tiny explicit-subset oracle tests; not Lean theorem',
        scope='All one-cell Godsil-McKay switches with cell size exactly four for this fixed input graph')
    write_json(args.out/'report.json',report)
    print(json.dumps(report))


if __name__=='__main__':
    main()
