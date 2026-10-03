# Round 4 root synthesis — the pattern in the small gains (23:08 UTC)

Search-side values except where lane P audited (d4763, E4-3840, E7-768). B192 continuous
2-level optimum 0.0301389773 is the reference.

| Construction | classes | gain vs B192 |
|---|---:|---:|
| E4 G/K, K=120 | 384 | 3.2e-8 |
| E4 K=60 / E7 Z2^2 lift | 768 | 4.2e-8 / 5.0e-8 |
| Z5 lift C (3 levels) / d4763 | 960 | 5.2e-8 / 7.4e-8 |
| E4 K=24 / E5 split depth 1 | 1920 | 6.1e-8 / 8.2e-8 |
| E4 K=12 (audited) / E5 depth 2 | 3840 | 8.2e-8 / 9.0e-8 |
| E5 depth 3 (partial, float) | 7680 | 9.4e-8 |

## Observations

1. **One mechanism in several guises.** Every gain after B192 is a lift / cover of B192 that
   adds a hidden latent correlation to its *fractional* edges only (Z5 voltages, Z2 towers,
   E5 +-A sign splits, E4 coset symmetry breaking, E7's Z2^2 lift). 0/1 entries never move.
2. **The gain is cubic, driven by triangles of fractional edges.** Quadratic terms vanish
   identically for these moves (E5; E9 tower; L2's refinement-stability remark, cf.
   Csóka–Hubai–Lovász). Leading term T3 = sum over fractional triangles uvw of
   A_uv A_vw A_wu * sum_z (p_uz p_vz p_wz - q_uz q_vz q_wz), opposed by a quartic 4-cycle term.
   In B192 all active fractional triangles are PPH (R2); the Z5 lift is a +-1 holonomy sign
   field on them, frustrated (E10: symmetry order 2).
3. **Diminishing returns, roughly geometric in log(classes).** E5 per-doubling gains
   8.3e-9, 7.7e-9, ~3.9e-9 (partial). Geometric extrapolation (ratio 0.5–0.7) puts the limit
   of this route near 0.03013887–0.03013888, i.e. ~1.0–1.1e-7 below B192. The 0.030138 target
   needs ~9e-7 more: roughly 10x what this mechanism can plausibly deliver.
4. **Latent quality matters more than latent size.** The single Z5 step (C5 = Paley(5), the
   triangle-free 2-colouring of K5) gave 5e-8 in one move; Z2 splits give ~8e-9 each. The
   latent kernel's own triangle structure enters T3; a Ramsey-critical latent (no
   monochromatic triangles) is the best-performing one seen.
5. **Consequence for the convergence story.** The routes "converge" because they are the same
   mechanism on the same base, so their agreement is evidence that B192 is a strong attractor,
   not independent evidence of the value. The plateau is bounded by B192's fractional support
   (2496 fractional entries of 36672; 880 active triangles).

## Implied next hypotheses

- H-R5-a: enlarge the fractional support first. Open cheapest 0/1 levels (E11 slacks: H on S
  9.2e-6, off-C 1.8e-5) *jointly* with a lift; predict the new PPP/PPH triangles raise T3
  enough to overcome the first-order cost. Disconfirm: first-order cost > cubic gain at all eps.
- H-R5-b: Ramsey-critical latent kernels: Paley(9) on Z3^2, Paley(13), Paley(17), Clebsch /
  Greenwood–Gleason on F2^4 as the lift latent instead of C5, with holonomy-informed starts
  (E9's random starts could not even rediscover Z5, so starts must be informed).
- H-R5-c: analytic upper envelope. Bound the total achievable lift gain from B192 by
  optimising T3/T4 over latent kernels (spectral: triangle sum lambda^3 vs 4-cycle
  sum lambda^4) to predict the plateau limit; if it is above 0.030138, retire B192-lift
  routes for the record target and redirect to new bases (basin census).
