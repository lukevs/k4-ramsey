# Round 4 — lane L1: literature status of c4 bounds

Search window: 2026-09-27, 22:29–22:40 UTC. Web/API searches only. No compute
jobs, no contact with anyone, no commits. This builds on `prior-art-round2.md`,
`adjacent-methods.md` §5 and `adjacent-structural-mechanisms.md`, which
already covered the arXiv/Crossref/OpenAlex/DataCite author searches, Even-Zohar's
GitHub, and the Technion library entry point. None of those are repeated here
except where they were re-queried to check for newer entries.

Our incumbent (d4763fef): F = 16900934504649027287619486865996291 /
560768060721761383881293603555770368 ≈ **0.03013890356539909**.

## Source table

| # | Source | Date | Claim (c4 = min density of monochromatic K4 among 4-sets) | Exact value | Construction public? | URL | Evidence type |
|---|---|---|---|---|---|---|---|
| U1 | Parczyk–Pokutta–Spiegel–Szabó, *New Ramsey Multiplicity Bounds and Search Heuristics*, FoCM 25(5):1777–1814 | arXiv v1 2022-06-08, v3 2024-09-13; FoCM online 2024-08-26 | Thm 1.1: "c4 ≤ 4551721·2^−24·3^−2 < 0.030145" | 4551721/(2^24·9) = 0.030144857035742864 | Yes. graph6 strings on Zenodo (graphs.zip) | https://arxiv.org/abs/2206.04036 ; https://doi.org/10.1007/s10208-024-09675-6 ; https://zenodo.org/records/6602512 | published (peer-reviewed) |
| U2 | McKay, as reported in the PPSS v3 closing "Note", citing "[58] McKay, B. (2024). Personal communication." | PPSS v3, 2024-09-13 | "The most successful attempt created a graph with value 10486266368/768^4 = 0.0301422734319 … McKay's graph has 768 vertices, 148724 edges, 536 vertices of degree 387, 232 vertices of degree 388, and … a trivial automorphism group." Local search that flips pairs, starting from the PPSS 768-vertex Cayley graph. | 10486266368/768^4 ≈ 0.030142273431942788 | **No.** No adjacency matrix in the PPSS Zenodo record. McKay's public combinatorial-data pages (users.cecs.anu.edu.au/~bdm/data/, graphs.html, extremal.html) had no multiplicity entry when grepped. | https://arxiv.org/abs/2206.04036v3 (the Note just before the Acknowledgements) | reported in a published paper as a personal communication; no witness |
| U3 | Feinstein (with Even-Zohar), RSA 2025 contributed talk, *Improved Constructions for Ramsey Multiplicities* | 2025-08-07 (Thursday, 17:00–17:25, Vienna) | Verbatim: "we provide random constructions that improve the upper bounds on \(c_4\) and \(c_5\). Our constructions are substantially more symmetric and structured than the so-far best known ones, due to Parczyk et al. (2022) …" | none | No. The program PDF (assets/pdfs/RSA2025_Program.pdf) lists only the title and time slot. No slides or book of abstracts are linked. | https://www.dmg.tuwien.ac.at/rsa2025/ | announcement |
| U4 | Feinstein, Technion Combinatorics Seminar (MSc graduation talk; "MSc advisor: Chaim Even Zohar"), room 814 Amado | 2026-01-21, 14:30 (page first posted 2025-10-21, last modified 2026-01-19) | Verbatim: "Introducing new methods and ideas, we provide randomized constructions that improve these bounds, showing c(4) < 0.030139 and c(5) < 0.001652. Our constructions are more structured, symmetric, and human-friendly than the previous ones …" | none (a rounded inequality only) | No slides, video, thesis or code linked | https://math.technion.ac.il/events/noam-feinstein/ | announcement |
| U5 | Even-Zohar–Linial, *A Note on the Inducibility of 4-vertex Graphs*, Graphs & Combin. 31(5) (2015) 1367–1380 | arXiv 2013-12-04 / 2014-10-21 | c4 < 0.030285 (1/33.0205) via nested composition | yes (in paper) | yes (formula) | https://arxiv.org/abs/1312.1205 | published |
| U6 | Thomason 1989 (JLMS) / 1997 (Combinatorica 17:125–134) | 1989/1997 | c4 < 0.030304, then < 0.030291 | yes | yes | https://doi.org/10.1007/BF01196136 | published |
| L1 | Grzesik–Lee–Lidický–Volec, *On tripartite common graphs*, CPC 31(5) (2022) 907–923 | arXiv 2020-12-03 / 2022-04-27 | Concluding remarks: "A direct flag algebra calculation using expressions with 9-vertex subgraph densities yields C(K4) ≥ 1/33.77 ≈ 0.0296, which is a slight improvement over previously known lower bound 1/33.9739 ≈ 0.0294343" | 1/33.77 is a rounded statement. No exact rational or certificate appears in the text. | n/a | https://arxiv.org/abs/2012.02057 ; https://doi.org/10.1017/s0963548322000074 | published, but as a remark without a stated certificate. PPSS (2024) cite it as "the best known lower bound stands at 0.0296 < c4". |
| L2 | Nieß, arXiv 1207.4714 | 2012-07-19 | c4 > 204603019/7112448000 > 0.02876689 | yes | n/a | https://arxiv.org/abs/1207.4714 | preprint (superseded) |
| X1 | AlphaEvolve repository of problems (Georgiev–Gómez-Serrano–Tao–Wagner, arXiv 2511.02864) | 2025-11 | The full list of 67 experiment directories was read through the GitHub tree API. None is about Ramsey multiplicity or monochromatic K4. The nearest are `edges_vs_triangles`, `sidorenko_conjecture` and `hypergraph_turan_tetrahedron`. | — | — | https://github.com/google-deepmind/alphaevolve_repository_of_problems | checked, not about this problem |

