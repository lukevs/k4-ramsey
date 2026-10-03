"""Data-derived print figures, with frozen input and output byte identities.

Every matrix figure is drawn from the published PPSS adjacency matrix or from
the algebraic rule, after checking that the two agree.  Each figure is written
as a PDF for the manuscript and a PNG for the Markdown documents.
"""

from __future__ import annotations

import base64
import json
import os
import re
from fractions import Fraction
from pathlib import Path

from ..artifacts import hash_file, read_json, write_json
from ..schemas.paper import FigureManifest
from .export import block_type

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "paper/figures"
BLUE, RED, INK, MUTED = "#2470bb", "#c5484b", "#212e3b", "#6b7785"
TYPE_COLORS = {"Z": "#e4e8ec", "X": "#e9b47a", "P": "#8a7cc8", "H": "#5aa27c"}

# Clebsch connection set S = {e1, e2, e3, e4, e1+e2+e3+e4}; e1 is the high bit.
CLEBSCH = [8, 4, 2, 1, 15]

# Upper bounds on c4 from explicit constructions or announcements.  The
# decimals are display values; exact values are in the manuscript.
HISTORY = [
    ("Random coloring", 1 / 32),
    ("Thomason 1989", 0.030304),
    ("Franek–Rödl 1993", 0.976501 / 32),
    ("Thomason 1997", 0.030291),
    ("Even-Zohar–Linial 2015", 1411 / 46592),
    ("PPSS 2022", 4551721 / 150994944),
    ("This paper", 0.030138887566497220),
]
LOWER = 0.0296
FINAL = [
    ("PPSS graph (2022)", 4551721 / 150994944, "published"),
    ("McKay (reported in PPSS)", 10486266368 / 768**4, "reported"),
    ("Feinstein (2026 talk)", 0.030139, "announced"),
    ("Clebsch base, optimal $p,h$", 0.030138977289665338, "ours"),
    ("Pentagon lift, $Q=9$", 4198776398959 / 139314069504000, "ours"),
    ("Pentagon lift, optimized", 0.030138903565399090, "ours"),
    ("One sign split", 0.030138895263623650, "ours"),
    ("Two sign splits (main)", 0.030138887566497220, "ours"),
]


