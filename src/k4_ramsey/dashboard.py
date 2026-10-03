"""Static, self-contained view of single-experiment evidence (not a verifier)."""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

import typer

from .engine import SEED_NUMERATOR, TARGET
from .schemas.dashboard import RecordedValue, ReportHeader, WeightedSidecar

app = typer.Typer(pretty_exceptions_enable=False)


def main() -> None:
    app()


@app.command()
def render_command(
    reports: Annotated[Path, typer.Option()] = Path("reports"),
    out: Annotated[Path, typer.Option()] = Path("journal.html"),
) -> None:
    """Render a static, self-contained dashboard without rerunning experiments."""
    typer.echo(render(reports, out))


def render(reports: Path, out: Path):
    """Render existing reports without modifying, rerunning, or promoting them."""
    reports, out = Path(reports).resolve(), Path(out).resolve()
    records = sorted(
        iter_report_records(reports),
        key=lambda item: item[1]["started_at"],
        reverse=True,
    )
    entries = [(path, data, *assess_record(path, data)) for path, data in records]
    verified = [entry for entry in entries if entry[2] is not None]
    graphons = read_graphon_records(reports)
    ranked = list(verified)
    for record in graphons:
        value = record["value"]
        ranked.append(
            (
                record["path"],
                {
                    "verification": {
                        "numerator": value.numerator,
                        "denominator": value.denominator,
                    }
                },
                value,
                record["level"],
            )
        )
    best = min(ranked, key=lambda entry: entry[2]) if ranked else None
    benchmark = Fraction(TARGET, 768**4)
    best_value = (
        f"{best[1]['verification']['numerator']} / {best[1]['verification']['denominator']}"
        if best
        else "No checked candidate"
    )
    best_gap = str(best[2] - benchmark) if best else "—"

    # A reduced fraction's numerator is not a comparable score across runs.
    # Always show the same denominator (768^4) in the headline and run cards.
    def reference_units(value):
        gap = (value - benchmark) * 768**4
        if gap.denominator == 1:
            return f"{abs(gap.numerator):,} " + (
                "below" if gap < 0 else "above" if gap > 0 else "from"
            )
        return f"{float(abs(gap)):,.3f} " + ("below" if gap < 0 else "above")

    best_gap_units = reference_units(best[2]) if best else "—"
    best_name = (
        str(best[0].parent.relative_to(reports)) if best else "Awaiting evidence"
    )
    best_percent = f"{float(best[2]) * 100:.10f}%" if best else "—"
    active = sum(
        data["status"] in {"preparing", "searching", "verifying"} for _, data in records
    )
    cards = []
    for path, data, value, evidence in entries:
        if any(record["path"] == path for record in graphons):
            continue  # Already displayed with its applicable graphon evidence.
        name = str(path.parent.relative_to(reports))
        status = data["status"]
        color = (
            "checked"
            if value is not None
            else (
                "failed"
                if status in {"failed", "timeout", "interrupted"}
                else "pending"
            )
        )
        duration = data.get("total_seconds")
        runtime = (
            f"{duration:.2f} s" if type(duration) in (int, float) else "Not recorded"
        )
        links = [
            render_link(path, out, "Report" if path.name == "report.json" else "Status")
        ]
        weighted = bool(data.get("_weighted_sidecar"))
        badge = "weighted v1 · checked" if weighted and value is not None else status
        if weighted:
            links += [
                render_link(data["_candidate_path"], out, "Weighted candidate"),
                render_link(data["_weighted_sidecar"], out, "Weighted verification v1"),
            ]
        for filename, label in [
            ("candidate.json", "Candidate"),
            ("verification.json", "Verification"),
            ("search.json", "Search metrics"),
            ("config.json", "Config"),
            ("stdout.log", "Output"),
            ("stderr.log", "Errors"),
        ]:
            if (path.parent / filename).is_file():
                links.append(render_link(path.parent / filename, out, label))
        exact = str(value) if value is not None else "Unverified"
        display = f"{float(value) * 100:.10f}%" if value is not None else "—"
        raw = (
            f"{data['verification']['numerator']} / {data['verification']['denominator']}"
            if value is not None
            else "—"
        )
        improvement = (
            data.get("improvement", "—") if value is not None and not weighted else "—"
        )
        gap_units = reference_units(value) if value is not None else "—"
        error = (
            f'<p class="error">{escape_html(data["error"])}</p>'
            if data.get("error")
            else ""
        )
        cards.append(f"""<article class="run">
          <div class="run-top"><span class="run-name">{escape_html(name)}</span><span class="badge {color}">{escape_html(badge)}</span></div>
          <h3>{escape_html(data["hypothesis"])}</h3>
          <p class="prediction">{escape_html(data.get("prediction", "No prediction recorded"))}</p>
          <dl><div><dt>Exact checked density</dt><dd>{escape_html(exact)}</dd></div>
          <div><dt>Gap to McKay · numerator units over 768⁴</dt><dd>{escape_html(gap_units)} McKay</dd></div>
          <div><dt>Numerator / denominator · rounded percentage</dt><dd>{escape_html(raw)}<br>{escape_html(display)}</dd></div>
          <div><dt>Numerator removed from input (positive is better)</dt><dd>{escape_html(improvement)}</dd></div>
          <div><dt>Started · UTC / reported zone</dt><dd>{escape_html(data["started_at"])}</dd></div>
          <div><dt>Total runtime · seed</dt><dd>{escape_html(runtime)} · {escape_html(data.get("seed", "—"))}</dd></div></dl>
          <p class="evidence">{escape_html(evidence)}</p>{error}<nav>{" ".join(links)}</nav></article>""")
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>K4 research · experiment journal</title>
<style>
:root{color-scheme:light;--ink:#142b35;--muted:#577078;--line:#d7e3e3;--teal:#086a64}
*{box-sizing:border-box}body{margin:0;background:#f2f6f5;color:var(--ink);font:15px/1.6 system-ui,-apple-system,sans-serif}
main{max-width:1120px;margin:auto;padding:48px 28px 64px}header{border-bottom:1px solid var(--line);padding-bottom:26px}
.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:.17em;color:var(--teal);font-weight:700}
h1{font-size:clamp(30px,5vw,48px);letter-spacing:-.04em;line-height:1.12;margin:12px 0}header p{max-width:760px;color:var(--muted)}
.summary{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin:26px 0}.tile{background:#fff;border:1px solid var(--line);border-radius:12px;padding:22px;overflow-wrap:anywhere}
.tile strong{display:block;font-size:22px;line-height:1.4;margin:8px 0}.tile small,.muted{color:var(--muted)}.label{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.notice{border-left:3px solid var(--teal);padding:2px 16px;margin:24px 0;color:var(--muted)}
.chart{background:white;border:1px solid var(--line);border-radius:12px;padding:24px;margin:24px 0}.chart svg{display:block;width:100%;height:auto}.chart svg text{font:12px ui-monospace,monospace;fill:#577078}.chart p{font-size:13px}
.legend{display:flex;gap:8px 20px;flex-wrap:wrap;font-size:12px}
.graphon-summary{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:18px 0}.graphon-tile{background:#f8fbfa}.graphon-tile p{margin:12px 0 4px}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line)}th{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.section-heading{display:flex;gap:16px;align-items:center;justify-content:space-between;margin:32px 0 16px}h2{font-size:21px;margin:0}
input{font:inherit;padding:9px 13px;border:1px solid var(--line);border-radius:8px;max-width:100%;background:white}
.run{background:white;border:1px solid var(--line);border-radius:12px;padding:24px;margin:16px 0;overflow-wrap:anywhere}
.run-top{display:flex;align-items:center;justify-content:space-between;gap:16px}.run-name{font:13px ui-monospace,monospace;color:var(--muted)}
.badge{font-size:12px;padding:3px 10px;border-radius:20px;background:#eef2f4}.checked{background:#dbf1e8;color:#166348}.failed{background:#fce6e1;color:#9b392e}.pending{background:#fff1d4;color:#775211}
h3{font-size:20px;line-height:1.35;margin:15px 0 8px}.prediction{color:var(--muted);margin:0 0 18px}dl{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:0}dt{font-size:12px;color:var(--muted)}dd{margin:3px 0;font:14px/1.6 ui-monospace,monospace}
.evidence{font-size:12px;color:var(--muted)}.error{color:#9b392e}nav{display:flex;gap:16px;flex-wrap:wrap;border-top:1px solid var(--line);padding-top:14px}a{color:var(--teal);text-underline-offset:3px}footer{font-size:12px;color:var(--muted);margin-top:30px}
@media(max-width:650px){main{padding:28px 16px}.summary,.graphon-summary,dl{grid-template-columns:1fr}.section-heading{align-items:stretch;flex-direction:column}.run{padding:18px}.tile strong{font-size:19px}}
</style></head><body><main>"""
    page += f"""<header><div class="eyebrow">K4 multiplicity / research notebook</div>
<h1>Experiments, with evidence.</h1><p>Explore hypotheses rapidly. Keep exact values, failed attempts, and verification boundaries visible. McKay is a comparison milestone, not a stopping criterion.</p></header>
<section class="summary" aria-label="Experiment summary"><div class="tile"><span class="label">Legacy run reports / binary or weighted checked</span><strong>{len(entries)} / {len(verified)}</strong><small>{len(graphons)} graphon verification reports. {active} recorded in progress. Completed evidence is required for ranking.</small></div>
<div class="tile"><span class="label">Best exact checked density</span><strong>{escape_html(best_value)}</strong><div>{escape_html(best_percent)}</div><small>{escape_html(best_name)}</small></div>
<div class="tile"><span class="label">Gap to McKay · fixed units</span><strong>{escape_html(best_gap_units)} McKay</strong><small>Numerator units with denominator 768⁴. Smaller is better.<br>Exact density difference: {escape_html(best_gap)}</small></div></section>
<aside class="notice">The headline and chart include all independently checked constructions with matching candidate hashes. Evidence methods include native exact recounts and compiled Lean recounts; neither is an end-to-end formal proof. Graphon verification methods are shown below. This page does not rerun the verifier. Rankings use exact fractions, not rounded decimals.</aside>
{render_timeline(verified, benchmark, graphons)}
{render_portfolio_panel(reports, out)}
{render_graphon_panel(graphons, out, benchmark)}
<div class="section-heading"><h2>Experiment log</h2><label><span class="muted">Filter </span><input id="filter" type="search" placeholder="Hypothesis, status, run…" aria-label="Filter experiments"></label></div>
<section id="runs">{"".join(cards) if cards else '<p class="muted">No experiment reports yet.</p>'}</section>
<footer>Static snapshot generated {escape_html(stamp)}. Not live monitoring. Regenerate with <code>just dashboard --reports REPORTS --out JOURNAL.html</code>.</footer></main>
<script>document.getElementById('filter').addEventListener('input',function(){{const q=this.value.toLowerCase();document.querySelectorAll('.run').forEach(el=>{{el.hidden=!el.textContent.toLowerCase().includes(q)}})}});</script></body></html>"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return out


def iter_report_records(root):
    for directory, children, files in os.walk(root, followlinks=False):
        children[:] = sorted(
            c for c in children if c != "snapshot" and not c.startswith(".")
        )
        name = "report.json" if "report.json" in files else "status.json"
        if name not in files:
            continue
        path = Path(directory) / name
        try:
            data = json.loads(path.read_text(), parse_constant=lambda s: None)
            ReportHeader.model_validate(data)
        except (OSError, ValueError):
            continue
        children[:] = []
        yield path, attach_weighted_evidence(path, data)


def attach_weighted_evidence(path, data):
    """Attach separately versioned recount evidence in memory, never rewrite reports."""
    sidecar = path.parent / "weighted-verification-v1.json"
    if not sidecar.is_file() or data.get("status") != "completed":
        return data
    enriched = dict(data)
    try:
        checked = json.loads(sidecar.read_text())
        sidecar_data = WeightedSidecar.model_validate(checked)
        candidate = Path(sidecar_data.candidate).resolve()
        if candidate.parent != path.parent.resolve():
            raise ValueError("weighted candidate must belong to this experiment")
        enriched.update(
            verification=checked,
            evidence=checked["status"],
            candidate_sha256=checked.get("candidate_sha256"),
            _candidate_path=candidate,
            _weighted_sidecar=sidecar,
        )
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        enriched["_weighted_error"] = f"Invalid weighted evidence: {error}"
    return enriched


def assess_record(path, data):
    if data.get("_weighted_error"):
        return None, data["_weighted_error"]
    checked = data.get("verification")
    contracts = {"lean_native_checked", "lean_native_checked_weighted_v1"}
    if (
        data.get("status") != "completed"
        or data.get("evidence") not in contracts
        or not isinstance(checked, dict)
        or checked.get("status") != data.get("evidence")
        or (
            data.get("evidence") == "lean_native_checked_weighted_v1"
            and not data.get("_weighted_sidecar")
        )
    ):
        return None, "Not independently checked / incomplete"
    try:
        value = RecordedValue.model_validate(checked)
    except ValueError:
        return None, "Invalid exact verification value"
    try:
        actual = hashlib.sha256(
            data.get("_candidate_path", path.parent / "candidate.json").read_bytes()
        ).hexdigest()
    except OSError:
        return None, "Candidate missing or unreadable"
    if actual != data.get("candidate_sha256"):
        return None, "Candidate hash mismatch — excluded from best"
    label = (
        "Weighted v1 compiled Lean recount; denominator is total weight⁴"
        if data.get("_weighted_sidecar")
        else "Recorded Lean recount"
    )
    return Fraction(
        value.numerator, value.denominator
    ), label + "; candidate hash matches"


def read_graphon_records(root):
    """Load separately-scoped exact graphon evidence without mixing rankings."""
    records = []
    for path in Path(root).glob("*/report.json"):
        try:
            data = json.loads(path.read_text())
            evidence = data.get("evidence")
            if evidence == "independent_standalone_compiled_lean_exact_nat_recount":
                checked = data["lean_recount"]
                candidate = Path(data["candidate"]["path"]).resolve()
                expected_hash = data["candidate"]["sha256"]
                level = "compiled Lean exact Nat recount"
                lean = True
            elif (
                data.get("status") == "completed"
                and evidence == "independent_generic_direct_ordered_index_u256_recount"
            ):
                checked = data["direct_recount"]
                candidate = Path(data["candidate"]["path"]).resolve()
                expected_hash = data["candidate"]["sha256"]
                level = "Independent direct exact native recount (U256)"
                lean = False
            elif (
                data.get("status") == "completed"
                and evidence
                == "independent_native_candidate_bound_histogram_plus_compiled_lean_exact_nat_arithmetic"
            ):
                checked = data["compressed_recount"]
                candidate = Path(data["candidate"]["path"]).resolve()
                expected_hash = data["candidate"]["sha256"]
                level = "Independent native recount + Lean certificate arithmetic"
                lean = False
            elif (
                data.get("status") == "completed"
                and evidence
                == "independent_group_verified_rooted_multiprime_crt_recount"
            ):
                checked = data["recount"]
                candidate = Path(data["candidate"]["path"]).resolve()
                expected_hash = data["candidate"]["sha256"]
                level = "Independent rooted CRT recount under verified transitivity"
                lean = False
            elif data.get("status") in {
                "independent_u256_ordered_recount_passed",
                "independent_generic_ordered_recount_passed",
            } and isinstance(data.get("actual_density"), str):
                checked = {"density": data["actual_density"]}
                candidate = (path.parent / "graphon-candidate.json").resolve()
                expected_hash = data["candidate_sha256"]
                level = (
                    "Independent exact native recount"
                    if data["status"] == "independent_generic_ordered_recount_passed"
                    else "Independent exact native recount (U256)"
                )
                lean = False
            else:
                continue
            if candidate.parent != path.parent.resolve():
                # A verifier may live in a separate report directory, but its
                # candidate must still remain under the reports tree.
                candidate.relative_to(Path(root).resolve())
            actual_hash = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError("candidate hash mismatch")
            value = Fraction(checked["density"])
            if not 0 <= value <= 1:
                raise ValueError("density outside [0,1]")
            records.append(
                dict(
                    path=path,
                    candidate=candidate,
                    value=value,
                    level=level,
                    lean=lean,
                    timing=data,
                    hypothesis=data.get("hypothesis", path.parent.name),
                    trust=data.get("trust")
                    or data.get("evidence")
                    or "Exact recount; scope not recorded",
                )
            )
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            ZeroDivisionError,
        ):
            continue
    return records


def render_timeline(verified, benchmark, graphons=()):
    references = [
        ("Published seed", Fraction(SEED_NUMERATOR, 768**4), "#778692", "3 4"),
        ("McKay reference", benchmark, "#b66c35", "7 4"),
        (
            "2026 announced <0.030139; not reproduced",
            Fraction(30139, 1000000),
            "#88539e",
            "10 3 2 3",
        ),
    ]
    observations = []
    timeline_entries = list(verified)
    approximate_times = False
    for record in graphons:
        data = dict(record["timing"])
        if not data.get("finished_at") and not data.get("started_at"):
            data["finished_at"] = datetime.fromtimestamp(
                record["path"].stat().st_mtime, timezone.utc
            ).isoformat()
            data["_timing_note"] = "report file timestamp; completion time not recorded"
            approximate_times = True
        timeline_entries.append(
            (record["path"], data, record["value"], record["level"])
        )
    for path, data, value, evidence in timeline_entries:
        try:
            stamp = datetime.fromisoformat(
                data.get("finished_at") or data["started_at"]
            )
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            if not data.get("finished_at"):
                duration = data.get("total_seconds", data.get("seconds"))
                if (
                    type(duration) not in (int, float)
                    or not math.isfinite(duration)
                    or duration < 0
                ):
                    continue
                stamp += timedelta(seconds=duration)
            label = path.parent.name + " · " + evidence
            if data.get("_timing_note"):
                label += " · " + data["_timing_note"]
            observations.append((stamp.astimezone(timezone.utc), value, label))
        except (TypeError, ValueError, OverflowError):
            continue
    observations.sort(key=lambda item: item[0])
    if not observations:
        return '<section class="chart"><h2>Best checked density over time</h2><p class="muted">No hash-valid checked results with completion timing yet.</p></section>'
    points, best = [], None
    for stamp, value, name in observations:
        best = value if best is None else min(best, value)
        points.append((stamp, best, name))
    values = [value for _, value, _ in points] + [
        value for _, value, _, _ in references
    ]
    lower, upper = min(values), max(values)
    span = upper - lower
    if not span:
        span = Fraction(1, 10**6)
    lower, upper = lower - span / 8, upper + span / 8
    start, end = points[0][0], points[-1][0]
    elapsed = (end - start).total_seconds()

    def position_time(stamp):
        return 150 + (
            float((stamp - start).total_seconds() / elapsed) * 760 if elapsed else 380
        )

    # Fraction arithmetic decides ordering and relative y-position; floats are
    # used only for rendering coordinates and human-readable axis labels.
    def position_density(value):
        return 210 - float((value - lower) / (upper - lower)) * 160

    line = f"M {position_time(points[0][0]):.3f} {position_density(points[0][1]):.3f}"
    for stamp, value, _ in points[1:]:
        line += f" H {position_time(stamp):.3f} V {position_density(value):.3f}"
    grid = []
    for i in range(5):
        value = lower + (upper - lower) * Fraction(i, 4)
        position = position_density(value)
        grid.append(
            f'<line x1="150" y1="{position:.3f}" x2="910" y2="{position:.3f}" stroke="#e3ecea"/><text x="136" y="{position + 4:.3f}" text-anchor="end">{float(value):.10f}</text>'
        )
    circles = "".join(
        f'<circle cx="{position_time(stamp):.3f}" cy="{position_density(value):.3f}" r="4" fill="#086a64"><title>{escape_html(stamp.isoformat())} · best {escape_html(value)} · {escape_html(name)}</title></circle>'
        for stamp, value, name in points
    )
    reference_lines = "".join(
        f'<line x1="150" y1="{position_density(value):.3f}" x2="910" y2="{position_density(value):.3f}" stroke="{color}" stroke-dasharray="{dash}"><title>{escape_html(label)}: {escape_html(value)}</title></line>'
        for label, value, color, dash in references
    )
    legend = "".join(
        f'<span style="color:{color}">━ {escape_html(label)} ({float(value):.10f})</span>'
        for label, value, color, _ in references
    )
    timing_note = (
        " Graphon reports without recorded completion times use their report file timestamps, labeled in tooltips."
        if approximate_times
        else ""
    )
    return f'''<section class="chart"><h2>Best checked density over time</h2><p class="muted">Lower is better. Step line is the cumulative best across independently checked, hash-matching binary, weighted, and graphon candidates. Hover points for the verification method.</p>
<div class="legend">{legend}</div>
<svg viewBox="0 0 980 270" role="img" aria-label="Best checked density over completion time, with published, McKay and unverified announcement reference lines">
{"".join(grid)}{reference_lines}
<path d="{line}" stroke="#086a64" stroke-width="2.5" fill="none"/>{circles}
<text x="150" y="240">{escape_html(start.strftime("%Y-%m-%d %H:%M:%S UTC"))}</text>
<text x="910" y="260" text-anchor="end">{escape_html(end.strftime("%Y-%m-%d %H:%M:%S UTC"))}</text>
</svg><p class="evidence">Completion time uses finished_at when present, otherwise started_at + duration.{timing_note} Hover points for exact fractions. Axis decimals are display only; invalid timing is omitted.</p></section>'''


def render_graphon_panel(records, out, benchmark):
    if not records:
        return """<section class="chart"><h2>Asymptotic graphon constructions</h2>
<p class="muted">No hash-valid exact graphon recounts recorded.</p></section>"""
    best = min(records, key=lambda record: record["value"])
    lean_records = [record for record in records if record["lean"]]
    best_lean = (
        min(lean_records, key=lambda record: record["value"]) if lean_records else None
    )
    announced = Fraction(30139, 1000000)

    def tile(label, record):
        if record is None:
            return f'<div class="tile"><span class="label">{escape_html(label)}</span><strong>Awaiting evidence</strong></div>'
        value = record["value"]
        links = " ".join(
            (
                render_link(record["candidate"], out, "Candidate"),
                render_link(record["path"], out, "Evidence report"),
            )
        )
        relation = float((value - benchmark) * 768**4)
        announced_gap = float(announced - value)
        return f"""<div class="tile graphon-tile"><span class="label">{escape_html(label)}</span>
<strong>{float(value):.15f}</strong><small>{escape_html(value)}</small>
<p>{escape_html(record["level"])}</p><small>{abs(relation):,.3f} fixed-768⁴ units {"below" if relation < 0 else "above"} McKay<br>
{announced_gap:.3e} below the rounded 0.030139 line</small><nav>{links}</nav></div>"""

    rows = "".join(
        f"""<tr><td>{escape_html(record["path"].parent.name)}</td>
<td>{float(record["value"]):.15f}</td><td>{escape_html(record["level"])}</td></tr>"""
        for record in sorted(records, key=lambda record: record["value"])
    )
    return f"""<section class="chart graphon"><h2>Asymptotic graphon constructions</h2>
<p class="muted">A graphon is a table of red-edge probabilities between groups of vertices. Its value is the limiting proportion of monochromatic K₄s in arbitrarily large graphs generated from that table. Lower is better; 0.030139 is about 3.0139%.</p>
<div class="graphon-summary">{tile("Strongest exact graphon recount", best)}{tile("Strongest compiled-Lean graphon recount", best_lean)}</div>
<aside class="notice"><strong>What is verified?</strong> Every value shown here has an exact recount of its saved candidate, with a matching file hash. Native recounts and compiled Lean recounts are labeled separately. <strong>What remains?</strong> The counting algorithm and the argument that actual graph colorings approach this limit have not been proved end-to-end in Lean. Compiled Lean execution checks a calculation; it is not that formal proof.</aside>
<p class="muted">The probabilistic existence argument has been reviewed. No displayed result is a global optimum or established world record. The January 2026 result is available here only as the rounded announcement <strong>c(4) &lt; 0.030139</strong>; its exact value remains unknown.</p>
<div class="table-wrap"><table><thead><tr><th>Artifact</th><th>Density</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></section>"""


def render_portfolio_panel(reports, out):
    """Display coordinator notes separately from scored evidence."""
    path = reports.parent / "research" / "portfolio-status.json"
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or not isinstance(data.get("lanes"), list):
            raise ValueError("invalid portfolio snapshot")
        rows = []
        for lane in data["lanes"]:
            if not isinstance(lane, dict):
                raise ValueError("invalid lane")
            rows.append(
                "<tr>"
                + "".join(
                    f"<td>{escape_html(lane.get(k, '—'))}</td>"
                    for k in ("lane", "status", "next_test")
                )
                + "</tr>"
            )
        return f"""<section class="chart"><h2>Current research portfolio</h2>
<p class="muted">Coordinator snapshot: {escape_html(data.get("updated_at", "unknown"))}.
{escape_html(data.get("limits", ""))} These are assignments and observations, not verified scores or live process telemetry.</p>
<div class="table-wrap"><table><thead><tr><th>Lane</th><th>State</th><th>Next discriminating test</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div><p class="evidence">{render_link(path, out, "Snapshot source")}</p></section>"""
    except (OSError, ValueError, TypeError):
        return '<aside class="notice">Portfolio snapshot unavailable; checked rankings are unaffected.</aside>'


def escape_html(value):
    return html.escape(str(value), quote=True)


def render_link(path, out, label):
    url = quote(os.path.relpath(path, out.parent), safe="/")
    # Prefix relative links so names containing a colon can never become a scheme.
    return f'<a href="{escape_html("./" + url)}">{escape_html(label)}</a>'


if __name__ == "__main__":
    main()