## Searches with no hit for a Feinstein–Even-Zohar artifact (not located ≠ does not exist)

- arXiv API, re-queried now. `au:"Even-Zohar"` lists nothing after 2025-08-04 (*Plabic Tangles…*), and nothing on Ramsey multiplicity. `au:Feinstein_N` and `au:Feinstein AND cat:math.CO` return nothing. `abs:"Ramsey multiplicity"` sorted by date (through 2026-09-16) shows no c4/c5 construction paper. `abs:"monochromatic K_4"` shows nothing after PPSS.
- OpenAlex, searching `"Ramsey multiplicities"` from 2024-06 onward and `monochromatic K4` from 2023 onward: no Feinstein or Even-Zohar record and no new c4 upper or lower bound. The only hits are unrelated (odd cycles, ordered graphs, rainbow, and AI-generated Zenodo items about small K_n).
- Zenodo, searching the phrases `"Ramsey multiplicity"`, `"Ramsey multiplicities"` and `"monochromatic K_4"`: only PPSS 6602512, KPS triangle-multiplicity code, and unrelated or irrelevant records.
- GitHub repository search "ramsey multiplicity": only `FordUniver/kps_trianglemult`.
- Technion math site search: its search does not index events, so nothing further was found. The Technion thesis repository was not retrievable in round 2 and was not retried. **The MSc thesis is presumably complete (graduation seminar Jan 2026) but was not located.**
- General web searches: `"0.030139" Ramsey`, `"Feinstein" "Even-Zohar" Ramsey`, and talk/slides/video queries found no slides, video, preprint or thesis PDF.
- Semantic Scholar: rate-limited (HTTP 429), so not checked this pass.

## Other 2024–2026 upper-bound improvements

None located beyond U2–U4. LLM and AI-discovery work in 2025–26 touches Ramsey *numbers*:
- RamseyGadgets, arXiv 2608.14999
- Reinforced Generation…Ramsey Numbers, arXiv 2603.09172
- Doubly Saturated Ramsey Graphs, arXiv 2604.21187
- AlphaEvolve's R(·,·) work

None of these touches the K4 multiplicity constant. This is a not-located result, not proof of absence.

## Current best lower bound

**c4 ≥ 1/33.77 ≈ 0.0296**, from L1 (GLLV, CPC 2022). This is the value PPSS cite as the best known. No later improvement was located. Gap to our value: ≈ 5.27e-4.

## Venue and precedent for a write-up

- **PPSS**, published in *Foundations of Computational Mathematics*. Upper-bound witnesses were released as graph6 strings, with a description file, on Zenodo (DOI 10.5281/zenodo.6602512). Lower bounds came with flagmatic certificates (cited as doi.org/10.5281/zenodo.6364588). This is the closest precedent: a computer-found construction plus a public witness and an archived dataset.
- **Even-Zohar–Linial**, published in *Graphs and Combinatorics*: an exact rational limit derived by hand from a profile recurrence.
- **Thomason**: JLMS (1989) and Combinatorica (1997).
- **Kiem–Pokutta–Spiegel**, four-colour triangle multiplicity: JCTB 179 (2026). Code is on GitHub and Zenodo (10683661), so JCTB accepts computer-assisted multiplicity results with archived code.
- **McKay's improvement** was never published on its own. It appears only as a closing note in PPSS v3. This matters: an improvement of ~1e-6 was treated as note-worthy, not paper-worthy, on its own.

Implication for us: a graphon/step-matrix witness is new in format relative to PPSS's finite graph6 cores. The write-up should ship:
- the rational step matrix and weights, with a SHA;
- an independent exact recount script;
- optionally, the Lean check;
- an archive (Zenodo-style).

## Verdict

1. Our value 0.03013890356539909 is **strictly below every located public upper bound that has a stated value**:
   - PPSS, published: 0.0301448570. We are lower by 5.95e-6.
   - McKay, reported with no witness: 0.0301422734. We are lower by 3.37e-6.
   - Feinstein–Even-Zohar's rounded announcement, c4 < 0.030139: our value is 9.64e-8 below that threshold.
2. **We cannot establish that we beat Feinstein–Even-Zohar.** Their announced statement "c(4) < 0.030139" is consistent with any true value in (0.0296, 0.030139), including values below ours. No exact value, construction, preprint, slides, video, thesis or code was **located**. That is a search limitation, not evidence that it does not exist. The work was presented twice (Aug 2025, Jan 2026) and an MSc thesis very likely exists at the Technion.
3. Also unknown:
   - whether their "randomized, structured, symmetric" construction coincides with our stochastic-block mechanism (prior-art-round2 notes that softening a structured blow-up has precedent in Thomason 1997);
   - McKay's actual graph;
   - a certificate for GLLV's 1/33.77 lower bound.
4. No other 2024–2026 upper-bound improvement for c4 was located. This includes the AlphaEvolve problem list, where the problem is absent. The best lower bound remains 0.0296 (GLLV 2022).

Safe public claim: "improves the best published bound (PPSS 2024) and the value reported by McKay (PPSS v3). It is below the rounded threshold announced by Feinstein and Even-Zohar (2025/26), whose exact value we could not locate." Do not claim a record against Feinstein and Even-Zohar.
