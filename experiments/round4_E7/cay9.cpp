// E7: orbit-polynomial Cayley K4 engine.
// Density t(K4,W)+t(K4,1-W) for W(x,y)=p[orbit(y-x)], identity orbit 0 has p=0.
// F = sum_{a,b,c} prod of 6 edge values = sum_monomials c_m (prod p + prod (1-p)),
// density = F / n^3.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <climits>
#include <cmath>
#include <vector>
#include <string>
#include <random>
#include <algorithm>
#include <chrono>
using namespace std;
typedef unsigned long long u64;
typedef unsigned __int128 u128;

int n, K;
vector<int> orb;
vector<int> D;  // D[x*n+y] = x^{-1} y
struct Mono { uint16_t id[6]; int64_t c; };
vector<Mono> monos;
// distinct-set form for binary work
struct SetMono { uint8_t k; uint16_t id[6]; int64_t c; };
vector<SetMono> smonos;

void load(const string& pre) {
  FILE* f = fopen((pre + ".bin").c_str(), "rb");
  int hdr[2]; fread(hdr, 4, 2, f); n = hdr[0]; K = hdr[1];
  orb.resize(n); fread(orb.data(), 4, n, f);
  D.resize((size_t)n * n); fread(D.data(), 4, (size_t)n * n, f); fclose(f);
}

void build() {
  vector<int> rep(K, -1), sz(K, 0);
  for (int x = 0; x < n; x++) { if (rep[orb[x]] < 0) rep[orb[x]] = x; sz[orb[x]]++; }
  // open addressing hash
  size_t cap = 1 << 22; vector<u64> keys(cap, ~0ULL); vector<int64_t> vals(cap, 0); size_t used = 0;
  auto ins = [&](u64 k, int64_t v) {
    size_t h = (k * 0x9E3779B97F4A7C15ULL) >> 20; h &= cap - 1;
    while (keys[h] != ~0ULL && keys[h] != k) h = (h + 1) & (cap - 1);
    if (keys[h] == ~0ULL) { keys[h] = k; used++; }
    vals[h] += v;
    if (used * 2 > cap) {
      size_t nc = cap * 2; vector<u64> nk(nc, ~0ULL); vector<int64_t> nv(nc, 0);
      for (size_t i = 0; i < cap; i++) if (keys[i] != ~0ULL) {
        size_t hh = ((keys[i] * 0x9E3779B97F4A7C15ULL) >> 20) & (nc - 1);
        while (nk[hh] != ~0ULL) hh = (hh + 1) & (nc - 1);
        nk[hh] = keys[i]; nv[hh] = vals[i];
      }
      keys.swap(nk); vals.swap(nv); cap = nc;
    }
  };
  for (int r = 0; r < K; r++) {
    int a = rep[r];
    const int* Da = &D[(size_t)a * n];
    for (int b = 0; b < n; b++) {
      int ob = orb[b], oab = orb[Da[b]];
      const int* Db = &D[(size_t)b * n];
      for (int c = 0; c < n; c++) {
        int v[6] = {r, ob, orb[c], oab, orb[Da[c]], orb[Db[c]]};
        sort(v, v + 6);
        u64 k = 0; for (int i = 0; i < 6; i++) k = (k << 9) | v[i];
        ins(k, sz[r]);
      }
    }
  }
  for (size_t i = 0; i < cap; i++) if (keys[i] != ~0ULL) {
    Mono m; u64 k = keys[i]; for (int j = 5; j >= 0; j--) { m.id[j] = k & 511; k >>= 9; } m.c = vals[i];
    monos.push_back(m);
  }
  for (auto& m : monos) {
    SetMono s; s.k = 0; s.c = m.c;
    for (int j = 0; j < 6; j++) if (j == 0 || m.id[j] != m.id[j - 1]) s.id[s.k++] = m.id[j];
    smonos.push_back(s);
  }
  // merge identical sets
  fprintf(stderr, "monomials=%zu\n", monos.size());
}

double evalF(const vector<double>& p, vector<double>* g) {
  double F = 0; if (g) fill(g->begin(), g->end(), 0.0);
  for (auto& m : monos) {
    double a[6], b[6];
    for (int j = 0; j < 6; j++) { a[j] = p[m.id[j]]; b[j] = 1 - a[j]; }
    double pa[7], sa[7], pb[7], sb[7]; pa[0] = pb[0] = 1; sa[6] = sb[6] = 1;
    for (int j = 0; j < 6; j++) { pa[j + 1] = pa[j] * a[j]; pb[j + 1] = pb[j] * b[j]; }
    for (int j = 5; j >= 0; j--) { sa[j] = sa[j + 1] * a[j]; sb[j] = sb[j + 1] * b[j]; }
    F += m.c * (pa[6] + pb[6]);
    if (g) for (int j = 0; j < 6; j++) (*g)[m.id[j]] += m.c * (pa[j] * sa[j + 1] - pb[j] * sb[j + 1]);
  }
  return F;
}

