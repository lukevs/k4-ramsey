# Round 5 lane F4: provable statements for the paper

Window 23:15–00:15 UTC, 2026-09-27/28. Local only, single-threaded, no commits, nothing submitted.
- Code: `experiments/round5_F4/`.
- Receipts: `reports/round5-F4-{poly,crit,kkt-float,kkt-cert}-001/`.

Process note: the Task 1 jobs (`poly.py`, `crit.py`, each under 10 s) and the first Task 2 float run
(`kkt_float.py`, 23 s) ran at 23:12–23:16 UTC. That is up to 3 minutes before the window opened.
`kkt_float.py` also ran without pinning BLAS to one thread. All later jobs set `VECLIB_MAXIMUM_THREADS=1`
(and the OMP/OpenBLAS variables), and every job stayed under 10 minutes.

## Hypothesis record

- **H-R5-F4a (L2 item 1).**
  - Claim: F(p,h) = t(K4,W)+t(K4,1-W) on the B192 Clebsch-design family is a rational polynomial. It has a unique global minimum on [0,1]^2, at the continuous optimum (0.779181, 0.534265).
  - Disconfirmation: a second interior critical point with a value that is equal or lower, or a boundary value below it.
- **H-R5-F4b (L2 item 2).**
  - Claim: the E4-3840 kernel is (near) a strict local minimum of f in its 456-parameter G/K-invariant orbital family. That means strict complementarity on the 433 bound orbitals and a positive-definite 23×23 reduced Hessian.
  - Disconfirmation: a wrong-signed bound gradient, or a non-positive reduced Hessian eigenvalue at the certified stationary point.

---

## Theorem A (B192 family: exact polynomial and unique global minimum)

**Setting.** Let Q = F2^4, C = {0, e1, e2, e3, e4, 1111}, and use the 12-block type matrix T of
`experiments/round4_E11/rule.json` (round 4 lane E11). The graphon W_{p,h} on Q×[12] with 192 equal parts is

  W((x,s),(y,t)) = g_{T[s,t]}(x+y), with
  - g_Z = 1_{off C},
  - g_X = 1_C,
  - g_P = p·1_C,
  - g_H = h·1_{0} + 1_{C∖0}.

B192 is the member of this family with p = 51064/65536 and h = 35015/65536.

**(A1) Exact polynomial.** F(p,h) := t(K4,W_{p,h}) + t(K4,1−W_{p,h}) equals

```
F(p,h) = ( 251655 − 97344 p + 66888 p^2 − 7008 p^3 + 1224 p^4
           − 6552 h + 9216 p h − 4176 p^2 h + 2304 p^3 h − 144 p^4 h
           + 990 h^2 − 576 p h^2 + 648 p^2 h^2 − 288 p^3 h^2 + 72 p^4 h^2
           − 16 h^3 + 3 h^4 ) / 7077888
```

Here 7077888 = 2^18·27. F has total degree 6, and degree 4 in each of p and h.

**(A2) Unique critical point.**
- ∇F = 0 has exactly one real solution (p*, h*) in all of R^2, and it lies inside (0,1)^2.
- p* is the unique real root of the irreducible degree-17 polynomial

  g(p) = 288p^17 − 4968p^16 + 48528p^15 − 326808p^14 + 1640880p^13 − 6374994p^12 + 19669380p^11
         − 49113990p^10 + 100709306p^9 − 170524126p^8 + 238109998p^7 − 272230472p^6 + 252306699p^5
         − 183872508p^4 + 106134988p^3 − 50525006p^2 + 20013641p − 4856020.

- h* = r(p*) for an explicit rational polynomial r of degree 16 (the lex Gröbner basis is in shape position; r is in `crit.json`, key `r_p`).
- The minimal polynomial of h* has degree 17:

  h^17 − 20h^16 + 605h^15 − 8472h^14 + 131574h^13 − 1194882h^12 + 12128467h^11 − 54410480h^10
  + 563189714h^9 − 218541434h^8 + 30051512275h^7 + 43344701336h^6 + 3023788045110h^5
  − 10935824953542h^4 + 239062425432669h^3 − 914461904643408h^2 + 2452454302111137h − 1084936690311786.

