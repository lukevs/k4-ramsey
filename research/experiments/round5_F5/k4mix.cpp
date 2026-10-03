// Lane F5 round 5: exact mixed-matrix K4 count mod primes, pair-quadratic with dgemm.
// S(c) = sum_{u1..u4} X12[u1,u2] X13[u1,u3] X14[u1,u4] X23[u2,u3] X24[u2,u4] X34[u3,u4]
// with X_e = F[c_e] reduced mod p.  All double intermediates < 2^53 (asserted on p, n).
// Usage: k4mix F.bin n K plan.txt p1 [p2 ...]
//   F.bin: K*n*n int64 little endian (F[c][u][v]).
//   plan.txt: lines "c13 c23 c34 m" followed by m lines "c12 c13 c14 c23 c24 c34".
// Output: "R <prime> <keyidx> <assignidx> <residue>".
#include <Accelerate/Accelerate.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <chrono>

static inline double modp(double x, double p, double invp) {
  double q = std::floor(x * invp);
  double r = x - q * p;
  if (r < 0) r += p;
  if (r >= p) r -= p;
  return r;
}

int main(int argc, char** argv) {
  if (argc < 6) { fprintf(stderr, "usage\n"); return 2; }
  const char* fpath = argv[1];
  int n = atoi(argv[2]), K = atoi(argv[3]);
  const char* plan = argv[4];
  std::vector<long long> primes;
  for (int i = 5; i < argc; i++) primes.push_back(atoll(argv[i]));
  std::vector<int64_t> F((size_t)K * n * n);
  FILE* f = fopen(fpath, "rb");
  if (!f || fread(F.data(), 8, F.size(), f) != F.size()) { fprintf(stderr, "read F\n"); return 3; }
  fclose(f);
  struct Key { int c13, c23, c34; std::vector<std::vector<int>> as; };
  std::vector<Key> keys;
  FILE* pf = fopen(plan, "r");
  int a, b, c, m;
  while (fscanf(pf, "%d %d %d %d", &a, &b, &c, &m) == 4) {
    Key k{a, b, c, {}};
    for (int i = 0; i < m; i++) {
      std::vector<int> v(6);
      for (int j = 0; j < 6; j++) if (fscanf(pf, "%d", &v[j]) != 1) return 4;
      k.as.push_back(v);
    }
    keys.push_back(k);
  }
  fclose(pf);
  size_t nn = (size_t)n * n;
  std::vector<double> R((size_t)K * nn), P(nn), G(nn);
  for (long long pl : primes) {
    // exactness: n*(p-1)^2 < 2^53 for dgemm; also (p-1)^2 < 2^53 and n*(p-1) < 2^53
    if ((long double)n * (pl - 1) * (pl - 1) >= 9007199254740992.0L) { fprintf(stderr, "prime too big\n"); return 5; }
    double p = (double)pl, invp = 1.0 / p;
    for (size_t i = 0; i < R.size(); i++) {
      long long v = F[i] % pl; if (v < 0) v += pl;
      R[i] = (double)v;
    }
    for (size_t ki = 0; ki < keys.size(); ki++) {
      auto t0 = std::chrono::steady_clock::now();
      Key& k = keys[ki];
      const double* X13 = &R[(size_t)k.c13 * nn];
      const double* X23 = &R[(size_t)k.c23 * nn];
      const double* X34 = &R[(size_t)k.c34 * nn];
      std::vector<unsigned long long> acc(k.as.size(), 0);
      for (int u1 = 0; u1 < n; u1++) {
        const double* r13 = X13 + (size_t)u1 * n;
        for (int u2 = 0; u2 < n; u2++) {
          const double* r23 = X23 + (size_t)u2 * n;
          double* pr = &P[(size_t)u2 * n];
          for (int u3 = 0; u3 < n; u3++) pr[u3] = modp(r13[u3] * r23[u3], p, invp);
        }
        cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, n, n, n, 1.0, P.data(), n, X34, n, 0.0, G.data(), n);
        for (size_t i = 0; i < nn; i++) G[i] = modp(G[i], p, invp);
        for (size_t ai = 0; ai < k.as.size(); ai++) {
          const auto& as = k.as[ai];
          const double* r12 = &R[(size_t)as[0] * nn] + (size_t)u1 * n;
          const double* r14 = &R[(size_t)as[2] * nn] + (size_t)u1 * n;
          const double* X24 = &R[(size_t)as[4] * nn];
          unsigned long long s = 0;
          for (int u2 = 0; u2 < n; u2++) {
            const double* g = &G[(size_t)u2 * n];
            const double* r24 = X24 + (size_t)u2 * n;
            double t = 0;  // n terms < p: < 2^31
            for (int u4 = 0; u4 < n; u4++) {
              double y = modp(g[u4] * r24[u4], p, invp);
              t += modp(y * r14[u4], p, invp);
            }
            t = modp(t, p, invp);
            s += (unsigned long long)modp(t * r12[u2], p, invp);
          }
          acc[ai] = (acc[ai] + s % (unsigned long long)pl) % (unsigned long long)pl;
        }
      }
      double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
      for (size_t ai = 0; ai < k.as.size(); ai++)
        printf("R %lld %zu %zu %llu\n", pl, ki, ai, acc[ai]);
      fprintf(stderr, "prime %lld key %zu done %.2fs\n", pl, ki, dt);
      fflush(stdout);
    }
  }
  return 0;
}
