"""Nagda-inspired grow -> witness-guided rebuild -> exact repair pilot.

The score is the exact ordered-index blue-diagonal blow-up objective from the
native engine, not a distinct-K4 surrogate.  This is a procedure comparison,
not a family optimum or a reinforcement-learning implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, certificate, load

ROOT = Path(__file__).resolve().parents[3]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def literal_ordered(rows: list[str]) -> int:
    n = len(rows)
    answer = 0
    for v in itertools.product(range(n), repeat=4):
        colors = [int(rows[v[i]][v[j]]) for i in range(4) for j in range(i + 1, 4)]
        answer += all(colors) or not any(colors)
    return answer


def controls() -> None:
    rows = ["01010", "10101", "01011", "10100", "01100"]
    graph = Graph(certificate(rows))
    assert graph.counts()["numerator"] == literal_ordered(rows)
    before = graph.counts()["numerator"]
    delta = graph.delta(1, 4)
    graph.flip(1, 4)
    assert graph.counts()["numerator"] == before + delta
    graph.flip(1, 4)
    assert graph.counts()["numerator"] == before
    graph.close()


def quotient_representatives(candidate: dict, model: dict) -> dict:
    vertices = [fiber[0] for fiber in model["fibers"]]
    rows = candidate["red_rows"]
    return certificate(["".join(rows[i][j] for j in vertices) for i in vertices])


def random_graph(n: int, seed: int) -> dict:
    rng = random.Random(seed)
    rows = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            rows[i][j] = rows[j][i] = rng.randrange(2)
    return certificate(["".join(map(str, row)) for row in rows])


def grow_clone(data: dict, donor: int) -> dict:
    old = data["red_rows"]
    n = len(old)
    rows = [list(row) + [old[i][donor]] for i, row in enumerate(old)]
    rows.append([old[donor][j] for j in range(n)] + ["0"])
    return certificate(["".join(row) for row in rows])


def density_key(data: dict) -> tuple[int, int]:
    graph = Graph(data)
    numerator = graph.counts()["numerator"]
    graph.close()
    return numerator, len(data["red_rows"]) ** 4


def better(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] * b[1] < b[0] * a[1]


def strict_repair(data: dict, seconds: float) -> tuple[dict, dict]:
    graph = Graph(data)
    graph.enable_cache()
    initial = value = graph.counts()["numerator"]
    start = time.monotonic()
    scans = accepted = 0
    local = False
    while time.monotonic() - start < seconds:
        move = graph.best_cached_flip()
        scans += 1
        if move is None or move[2] >= 0:
            local = True
            break
        graph.flip(move[0], move[1])
        value += move[2]
        accepted += 1
    if graph.counts()["numerator"] != value:
        raise RuntimeError("strict repair count drift")
    out = graph.export()
    graph.close()
    return out, dict(initial_numerator=initial, numerator=value, scans=scans,
                     accepted=accepted, single_edge_local=local,
                     seconds=time.monotonic() - start)


def witness_edge(rows: list[bytearray], rng: random.Random) -> tuple[int, int] | None:
    n = len(rows)
    for _ in range(256):
        v = [rng.randrange(n) for _ in range(4)]
        pairs = [(v[i], v[j]) for i in range(4) for j in range(i + 1, 4)]
        colors = [rows[a][b] for a, b in pairs]
        if all(c == colors[0] for c in colors):
            mutable = [(a, b) for a, b in pairs if a != b]
            if mutable:
                a, b = rng.choice(mutable)
                return (a, b) if a < b else (b, a)
    return None


def growth_repair(clone: dict, seed: int, seconds: float, destroy_edges: int,
                  focus: int | None = None) -> tuple[dict, dict]:
    rng = random.Random(seed)
    n = len(clone["red_rows"])
    new = n - 1 if focus is None else focus
    # Retain the undamaged clone as a portfolio checkpoint, then force a new basin.
    best_data = clone
    best = density_key(clone)
    destroyed = [list(row) for row in clone["red_rows"]]
    others = [v for v in range(n) if v != new]
    targets = rng.sample(others, min(destroy_edges, len(others)))
    for v in targets:
        bit = "0" if destroyed[new][v] == "1" else "1"
        destroyed[new][v] = destroyed[v][new] = bit
    start_data = certificate(["".join(row) for row in destroyed])
    graph = Graph(start_data)
    graph.enable_cache()
    rows = [bytearray(map(int, row)) for row in start_data["red_rows"]]
    value = graph.counts()["numerator"]
    start = time.monotonic()
    anneal_deadline = start + 0.70 * seconds
    probes = [abs(graph.cached_delta(*rng.sample(range(n), 2))) for _ in range(64)]
    temperature = max(1.0, sorted(probes)[len(probes) // 2] / 2)
    proposals = accepted = uphill = witnesses = reheats = no_best = 0
    while time.monotonic() < anneal_deadline:
        edge = witness_edge(rows, rng) if rng.random() < 0.75 else None
        witnesses += edge is not None
        if edge is None:
            if rng.random() < 0.7:
                edge = tuple(sorted((rng.choice(others), new)))
            else:
                edge = tuple(sorted(rng.sample(range(n), 2)))
        u, v = edge
        delta = graph.cached_delta(u, v)
        proposals += 1
        phase = (time.monotonic() - start) / max(1e-9, anneal_deadline - start)
        temp = temperature * max(0.02, 1 - phase)
        if delta < 0 or rng.random() < math.exp(-max(0, delta) / temp):
            graph.flip(u, v)
            rows[u][v] ^= 1
            rows[v][u] ^= 1
            value += delta
            accepted += 1
            uphill += delta > 0
            now = (value, n**4)
            if better(now, best):
                best = now
                best_data = graph.export()
                no_best = 0
            else:
                no_best += 1
        if no_best >= 1000:
            # Paper-inspired reheat: a tiny exact perturbation chain, not relabeling
            # (plain relabeling is score- and search-state-invariant here).
            for _ in range(3):
                u, v = sorted(rng.sample(range(n), 2))
                delta = graph.cached_delta(u, v)
                graph.flip(u, v)
                rows[u][v] ^= 1
                rows[v][u] ^= 1
                value += delta
            reheats += 1
            no_best = 0
    if graph.counts()["numerator"] != value:
        raise RuntimeError("anneal count drift")
    graph.close()
    remaining = max(0.0, seconds - (time.monotonic() - start))
    repaired, repair = strict_repair(best_data, remaining)
    final = density_key(repaired)
    if better(final, best):
        best_data, best = repaired, final
    return best_data, dict(numerator=best[0], denominator=best[1], proposals=proposals,
                           accepted=accepted, uphill=uphill, witness_proposals=witnesses,
                           reheats=reheats, destroyed_incident_edges=len(targets),
                           repair=repair, seconds=time.monotonic() - start)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seconds-per-arm", type=float, default=3.0)
    parser.add_argument("--full-incumbent", action="store_true")
    parser.add_argument("--destroy-only", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    controls()
    candidate_path = ROOT / "reports/finite-joint-two-switch-002/candidate.json"
    model_path = ROOT / "reports/pilot-algebraic-cycle-model-001/model.json"
    incumbent = load(candidate_path)
    algebraic = quotient_representatives(incumbent, json.loads(model_path.read_text()))
    sources = ({"best_binary_finite": incumbent} if args.full_incumbent else
               {"algebraic_quotient": algebraic, "random": random_graph(192, 20260927)})
    seeds = (17,) if args.full_incumbent else (17, 43)
    results = []
    for source_name, source in sources.items():
        for seed in seeds:
            rng = random.Random(seed)
            donor = rng.randrange(len(source["red_rows"]))
            clone = source if args.destroy_only else grow_clone(source, donor)
            for method in ("single_local", "growth_repair"):
                begun = time.monotonic()
                if method == "single_local":
                    result, stats = strict_repair(clone, args.seconds_per_arm)
                else:
                    result, stats = growth_repair(
                        clone, seed, args.seconds_per_arm, 32,
                        focus=donor if args.destroy_only else None)
                path = args.out / f"{source_name}-seed{seed}-{method}.json"
                write(path, result)
                numerator, denominator = density_key(result)
                results.append(dict(source=source_name, seed=seed, donor=donor,
                                    method=method, numerator=numerator,
                                    denominator=denominator, decimal=numerator / denominator,
                                    candidate=str(path), candidate_sha256=sha(path), stats=stats,
                                    wall_seconds=time.monotonic() - begun))
    report = dict(schema="growth-repair-pilot-v1", status="completed",
                  controls="tiny literal ordered-tuple equality with repeats/blue diagonal and sequential exact-delta drift passed",
                  objective="exact asymptotic equal-mass blue-diagonal step-graphon density numerator / n^4",
                  procedure=("retain parent; destroy32 edges incident to one type; " if args.destroy_only else
                             "clone growth; retain clone; destroy32 incident edges; ") +
                            "75% monochromatic ordered-K4 witness proposals; reheated Metropolis; strict exact cached repair",
                  baseline="same source, donor, clone, seed and wall budget; strict exact cached single-edge repair",
                  seconds_per_arm=args.seconds_per_arm,
                  source_candidate=str(candidate_path), source_candidate_sha256=sha(candidate_path),
                  source_model=str(model_path), source_model_sha256=sha(model_path),
                  results=results,
                  caveat="Small matched procedure gate; no reinforcement learning, family optimum, or global claim.")
    write(args.out / "report.json", report)
    for row in results:
        print(row["source"], row["seed"], row["method"], row["decimal"], row["wall_seconds"])


if __name__ == "__main__":
    main()