- Numerically:
  - p* = 0.779180833031354…
  - h* = 0.534265188030699159880310784091…
  - Both have isolating intervals of width < 1e-90 in `crit.json`.

**(A3) Minimum value.**
- F* = F(p*,h*) ∈ [0.0301389772896653383862340584503107791518563682 ± 1e-45].
- F* is an algebraic number of degree 17. Its minimal polynomial is the irreducible degree-17 factor of Res_p(g(p), z − F(p,r(p))), given in full in `reports/round5-F4-crit-001/crit.json` (key `F_minpoly`). Its leading coefficient is 37118710997…; exactly one of its real roots lies in the enclosure.
- The Hessian at (p*,h*) is positive definite, by interval arithmetic (600-bit):
  - F_pp ∈ 0.0156540843555984…,
  - F_hh ∈ 0.000227299105949746…,
  - det ∈ 2.66720210491081…e−6.

**(A4) Global statement.** On [0,1]^2, F attains its minimum uniquely at (p*,h*).
- Boundary edges:
  - p=0 and p=1 have no critical points.
  - On h=0 the minimum is 0.0301635157703895… (at p=0.81162).
  - On h=1 the minimum is 0.0301573587278795… (at p=0.75129).
- Corners:
  - F(1,0) = 0.030434926…
  - F(1,1) = 0.030644169…
  - F(0,1) = 0.034767433…
  - F(0,0) = 0.035555098…
- Every boundary value is at least F* + 1.84e−5.

Consequences:
- B192's stored point is not the minimiser. F(51064/65536, 35015/65536) = 0.03013897728988013 = F* + 2.1e−13.
- F* reproduces the value of E4's 24-orbital control kernel (0.030138977289665), which confirms that item.
- Since the only critical point on R^2 is (p*,h*) and F is a polynomial, the family has no other local minimum anywhere in R^2.

### Proof / certificate

1. **F is a polynomial of this shape.** Each of the six edge factors of a K4 term is 0, 1, p, h, 1−p or 1−h. So F is a polynomial with deg_p ≤ 6 and deg_h ≤ 6.
2. **Interpolation.** A tensor Lagrange interpolation on {0,…,6}^2 therefore recovers F exactly. `poly.py` evaluates F at those 49 integer points with exact integer arithmetic (int64 with no overflow: entries ≤ 6 and 192^3 terms). It uses the rooted formula F = N^−3 Σ_{b,c,d} W_0b W_0c W_0d W_bc W_bd W_cd (red + blue, N = 192), which is valid because W is a Cayley graphon.
   - The rooted value was checked equal at all 12 block representatives at all 49 grid points (`reports/round5-F4-poly-001/rootcheck.log`).
3. **Cross-checks of the polynomial.**
   - It equals lane P's independent exact values at (32/41, 22/41) and (4/5, 2/5).
   - It equals a separate big-integer exact evaluator (`Fexact`) at those two points and at three fresh points off the grid: B192's stored point (value 0.03013897728988013), (1/3, 7/9) and (9/2, −3/7).
   - Log: `reports/round5-F4-poly-001/poly.log`. Polynomial: `experiments/round5_F4/Fpoly.json`.
4. **Critical points** (`crit.py`).
   - gcd(F_p, F_h) = 1, so there is no curve of critical points.
   - The lex Gröbner basis of (F_p, F_h), with h > p, is {h − r(p), g(p)}, with g irreducible over Q.
   - So the complex critical points are in bijection with the 17 roots of g, and h = r(p) is real whenever p is.
   - An exact Sturm count gives exactly 1 real root of g on R, and it lies in [0,1].
   - Real-root isolation is exact (sympy continued-fraction isolation, width < 1e−90).
5. **Hessian and value.** Evaluated by mpmath interval arithmetic on the isolating box.
   - The minimal polynomial of F* comes from an exact resultant, and the interval enclosure of F* contains exactly one root of it.
6. **Boundary.** Each edge restriction is a univariate rational polynomial. Its derivative's roots in [0,1] are isolated exactly, the values are enclosed by intervals, and the corners are exact rationals.
7. **Conclusion.** A continuous function on a compact square attains its minimum at an interior critical point, an edge critical point, or a corner. The interior candidate is certified strictly smallest, so the minimiser is unique.

