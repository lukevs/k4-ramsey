// Round 4 E2: constructive Monte Carlo (NRPA / random rollouts / greedy) over
// orbit-coloured Cayley graphs on G = Z_m x F_{2^k}.
// Decision i = colour (red=1) of orbit i of G\{0} under H = <u> x <g> (x Frob).
// Objective: t(K4,W)+t(K4,1-W) of the blow-up, red loopless, blue diagonal.
// Exact integer count: hom = n * sum_a f(a); density = sum_a f(a) / n^3.
#include <vector>
#include <array>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <random>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <climits>
using namespace std;
typedef unsigned long long u64;

int m, k, K2, n, W; // n = m*2^k, W words
int prim_poly[] = {0, 0x3, 0x7, 0xB, 0x13, 0x25, 0x43, 0x83, 0x11D, 0x211, 0x409, 0x805};
int gfmul(int a, int b) {
  int r = 0;
  while (b) { if (b & 1) r ^= a; b >>= 1; a <<= 1; if (a & K2) a ^= prim_poly[k]; }
  return r;
}
inline int add(int x, int y) { return (((x / K2) + (y / K2)) % m) * K2 + ((x % K2) ^ (y % K2)); }
inline int neg(int x) { return ((m - x / K2) % m) * K2 + (x % K2); }

vector<vector<int>> orbits; // excluding identity
vector<int> orbit_of;
vector<vector<int>> addt; // addt[a][b] = a+b

void build_orbits(int dZ, int dF, int frob) {
  // multiplier on Z_m: element of order dZ in Z_m^* (search), must give -1 in group
  vector<int> gensZ, gensF;
  if (m > 1) {
    int uz = -1;
    for (int u = 1; u < m; u++) {
      if (std::gcd(u, m) != 1) continue;
      int o = 1, p = u; while (p != 1 % m) { p = p * u % m; o++; if (o > m) break; }
      if (o == dZ) { // check -1 in <u>
        int q = 1; bool hasneg = (m <= 2);
        for (int t = 0; t < o; t++) { if (q == m - 1) hasneg = true; q = q * u % m; }
        if (hasneg) { uz = u; break; }
      }
    }
    if (uz < 0) { fprintf(stderr, "no Z mult of order %d with -1\n", dZ); exit(1); }
    gensZ.push_back(uz);
  }
  if (k > 0 && dF > 1) {
    int ord = K2 - 1;
    if (ord % dF) { fprintf(stderr, "dF must divide 2^k-1\n"); exit(1); }
    int g = 1; for (int t = 0; t < ord / dF; t++) g = gfmul(g, 2);
    gensF.push_back(g);
  }
  auto act = [&](int x, int which, int gen) {
    int z = x / K2, f = x % K2;
    if (which == 0) z = z * gen % m;
    else if (which == 1) f = gfmul(f, gen);
    else f = gfmul(f, f);
    return z * K2 + f;
  };
  orbit_of.assign(n, -1);
  orbit_of[0] = -2;
  for (int s = 1; s < n; s++) {
    if (orbit_of[s] != -1) continue;
    vector<int> orb = {s}; orbit_of[s] = orbits.size();
    for (size_t h = 0; h < orb.size(); h++) {
      int x = orb[h];
      vector<int> nb;
      for (int g : gensZ) nb.push_back(act(x, 0, g));
      for (int g : gensF) nb.push_back(act(x, 1, g));
      if (frob) nb.push_back(act(x, 2, 0));
      nb.push_back(neg(x));
      for (int y : nb) if (orbit_of[y] == -1) { orbit_of[y] = orbits.size(); orb.push_back(y); }
    }
    orbits.push_back(orb);
  }
}