int64_t evalB(const vector<int>& x) {
  int64_t F = 0;
  for (auto& s : smonos) {
    bool all1 = true, all0 = true;
    for (int j = 0; j < s.k; j++) { if (x[s.id[j]]) all0 = false; else all1 = false; }
    if (all1) F += s.c; if (all0) F += s.c;
  }
  return F;
}

// exact over q
u128 evalQ(const vector<u64>& P, u64 q) {
  u128 F = 0;
  for (auto& m : monos) {
    u128 r = 1, b = 1;
    for (int j = 0; j < 6; j++) { r *= P[m.id[j]]; b *= (q - P[m.id[j]]); }
    F += (u128)m.c * (r + b);
  }
  return F;
}

string u128s(u128 v) { if (!v) return "0"; string s; while (v) { s += char('0' + (int)(v % 10)); v /= 10; } reverse(s.begin(), s.end()); return s; }

mt19937_64 rng; double LR0 = getenv("LR0") ? atof(getenv("LR0")) : 3e-3, LRD = getenv("LRD") ? atof(getenv("LRD")) : 1e-3;
double dens(int64_t F) { return (double)F / ((double)n * n * n); }

// steepest single-flip descent
int64_t flipDescent(vector<int>& x) {
  int64_t F = evalB(x);
  vector<int64_t> del(K);
  while (true) {
    fill(del.begin(), del.end(), 0);
    for (auto& s : smonos) {
      int z = 0, o = 0, zi = -1, oi = -1;
      for (int j = 0; j < s.k; j++) { if (x[s.id[j]]) { o++; oi = s.id[j]; } else { z++; zi = s.id[j]; } }
      if (z == 0) for (int j = 0; j < s.k; j++) del[s.id[j]] -= s.c;
      if (z == 1) del[zi] += s.c;
      if (o == 0) for (int j = 0; j < s.k; j++) del[s.id[j]] -= s.c;
      if (o == 1) del[oi] += s.c;
    }
    int best = -1; int64_t bd = 0;
    for (int i = 1; i < K; i++) if (del[i] < bd) { bd = del[i]; best = i; }
    if (best < 0) return F;
    x[best] ^= 1; F += bd;
  }
}

// exact block move over free set
int64_t lnsStep(vector<int>& x, const vector<int>& fr, int64_t Fcur) {
  int k = fr.size(); vector<int> pos(K, -1); for (int i = 0; i < k; i++) pos[fr[i]] = i;
  size_t N = 1ULL << k; vector<int64_t> R(N, 0), B(N, 0);
  for (auto& s : smonos) {
    bool rok = true, bok = true; unsigned T = 0;
    for (int j = 0; j < s.k; j++) {
      int v = s.id[j];
      if (pos[v] >= 0) T |= 1u << pos[v];
      else if (x[v]) bok = false; else rok = false;
    }
    if (rok) R[T] += s.c; if (bok) B[T] += s.c;
  }
  for (int i = 0; i < k; i++) for (size_t S = 0; S < N; S++) if (S >> i & 1) { R[S] += R[S ^ (1ULL << i)]; B[S] += B[S ^ (1ULL << i)]; }
  size_t bs = 0; int64_t bv = LLONG_MAX;
  for (size_t S = 0; S < N; S++) { int64_t v = R[S] + B[(N - 1) ^ S]; if (v < bv) { bv = v; bs = S; } }
  if (bv < Fcur) { for (int i = 0; i < k; i++) x[fr[i]] = bs >> i & 1; return bv; }
  return Fcur;
}