Evidence label: exact computer algebra (sympy over Q) plus interval enclosures. Trust base: the rule.json → B192 entrywise identity (E11, `verify_rule.py`) and P's exact values. Not Lean-checked.

Reproduce: `uv run --with numpy --with sympy --with mpmath python experiments/round5_F4/poly.py && … crit.py` (under 10 s).

---

## Theorem B (E4-3840: strict local minimum in its invariant family only)

**Setting.**
- G is the recovered transitive group of order 46080, acting on 3840 = |G/K| points, with K the order-12 class 20 of `reports/round4-E4-exact-3840-001/exact-report.json`.
- Kernels are constant on the 456 undirected G-orbitals, so x ∈ [0,1]^456 and W = x[P].
- The objective is f(x) = t(K4,W) + t(K4,1−W).
- The stored kernel (SHA 594aaefb…, numerators over 65536) has 237 orbitals at 0, 196 at 1 and 23 fractional. Call this the pattern Π.

**Theorem B.** There is a point x* ∈ [0,1]^456 with the following properties.
1. **Pattern.** x* has the pattern Π: the 433 bound coordinates are exactly 0/1 as in the stored kernel.
2. **Location.** x* lies within ℓ2 distance ρ ≤ 9.82e−15 of an explicit dyadic point X2/2^64. The free numerators are in `reports/round5-F4-kkt-cert-001/certificate.json`.
3. **Stationarity.** x* is the unique zero of the reduced gradient ∇_free f in the ball of radius 1.34e−11 around X2/2^64.
4. **Strict complementarity.**
   - ∂f/∂x_i(x*) ≥ 1.2585e−9 − 9e−15 > 0 on all 237 orbitals at 0.
   - ∂f/∂x_i(x*) ≤ −2.9127e−11 + 9e−15 < 0 on all 196 orbitals at 1.
5. **Second order.** The 23×23 reduced Hessian at x* has λ_min ≥ 1.1134e−9 > 0.
6. **Value.** f(x*) ∈ [F(X2) − 2.1e−28, F(X2)], where F(X2) is an exact rational (in `certificate.json`) equal to 0.0301388958162976020442211257…

Hence x* is a **strict local minimum of f over the invariant box [0,1]^456**, by the second-order sufficient conditions with strict complementarity. Its value is 6.62e−13 below the stored incumbent 0.030138895816959867. The stored 2^−16-quantised kernel is not exactly stationary: its reduced gradient is up to 2e−10, and x* moves the free coordinates by up to 0.0184, along an extremely flat valley with λ_min ≈ 1.2e−9.