long long evals = 0;
// f(a) summed over all a, using orbit reps: invariance of f under H holds as S is H-invariant.
// Returns sum_a f_S(a) + sum_a f_T(a)  (T = complement incl 0).
struct Evaluator {
  vector<u64> S, T, trS, trT; // trS[b*W..] = bitset of S+b
  long long count_one(const vector<u64>& X, const vector<u64>& trX, bool hasZero, const vector<char>& inX) {
    long long tot = 0;
    vector<u64> tmp(W);
    // reps: orbit reps plus identity (if in X)
    auto fa = [&](int a) {
      long long s = 0;
      const u64* Xa = &trX[(size_t)a * W];
      for (int w = 0; w < W; w++) tmp[w] = X[w] & Xa[w];
      for (int w = 0; w < W; w++) {
        u64 bits = tmp[w];
        while (bits) {
          int b = w * 64 + __builtin_ctzll(bits); bits &= bits - 1;
          const u64* Xb = &trX[(size_t)b * W];
          for (int q = 0; q < W; q++) s += __builtin_popcountll(tmp[q] & Xb[q]);
        }
      }
      return s;
    };
    if (hasZero) tot += fa(0);
    for (auto& orb : orbits) if (inX[orb[0]]) tot += fa(orb[0]) * (long long)orb.size();
    return tot;
  }
  long long eval(const vector<int>& col) { // col[i]=1 red
    evals++;
    S.assign(W, 0); T.assign(W, 0);
    vector<char> inS(n, 0), inT(n, 0);
    inT[0] = 1;
    for (size_t i = 0; i < orbits.size(); i++)
      for (int x : orbits[i]) { if (col[i]) inS[x] = 1; else inT[x] = 1; }
    for (int x = 0; x < n; x++) { if (inS[x]) S[x >> 6] |= 1ULL << (x & 63); if (inT[x]) T[x >> 6] |= 1ULL << (x & 63); }
    trS.assign((size_t)n * W, 0); trT.assign((size_t)n * W, 0);
    for (int b = 0; b < n; b++) {
      u64* ps = &trS[(size_t)b * W]; u64* pt = &trT[(size_t)b * W];
      const int* ab = addt[b].data();
      for (int x = 0; x < n; x++) { int y = ab[x]; if (inS[x]) ps[y >> 6] |= 1ULL << (y & 63); else pt[y >> 6] |= 1ULL << (y & 63); }
    }
    return count_one(S, trS, false, inS) + count_one(T, trT, true, inT);
  }
};

long long brute(const vector<int>& col) {
  vector<char> red(n, 0);
  for (size_t i = 0; i < orbits.size(); i++) for (int x : orbits[i]) red[x] = col[i];
  auto diff = [&](int x, int y) { return add(x, neg(y)); };
  long long tot = 0;
  for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) for (int c = 0; c < n; c++) for (int d = 0; d < n; d++) {
    int v[4] = {a, b, c, d}; int r = 0, bl = 0;
    for (int i = 0; i < 4; i++) for (int j = i + 1; j < 4; j++) { if (red[diff(v[i], v[j])]) r++; else bl++; }
    if (r == 6 || bl == 6) tot++;
  }
  return tot; // hom count over n^4
}

mt19937_64 rng;
Evaluator EV;
int L; // decisions
double nden;
double score_of(long long s) { return (double)s / nden; }

struct Res { long long s; vector<int> seq; };
long long best_global = LLONG_MAX; vector<int> best_seq;
long long budget = LLONG_MAX;
FILE* LOGF;
void record(const Res& r) {
  if (r.s < best_global) {
    best_global = r.s; best_seq = r.seq;
    fprintf(LOGF, "evals %lld best %.12f\n", evals, score_of(r.s)); fflush(LOGF);
  }
}
Res rollout(const vector<array<double, 2>>& pol) {
  Res r; r.seq.resize(L);
  uniform_real_distribution<double> U(0, 1);
  for (int i = 0; i < L; i++) {
    double p1 = 1.0 / (1.0 + exp(pol[i][0] - pol[i][1]));
    r.seq[i] = U(rng) < p1;
  }
  r.s = EV.eval(r.seq); record(r);
  return r;
}
void adapt(vector<array<double, 2>>& pol, const vector<int>& seq, double alpha) {
  vector<array<double, 2>> old = pol;
  for (int i = 0; i < L; i++) {
    double mx = std::max(old[i][0], old[i][1]);
    double z = exp(old[i][0] - mx) + exp(old[i][1] - mx);
    pol[i][seq[i]] += alpha;
    for (int c = 0; c < 2; c++) pol[i][c] -= alpha * exp(old[i][c] - mx) / z;
    double mn = std::min(pol[i][0], pol[i][1]); pol[i][0] -= mn; pol[i][1] -= mn; // shift-invariant renorm
  }
}
int NITER; double ALPHA;
Res nrpa(int level, vector<array<double, 2>> pol) {
  if (level == 0 || evals >= budget) return rollout(pol);
  Res best; best.s = LLONG_MAX;
  for (int it = 0; it < NITER && evals < budget; it++) {
    Res r = nrpa(level - 1, pol);
    if (r.s <= best.s) best = r;
    adapt(pol, best.seq, ALPHA);
  }
  return best;
}
// first-improvement bit-flip descent from s
Res descend(Res r) {
  bool imp = true;
  while (imp && evals < budget) {
    imp = false;
    vector<int> order(L); iota(order.begin(), order.end(), 0); shuffle(order.begin(), order.end(), rng);
    for (int i : order) {
      if (evals >= budget) break;
      r.seq[i] ^= 1; long long s = EV.eval(r.seq);
      if (s < r.s) { r.s = s; imp = true; record(r); } else r.seq[i] ^= 1;
    }
  }
  return r;
}