int main(int argc, char** argv) {
  string pre = argv[1], mode = argv[2];
  load(pre); auto t0 = chrono::steady_clock::now(); build();
  auto el = [&]() { return chrono::duration<double>(chrono::steady_clock::now() - t0).count(); };
  fprintf(stderr, "build %.1fs n=%d K=%d\n", el(), n, K);
  if (mode == "lns" || mode == "flip") {
    u64 seed = atoll(argv[3]); int k = atoi(argv[4]); double secs = atof(argv[5]); string out = argv[6];
    rng.seed(seed); double tstart = el();
    vector<int> bestx; int64_t bestF = LLONG_MAX; int starts = 0;
    k = min(k, K - 1);
    while (el() - tstart < secs) {
      vector<int> x(K); for (int i = 1; i < K; i++) x[i] = rng() & 1; x[0] = 0;
      int64_t F = flipDescent(x); starts++;
      if (mode == "lns") {
        int fails = 0;
        while (fails < 30 && el() - tstart < secs) {
          vector<int> ids; for (int i = 1; i < K; i++) ids.push_back(i);
          shuffle(ids.begin(), ids.end(), rng); ids.resize(k);
          int64_t F2 = lnsStep(x, ids, F);
          if (F2 < F) { F = flipDescent(x); fails = 0; } else fails++;
        }
      }
      if (F < bestF) { bestF = F; bestx = x; fprintf(stderr, "[%.1fs start %d] best %lld dens %.12f\n", el(), starts, (long long)F, dens(F)); }
    }
    FILE* o = fopen(out.c_str(), "w");
    fprintf(o, "{\"mode\":\"%s\",\"n\":%d,\"K\":%d,\"starts\":%d,\"F\":%lld,\"density\":%.15f,\"x\":[", mode.c_str(), n, K, starts, (long long)bestF, dens(bestF));
    for (int i = 0; i < K; i++) fprintf(o, "%d%s", bestx[i], i + 1 < K ? "," : "]}\n");
    fclose(o);
    printf("%s best F=%lld density=%.15f starts=%d\n", mode.c_str(), (long long)bestF, dens(bestF), starts);
  } else if (mode == "frac") {
    // start from x file (list of K numbers in [0,1]) given as whitespace text
    string xf = argv[3]; int iters = atoi(argv[4]); string out = argv[5];
    u64 seed = argc > 6 ? atoll(argv[6]) : 1; double noise = argc > 7 ? atof(argv[7]) : 0.0;
    rng.seed(seed); normal_distribution<double> nd(0, 1);
    vector<double> p(K); FILE* f = fopen(xf.c_str(), "r"); for (int i = 0; i < K; i++) fscanf(f, "%lf", &p[i]); fclose(f);
    for (int i = 1; i < K; i++) { p[i] = 0.5 + (p[i] - 0.5) * (getenv("SHRINK") ? atof(getenv("SHRINK")) : 0.9) + noise * nd(rng); p[i] = min(1.0, max(0.0, p[i])); }
    p[0] = 0; double sc = 1.0 / ((double)n * n * n);
    vector<double> g(K), m1(K, 0), m2(K, 0);
    double F = 0;
    // Adam
    for (int it = 0; it < iters; it++) {
      F = evalF(p, &g) * sc;
      double lr = LR0 * pow(LRD, (double)it / iters);
      for (int i = 1; i < K; i++) {
        double gi = g[i] * sc; m1[i] = 0.9 * m1[i] + 0.1 * gi; m2[i] = 0.999 * m2[i] + 0.001 * gi * gi;
        double mh = m1[i] / (1 - pow(0.9, it + 1)), vh = m2[i] / (1 - pow(0.999, it + 1));
        p[i] -= lr * mh / (sqrt(vh) + 1e-12); p[i] = min(1.0, max(0.0, p[i]));
      }
      if (it % 500 == 0) fprintf(stderr, "it %d F %.15f\n", it, F);
    }
    // projected gradient polishing with backtracking
    for (int it = 0; it < 300; it++) {
      F = evalF(p, &g) * sc; double step = 1e-2; bool ok = false;
      for (int t = 0; t < 30; t++) {
        vector<double> q2 = p; for (int i = 1; i < K; i++) { q2[i] -= step * g[i] * sc * 1e3; q2[i] = min(1.0, max(0.0, q2[i])); }
        double F2 = evalF(q2, nullptr) * sc; if (F2 < F) { p = q2; ok = true; break; } step *= 0.5;
      }
      if (!ok) break;
    }
    F = evalF(p, &g) * sc; double kkt = 0;
    for (int i = 1; i < K; i++) { double gi = g[i] * sc; if ((p[i] <= 0 && gi > 0) || (p[i] >= 1 && gi < 0)) continue; kkt += gi * gi; }
    u64 q = n <= 1024 ? 65536 : 32768; vector<u64> P(K);
    for (int i = 0; i < K; i++) P[i] = (u64)llround(p[i] * q);
    P[0] = 0;
    u128 num = evalQ(P, q); u128 den = (u128)n * n * n; for (int j = 0; j < 6; j++) den *= q;
    long double dv = (long double)num / (long double)den;
    printf("frac F=%.15f kkt=%.3e exact_q=%llu density=%.17Lf num=%s den=%s\n", F, sqrt(kkt), q, dv, u128s(num).c_str(), u128s(den).c_str());
    FILE* o = fopen(out.c_str(), "w");
    fprintf(o, "{\"n\":%d,\"K\":%d,\"q\":%llu,\"float_density\":%.17f,\"kkt\":%.3e,\"num\":\"%s\",\"den\":\"%s\",\"exact_density\":%.17Lf,\"P\":[", n, K, q, F, sqrt(kkt), u128s(num).c_str(), u128s(den).c_str(), dv);
    for (int i = 0; i < K; i++) fprintf(o, "%llu%s", P[i], i + 1 < K ? "," : "]}\n");
    fclose(o);
  } else if (mode == "exact") {
    u64 q = atoll(argv[3]); vector<u64> P(K); for (int i = 0; i < K; i++) P[i] = atoll(argv[4 + i]);
    u128 num = evalQ(P, q); printf("num=%s\n", u128s(num).c_str());
  }
}