**Scope (must be stated in the paper).**
- This is local optimality *within the G/K-invariant 456-parameter family only*.
- It is **not** a local minimum in graphon space. Lifts to smaller K (and E5's fibre lifts) strictly improve it, so in graphon space the kernel is a saddle.
- It says nothing about other 0/1 patterns far from Π.

### Proof / certificate (`kkt_cert.py`, `crt_exact.py`)

1. **Exact evaluation.**
   - At any rational X/D, f and all 456 partial derivatives are computed EXACTLY. The method is CRT over 18–21 primes below 1.531e6, where the float64 BLAS operations are exact: all integers stay below 2^53 because 3840·p^2 < 2^53.
   - It uses the vertex-transitive rooted formula ∂f/∂x_i = 6 n^−3 Σ_{b: P[0,b]=i} [S_red(0,b) − S_blue(0,b)].
   - Pipeline check: at the stored numerators it reproduces E4's exact fraction 2112616269946473812116180096163290703/70096007590220172985161700444471296000 bit for bit.
2. **Derivative bounds** (for x ∈ [0,1]^456): |∂^k f| ≤ 2·(6!/(6−k)!)·s/n.
   - Each derivative selects distinct K4 edge slots.
   - One slot constraint P[a,b]=i has tuple density s_i/n by transitivity, and every other factor lies in [0,1].
   - The free orbitals have s ≤ 12 and n = 3840, which gives M2 = 0.1875, M3 = 0.75 and M4 = 2.25.
3. **Hessian.**
   - H̃ is the central difference of exact gradients with step τ = 2^−20. It is an exact rational matrix, with entrywise error ≤ τ^2 M4/6 = 3.4e−13.
   - An exact rational LDL^T shows sym(H̃) − μI ≻ 0 with μ = 1.1221e−9. So λ_min(H(X2)) ≥ μ − 23·3.4e−13 = 1.1142e−9 =: λ0.
4. **Newton–Kantorovich.**
   - Inputs: β = 1/λ0, ‖∇_free f(X2)‖ ≤ 5.47e−24 (exact), η ≤ 4.91e−15, and L = 23^{1.5}·M3 = 82.7 (Lipschitz constant of the Hessian).
   - Then h = βLη = 3.6e−4 ≤ 1/2.
   - So a zero exists within ρ ≤ 2η, and it is unique within 1/(βL).
5. **Transfer to x*.**
   - λ_min(H(x*)) ≥ λ0 − Lρ.
   - Bound-orbital gradients move by at most M2·√23·ρ = 8.8e−15, against exact margins of 1.26e−9 and 2.91e−11.
   - The free coordinates stay at least 0.0113 away from the faces of the box.

Evidence label: exact integer arithmetic (CRT) plus explicit analytic remainder bounds. Search-side code, not independent and not Lean-checked.
- The trust base is E4's orbital construction (`coset_action.py`: invariance under 8 generators, transitivity) and the rooted gradient formula.
- The tightest item is the complementarity margin at one orbital fixed at 1 (−2.9e−11). It is certified, but it is the "cheapest" level to open.

Reproduce, with the thread count pinned by `VECLIB_MAXIMUM_THREADS=1`:
1. `kkt_float.py`, the float Newton step (23 s).
2. `kkt_cert.py stage1 reports/round5-F4-kkt-cert-001`, which produces X2 (5 min).
3. `kkt_cert.py stage2 reports/round5-F4-kkt-cert-001 reports/round5-F4-kkt-cert-001/stage1.json`, which produces the certificate (5 min).

---

## Results

| item | result | label |
|---|---|---|
| F(p,h) for the B192 family | explicit rational polynomial of total degree 6 (degree 4 in each variable), denominator 2^18·27 | exact |
| critical points of F on R^2 | exactly one; p* has degree 17, h* has degree 17 | exact (Gröbner + Sturm) |
| F* | degree-17 algebraic number, 0.03013897728966533838623405845031077915… (enclosure < 1e−45); Hessian positive definite | exact + interval |
| global minimum on [0,1]^2 | unique, interior; boundary is at least F* + 1.84e−5 | exact + interval |
| E4-3840 invariant family | strict local minimum x* certified (h_Kant = 3.6e−4, λ_min ≥ 1.11e−9, complementarity margins ≥ 2.9e−11) | exact CRT + analytic bounds |
| side result | f(x*) = 0.03013889581629760204…, which is 6.62e−13 below the stored incumbent | exact (not submitted) |

## Decision

- **H-R5-F4a: CONFIRMED (theorem grade).** Paper text: "B192's two-parameter family has a unique critical point in R^2, an algebraic point of degree 17, which is its unique global minimiser on [0,1]^2. F* is algebraic of degree 17."
- **H-R5-F4b: CONFIRMED (certificate grade, invariant family only).** Paper text: "strict local minimum among G/K-invariant step graphons with this support pattern; a saddle in graphon space."
- **No promotion.** The 6.6e−13 re-polish is below any meaningful margin. If root wants it recorded, X2 (denominator 2^64) is in `certificate.json`, but it is not in rational-step-graphon-v1 form.

## Next test

- Refinement-stability eigen-check (L2 item 3), which uses the exact CRT gradient machinery here.
  - Compute the second variation of f in graphon space at x* along the latent-correlation lift directions. This quantifies the saddle, where the quadratic term vanishes and the cubic term is the leading order.
  - The CRT evaluator generalises to any vertex-transitive kernel.
- The −2.9e−11 complementarity slack identifies the next 0/1 level to open (for lane F1).