int main(int argc, char** argv) {
  // args: m k dZ dF frob mode budget seed level niter alpha outprefix
  m = atoi(argv[1]); k = atoi(argv[2]); int dZ = atoi(argv[3]), dF = atoi(argv[4]), frob = atoi(argv[5]);
  string mode = argv[6]; budget = atoll(argv[7]); rng.seed(atoll(argv[8]));
  int level = argc > 9 ? atoi(argv[9]) : 2; NITER = argc > 10 ? atoi(argv[10]) : 100; ALPHA = argc > 11 ? atof(argv[11]) : 1.0;
  string out = argc > 12 ? argv[12] : "out";
  K2 = 1 << k; n = m * K2; W = (n + 63) / 64; nden = (double)n * n * n;
  addt.assign(n, vector<int>(n));
  for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) addt[a][b] = add(a, b);
  build_orbits(dZ, dF, frob);
  L = orbits.size();
  LOGF = fopen((out + ".log").c_str(), "w");
  fprintf(LOGF, "m=%d k=%d n=%d dZ=%d dF=%d frob=%d decisions=%d mode=%s budget=%lld\n", m, k, n, dZ, dF, frob, L, mode.c_str(), budget);
  auto t0 = chrono::steady_clock::now();
  if (mode == "oracle") {
    for (int t = 0; t < 20; t++) {
      vector<int> c(L); for (auto& x : c) x = rng() & 1;
      long long s = EV.eval(c) * n, b = brute(c);
      printf("fast %lld brute %lld %s\n", s, b, s == b ? "OK" : "MISMATCH");
    }
    return 0;
  }
  if (mode == "nrpa") {
    vector<array<double, 2>> pol(L, {0.0, 0.0});
    while (evals < budget) nrpa(level, pol); // restart at top level until budget
  } else if (mode == "random") {
    vector<array<double, 2>> pol(L, {0.0, 0.0});
    while (evals < budget) rollout(pol);
  } else if (mode == "greedy") {
    while (evals < budget) {
      Res r; r.seq.resize(L); for (auto& x : r.seq) x = rng() & 1; r.s = EV.eval(r.seq); record(r);
      descend(r);
    }
  } else if (mode == "seeded") { // env SEED_RED=file, SEED_BIAS=b: policy biased to seed, NRPA then descent
    FILE* sf = fopen(getenv("SEED_RED"), "r"); int a, b2, c2; fscanf(sf, "%d %d %d", &a, &b2, &c2);
    vector<char> inR(n, 0); int x; while (fscanf(sf, "%d", &x) == 1) inR[x] = 1; fclose(sf);
    double bias = atof(getenv("SEED_BIAS"));
    vector<array<double, 2>> pol(L, {0.0, 0.0});
    Res r0; r0.seq.resize(L);
    for (int i = 0; i < L; i++) { r0.seq[i] = inR[orbits[i][0]]; pol[i][r0.seq[i]] = bias; }
    r0.s = EV.eval(r0.seq); record(r0);
    fprintf(LOGF, "seed value %.12f\n", score_of(r0.s));
    Res d0 = descend(r0);
    fprintf(LOGF, "seed after descent %.12f evals %lld\n", score_of(d0.s), evals);
    long long b0 = budget; budget = b0 * 8 / 10;
    while (evals < budget) nrpa(level, pol);
    budget = b0; Res r{best_global, best_seq}; descend(r);
  } else if (mode == "nrpa+desc") {
    vector<array<double, 2>> pol(L, {0.0, 0.0});
    long long b0 = budget; budget = b0 * 8 / 10;
    while (evals < budget) nrpa(level, pol);
    budget = b0; Res r{best_global, best_seq}; descend(r);
  }
  double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
  fprintf(LOGF, "FINAL evals %lld secs %.1f best %.15f sum %lld n %d\n", evals, secs, score_of(best_global), best_global, n);
  fprintf(LOGF, "SEQ "); for (int x : best_seq) fprintf(LOGF, "%d", x); fprintf(LOGF, "\n");
  fclose(LOGF);
  printf("%s decisions=%d evals=%lld secs=%.1f best=%.12f\n", mode.c_str(), L, evals, secs, score_of(best_global));
  // dump red set
  FILE* f = fopen((out + ".red").c_str(), "w");
  fprintf(f, "%d %d %d\n", m, k, n);
  for (int i = 0; i < L; i++) if (best_seq[i]) for (int x : orbits[i]) fprintf(f, "%d ", x);
  fprintf(f, "\n"); fclose(f);
}