def render() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "build/matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, ListedColormap

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "pdf.fonttype": 42,
            "savefig.facecolor": "white",
            "mathtext.fontset": "dejavusans",
        }
    )
    OUT.mkdir(exist_ok=True)

    # The explorer stores the PPSS matrix in Clebsch order: twelve families of
    # sixteen positions x in F_2^4, each position a fiber of four vertices.
    explorer_path = ROOT / "explainer/clebsch-explorer.html"
    match = re.search(r"const DATA = (\{[^\n]+\});", explorer_path.read_text())
    if not match:
        raise ValueError("explorer data not found")
    data = json.loads(match.group(1))
    ordered = np.unpackbits(
        np.frombuffer(base64.b64decode(data["bits"]), dtype=np.uint8),
        bitorder="little",
    ).reshape(768, 768)
    seed_path = ROOT / "data/published_cayley_768.json"
    seed = np.array([[int(v) for v in row] for row in read_json(seed_path)["red_rows"]])
    order = data["order"]
    if sorted(order) != list(range(768)) or not np.array_equal(
        ordered, seed[np.ix_(order, order)]
    ):
        raise ValueError("explorer matrix differs from the published construction")
    if not np.array_equal(seed, seed.T) or np.any(np.diag(seed)):
        raise ValueError("published construction is not symmetric with zero diagonal")

    z = np.bitwise_xor.outer(np.arange(16), np.arange(16))
    inside = np.isin(z, [0, *CLEBSCH])
    neighbor = inside & (z != 0)
    internal = np.repeat(np.repeat(~inside, 4, axis=0), 4, axis=1)
    if any(
        not np.array_equal(
            ordered[64 * i : 64 * i + 64, 64 * i : 64 * i + 64], internal
        )
        for i in range(12)
    ):
        raise ValueError(
            "one internal family differs from the fourfold Clebsch pattern"
        )

    families = [tuple(f) for f in data["families"]]
    types = [[block_type(u, v) for v in families] for u in families]
    if types != data["types"]:
        raise ValueError("group rule differs from explorer type table")
    fiber_red = ordered.reshape(192, 4, 192, 4).sum(axis=(1, 3))
    expected = {
        "Z": np.where(inside, 0, 16),
        "X": np.where(inside, 16, 0),
        "P": np.where(inside, 12, 0),
        "H": np.where(z == 0, 8, np.where(neighbor, 16, 0)),
    }
    for f in range(12):
        for g in range(12):
            block = fiber_red[16 * f : 16 * f + 16, 16 * g : 16 * g + 16]
            differs = block != expected[types[f][g]]
            if f == g:
                differs &= z != 0
            if types[f][g] == "P":
                # PPSS has all-red fibers at the same position when d_e = 0.
                same_e = families[f][1] == families[g][1]
                differs &= ~((z == 0) & (block == (16 if same_e else 12)))
            if differs.any():
                raise ValueError(f"PPSS fiber counts differ from the rule at {f},{g}")

    minimum_path = ROOT / "paper/data/base-minimum.json"
    minimum = read_json(minimum_path)["interior"]
    if len(minimum) != 1:
        raise ValueError("expected one certified base-family minimum")
    p, h = [float(sum(Fraction(v) for v in minimum[0][key]) / 2) for key in ("p", "h")]

    cmap = LinearSegmentedColormap.from_list("red_probability", [BLUE, "#f6f1ee", RED])
    cmap.set_bad("#c9cfd5")
    outputs = {}

    def save(fig, name):
        for suffix, extra in ((".pdf", {}), (".png", {"dpi": 220})):
            path = OUT / f"{name}{suffix}"
            fig.savefig(
                path,
                bbox_inches="tight",
                pad_inches=0.06,
                metadata={"CreationDate": None, "ModDate": None}
                if suffix == ".pdf"
                else {"Software": None},
                **extra,
            )
            outputs[path.name] = {
                "sha256": hash_file(path),
                "bytes": path.stat().st_size,
            }
        plt.close(fig)

    def matrix(ax, values, stride=None, title="", missing_diagonal=False, lw=0.4):
        values = np.array(values, dtype=float)
        if missing_diagonal:
            np.fill_diagonal(values, np.nan)
        im = ax.imshow(
            values, cmap=cmap, vmin=0, vmax=1, interpolation="nearest", rasterized=True
        )
        n = len(values)
        if stride:
            for pos in np.arange(stride - 0.5, n - 1, stride):
                ax.axhline(pos, color="white", lw=lw)
                ax.axvline(pos, color="white", lw=lw)
        ax.set_title(title, loc="left", pad=6)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_linewidth(0.5)
            spine.set_color(MUTED)
        return im

    def red_blue_legend(fig, y, labels=("blue", "red"), x=0.5):
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=BLUE),
            plt.Rectangle((0, 0), 1, 1, color=RED),
        ]
        fig.legend(
            handles,
            labels,
            loc="center",
            bbox_to_anchor=(x, y),
            ncol=len(labels),
            frameon=False,
            fontsize=7.5,
            handlelength=1.2,
            columnspacing=1.6,
        )

    def bit_label(x):
        return format(x, "04b")

    # Figure 1: the Clebsch graph, drawn around the vertex 0000.
    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(6.4, 3.0), gridspec_kw={"width_ratios": [1.15, 1]}
    )
    angle = {k: np.pi / 2 - 2 * np.pi * k / 5 for k in range(5)}
    pos = {0: (0.0, 0.0)}
    for k, s in enumerate(CLEBSCH):
        pos[s] = (np.cos(angle[k]), np.sin(angle[k]))
    for k in range(5):
        near = CLEBSCH[k] ^ CLEBSCH[(k + 1) % 5]
        mid = angle[k] - np.pi / 5
        pos[near] = (2.05 * np.cos(mid), 2.05 * np.sin(mid))
        far = CLEBSCH[(k + 4) % 5] ^ CLEBSCH[(k + 1) % 5]
        pos[far] = (2.75 * np.cos(angle[k]), 2.75 * np.sin(angle[k]))
    if sorted(pos) != list(range(16)):
        raise ValueError("Clebsch layout does not place every vertex once")
    edges = [(x, y) for x in range(16) for y in range(x) if (x ^ y) in CLEBSCH]
    if len(edges) != 40:
        raise ValueError("Clebsch graph should have forty edges")
    for x, y in edges:
        layer = 0 if 0 in (x, y) else 1 if (x in CLEBSCH or y in CLEBSCH) else 2
        ax.plot(
            *zip(pos[x], pos[y]),
            color=BLUE,
            lw=[1.4, 1.0, 0.8][layer],
            alpha=[0.95, 0.75, 0.6][layer],
            zorder=1,
        )
    for x, (px, py) in pos.items():
        ring = 0 if x == 0 else 1 if x in CLEBSCH else 2
        ax.text(
            px,
            py,
            bit_label(x),
            ha="center",
            va="center",
            fontsize=6.2,
            family="DejaVu Sans Mono",
            color=INK,
            zorder=3,
            bbox={
                "boxstyle": "round,pad=0.28,rounding_size=0.5",
                "facecolor": ["#fbe9e9", "#e3edf7", "#ffffff"][ring],
                "edgecolor": INK,
                "linewidth": 0.7,
            },
        )
    ax.set_aspect("equal")
    ax.set_xlim(-3.15, 3.15)
    ax.set_ylim(-2.75, 3.0)
    ax.set_axis_off()
    ax.set_title("(a) Clebsch graph: $x\\sim y$ iff $x+y\\in S$", loc="left", pad=4)
    clebsch_color = np.where(inside, 0.0, 1.0)
    matrix(
        bx, clebsch_color, title="(b) As a coloring of $K_{16}$", missing_diagonal=True
    )
    bx.set_xticks(
        range(16),
        [bit_label(x) for x in range(16)],
        rotation=90,
        fontsize=5.2,
        family="DejaVu Sans Mono",
    )
    bx.set_yticks(
        range(16),
        [bit_label(x) for x in range(16)],
        fontsize=5.2,
        family="DejaVu Sans Mono",
    )
    bx.tick_params(length=0, pad=1.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.12, wspace=0.12)
    red_blue_legend(fig, 0.03, ("blue: Clebsch edge", "red: non-edge"), x=0.74)
    save(fig, "clebsch-graph")

    # Figure 2: the PPSS graph before and after reordering.
    fig, axes = plt.subplots(1, 3, figsize=(6.7, 2.55))
    matrix(axes[0], seed, title="(a) PPSS, published order", missing_diagonal=True)
    matrix(axes[1], ordered, 64, "(b) Same graph, Clebsch order", True, lw=0.6)
    matrix(axes[2], ordered[:64, :64], 4, "(c) One family (64 vertices)", True, lw=0.3)
    axes[1].set_xticks(np.arange(31.5, 768, 64), range(1, 13), fontsize=5.5)
    axes[1].set_yticks(np.arange(31.5, 768, 64), range(1, 13), fontsize=5.5)
    axes[1].tick_params(length=0, pad=1.5)
    axes[2].set_xticks(
        np.arange(1.5, 64, 4),
        [bit_label(x) for x in range(16)],
        rotation=90,
        fontsize=4.2,
        family="DejaVu Sans Mono",
    )
    axes[2].set_yticks(
        np.arange(1.5, 64, 4),
        [bit_label(x) for x in range(16)],
        fontsize=4.2,
        family="DejaVu Sans Mono",
    )
    axes[2].tick_params(length=0, pad=1)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.13, wspace=0.16)
    red_blue_legend(fig, 0.035)
    save(fig, "ppss-reordered")

    # Figure 3: the twelve-family rule and the four position patterns.
    fig = plt.figure(figsize=(6.7, 3.45))
    gs = fig.add_gridspec(
        2, 4, width_ratios=[1.25, 1.25, 1, 1], wspace=0.35, hspace=0.42
    )
    ax = fig.add_subplot(gs[:, 0])
    codes = {name: i for i, name in enumerate(TYPE_COLORS)}
    ax.imshow(
        [[codes[t] for t in row] for row in types],
        cmap=ListedColormap(list(TYPE_COLORS.values())),
        vmin=0,
        vmax=3,
    )
    for i in range(12):
        for j in range(12):
            ax.text(
                j,
                i,
                types[i][j],
                ha="center",
                va="center",
                fontsize=6,
                color=INK if types[i][j] in "ZX" else "white",
            )
    names = ["".join(map(str, (a, e, s))) for a, e, s in families]
    ax.set_xticks(
        range(12), names, rotation=90, fontsize=5.3, family="DejaVu Sans Mono"
    )
    ax.set_yticks(range(12), names, fontsize=5.3, family="DejaVu Sans Mono")
    ax.tick_params(length=0, pad=1.5)
    for pos6 in (5.5,):
        ax.axhline(pos6, color="white", lw=1.4)
        ax.axvline(pos6, color="white", lw=1.4)
    ax.set_title("(a) Family-pair types", loc="left", pad=6)

    # Family graph: one square per a in Z_3, corners (e, s).
    ax = fig.add_subplot(gs[:, 1])
    centers = [
        (0.0, 1.05),
        (-0.95, -0.55),
        (0.95, -0.55),
    ]
    corner = {(0, 0): (-1, 1), (1, 0): (1, 1), (0, 1): (-1, -1), (1, 1): (1, -1)}
    fpos = {
        f: (
            centers[f[0]][0] + 0.27 * corner[(f[1], f[2])][0],
            centers[f[0]][1] + 0.27 * corner[(f[1], f[2])][1],
        )
        for f in families
    }
    for i, f in enumerate(families):
        for j, g in enumerate(families):
            t = types[i][j]
            if j <= i or t == "Z":
                continue
            ax.plot(
                *zip(fpos[f], fpos[g]),
                color=TYPE_COLORS[t],
                lw=1.6 if t != "X" else 0.9,
                alpha=1 if t != "X" else 0.85,
                zorder=1 if t == "X" else 2,
            )
    for f, (px, py) in fpos.items():
        ax.scatter(px, py, s=36, color="white", edgecolor=INK, lw=0.7, zorder=3)
    for a, (cx, cy) in enumerate(centers):
        ax.text(
            cx,
            cy + (0.5 if a == 0 else -0.52),
            f"$a={a}$",
            ha="center",
            va="center",
            fontsize=7,
            color=MUTED,
        )
    for t, label in (("X", "X"), ("P", "P"), ("H", "H")):
        ax.plot([], [], color=TYPE_COLORS[t], lw=1.6, label=label)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=3,
        frameon=False,
        fontsize=7,
        handlelength=1.4,
    )
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.2, 1.6)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("(b) Family graph", loc="left", pad=6)

    patterns = {
        "Z": (~inside).astype(float),
        "X": inside.astype(float),
        "P": p * inside,
        "H": np.where(z == 0, h, np.where(inside, 1, 0)),
    }
    for idx, (name, values) in enumerate(patterns.items()):
        ax = fig.add_subplot(gs[idx // 2, 2 + idx % 2])
        im = matrix(ax, values, title=f"({chr(99 + idx)}) Pattern {name}")
        for spine in ax.spines.values():
            spine.set_color(TYPE_COLORS[name] if name != "Z" else MUTED)
            spine.set_linewidth(1.6 if name != "Z" else 0.5)
    fig.subplots_adjust(left=0.04, right=0.99, top=0.93, bottom=0.17)
    cax = fig.add_axes([0.66, 0.065, 0.3, 0.022])
    bar = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=[0, h, p, 1])
    bar.ax.set_xticklabels(["0", "$h$", "$p$", "1"], fontsize=7)
    bar.outline.set_linewidth(0.4)
    fig.text(0.635, 0.073, "red prob.", ha="right", va="center", fontsize=7)
    save(fig, "family-rule")

    # Figure 4: the two refinements, with the Q = 9 pentagon example.
    fig = plt.figure(figsize=(6.7, 2.45))
    ax = fig.add_axes([0.0, 0.08, 0.2, 0.78])
    pent = {
        a: (
            np.cos(np.pi / 2 - 2 * np.pi * a / 5),
            np.sin(np.pi / 2 - 2 * np.pi * a / 5),
        )
        for a in range(5)
    }
    for a in range(5):
        b = (a + 1) % 5
        ax.plot(*zip(pent[a], pent[b]), color=TYPE_COLORS["P"], lw=2.0, zorder=1)
        c = (a + 2) % 5
        ax.plot(
            *zip(pent[a], pent[c]), color="#d5d9de", lw=0.8, zorder=0, ls=(0, (2, 2))
        )
    for a, (px, py) in pent.items():
        ax.scatter(px, py, s=150, color="white", edgecolor=INK, lw=0.8, zorder=2)
        ax.text(px, py, str(a), ha="center", va="center", fontsize=7.5, zorder=3)
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.25, 1.3)
    ax.set_axis_off()
    ax.set_title("(a) Five labels in $\\mathbb{Z}_5$", loc="left", pad=4, fontsize=8.5)

    def labelled(ax, values, text, title, ticks):
        matrix(ax, values, len(values), title)
        n = len(values)
        ax.set_xticks(range(n), ticks, fontsize=6.5)
        ax.set_yticks(range(n), ticks, fontsize=6.5)
        ax.tick_params(length=0, pad=1.5)
        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    text[i][j],
                    ha="center",
                    va="center",
                    fontsize=6.3,
                    color="white" if values[i][j] in (0, 1) else INK,
                )
        for pos5 in np.arange(0.5, n - 1, 1):
            ax.axhline(pos5, color="white", lw=0.6)
            ax.axvline(pos5, color="white", lw=0.6)

    on = np.isin((np.arange(5)[:, None] - np.arange(5)) % 5, [1, 4])
    ax = fig.add_axes([0.235, 0.13, 0.2, 0.66])
    labelled(
        ax,
        np.where(on, 4 / 9, 1.0),
        [["4/9" if v else "1" for v in r] for r in on],
        "(b) Active $P$ block",
        range(5),
    )
    ax = fig.add_axes([0.475, 0.13, 0.2, 0.66])
    labelled(
        ax,
        np.where(on, 0.0, 8 / 9),
        [["0" if v else "8/9" for v in r] for r in on],
        "(c) $H$ block",
        range(5),
    )
    ax = fig.add_axes([0.745, 0.25, 0.2, 0.47])
    matrix(ax, [[0.72, 0.48], [0.48, 0.72]], 1, "(d) Sign split")
    ax.set_xticks([0, 1], ["+", "−"], fontsize=9)
    ax.set_yticks([0, 1], ["+", "−"], fontsize=9)
    ax.tick_params(length=0, pad=2)
    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                "$w+a$" if i == j else "$w-a$",
                ha="center",
                va="center",
                fontsize=8,
            )
    save(fig, "refinements")

    # Figure 5: upper bounds, with a zoom on the recent constructions.
    fig, (ax, bx) = plt.subplots(
        1,
        2,
        figsize=(6.7, 2.7),
        gridspec_kw={"width_ratios": [1, 1.35], "wspace": 0.75},
    )
    ys = np.arange(len(HISTORY))[::-1]
    ax.axvspan(0.0293, LOWER, color="#e4e8ec", lw=0)
    ax.text(
        0.02945,
        (ys[0] + ys[-1]) / 2,
        "excluded: $c_4>0.0296$",
        ha="center",
        va="center",
        rotation=90,
        fontsize=6,
        color=MUTED,
    )
    for y, (label, value) in zip(ys, HISTORY):
        ax.plot([0.0293, value], [y, y], color="#d5d9de", lw=0.8, zorder=0)
        ax.scatter(
            value, y, s=20, color=RED if label == "This paper" else INK, zorder=2
        )
    ax.set_yticks(ys, [label for label, _ in HISTORY], fontsize=6.8)
    ax.get_yticklabels()[-1].set_color(RED)
    ax.set_xlim(0.0293, 0.0315)
    ax.set_xticks([0.0295, 0.0300, 0.0305, 0.0310, 0.0315])
    ax.set_xticklabels(["0.0295", "0.0300", "0.0305", "0.0310", "0.0315"], fontsize=6.3)
    ax.set_title("(a) Upper bounds on $c_4$", loc="left", pad=6)
    ys = np.arange(len(FINAL))[::-1]
    lo, hi = 0.0301386, 0.0301452
    style = {
        "published": dict(color=INK, marker="o"),
        "reported": dict(color=MUTED, marker="o"),
        "announced": dict(color=MUTED, marker="<"),
        "ours": dict(color=RED, marker="o"),
    }
    for y, (label, value, kind) in zip(ys, FINAL):
        ax2 = bx
        ax2.plot([lo, value], [y, y], color="#d5d9de", lw=0.8, zorder=0)
        ax2.scatter(value, y, s=22, zorder=2, **style[kind])
        ax2.text(
            value + 2.0e-7,
            y,
            f"{(value - 0.03) * 1e6:.3f}" if kind != "announced" else "< 139",
            va="center",
            fontsize=5.8,
            color=MUTED,
        )
    bx.set_yticks(ys, [label for label, _, _ in FINAL], fontsize=6.8)
    for tick, (_, _, kind) in zip(bx.get_yticklabels(), FINAL):
        if kind == "ours":
            tick.set_color(RED)
    bx.set_xlim(lo, hi)
    ticks = [0.030139, 0.030141, 0.030143, 0.030145]
    bx.set_xticks(ticks, ["139", "141", "143", "145"], fontsize=6.3)
    bx.set_xlabel("$(\\mathrm{density}-0.03)\\times10^{6}$", fontsize=6.8, labelpad=2)
    bx.set_title("(b) Recent constructions", loc="left", pad=6)
    for a in (ax, bx):
        a.tick_params(length=2, pad=2, width=0.5)
        for side in ("top", "right"):
            a.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            a.spines[side].set_linewidth(0.5)
    save(fig, "bounds")

    manifest = FigureManifest(
        schema="k4-paper-figures-v1",
        source_sha256={
            str(path.relative_to(ROOT)): hash_file(path)
            for path in [explorer_path, seed_path, minimum_path, Path(__file__)]
        },
        files=outputs,
        checks=[
            "768x768 explorer matrix equals permuted published data",
            "all twelve internal families match the fourfold Clebsch pattern",
            "family type table equals the algebraic rule",
            "PPSS fiber red counts follow the rule, with P same-position 16 or 12",
        ],
    )
    write_json(OUT / "manifest.json", manifest)
    print(f"Generated {len(outputs)} checked manuscript figures in {OUT}.")
