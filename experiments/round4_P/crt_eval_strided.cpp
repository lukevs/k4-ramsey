// Round4-P second checker: exact ordered K4 count by pair quadratic forms,
// computed modulo several primes p < 2^21 with Accelerate dgemm, CRT in Python.
//
//   T(M) = sum_{a,b} M_ab * sum_{c,d} (M_ac M_bc) M_cd (M_ad M_bd)
//        = sum_a sum_b M_ab * [ X_a (M) ]_bb-rowdot,   X_a[b,c] = M_ac M_bc.
//
// For each a: X = (M_a o M_b) mod p, Y = X * M (dgemm), val_b = <X_b, Y_b> mod p.
// Exactness: X entries < p <= 2^21, M entries <= 2^16, so each dgemm output is a
// sum of N integer products each < 2^37; N <= 4096 keeps every partial sum an
// integer < 2^49 < 2^53, so the floating-point result is exact regardless of
// summation order or FMA use.  Everything after dgemm is int64 modular.
// Knows nothing about cyclic lifts, phases or motif expansions.
//
// stdin: N Q K, then K primes, then N*N integers (red numerators, row-major).
// stdout: for each prime, "p red_residue blue_residue".
#include <Accelerate/Accelerate.h>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

typedef int64_t I64;
static int STRIDE = 1;  // search-side only: valid iff W invariant under (i,a)->(i,a+1 mod STRIDE)

static I64 count_mod(const std::vector<I64>& M, int N, I64 p) {
  std::vector<double> Md(size_t(N) * N), X(size_t(N) * N), Y(size_t(N) * N);
  for (size_t i = 0; i < Md.size(); ++i) Md[i] = double(M[i] % p);
  I64 total = 0;
  for (int a = 0; a < N; a += STRIDE) {
    const I64* Ma = &M[size_t(a) * N];
    for (int b = 0; b < N; ++b)
      for (int c = 0; c < N; ++c)
        X[size_t(b) * N + c] = double((Ma[c] % p) * (M[size_t(b) * N + c] % p) % p);
    cblas_dgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, N, N, N, 1.0,
                X.data(), N, Md.data(), N, 0.0, Y.data(), N);
    I64 acc_a = 0;
    for (int b = 0; b < N; ++b) {
      I64 v = 0;
      for (int c = 0; c < N; ++c) {
        I64 y = I64(Y[size_t(b) * N + c]);
        if (double(y) != Y[size_t(b) * N + c] || y < 0) std::abort();
        I64 x = I64(X[size_t(b) * N + c]);
        v = (v + x * (y % p)) % p;
      }
      acc_a = (acc_a + (Ma[b] % p) * v) % p;
    }
    total = (total + acc_a) % p;
  }
  return total;
}

int main() {
  int N, K;
  I64 Q;
  if (std::scanf("%d %lld %d %d", &N, &Q, &K, &STRIDE) != 4) return 2;
  if (N < 1 || N > 4096 || Q < 1 || Q > 65536) return 3;
  std::vector<I64> primes(K);
  for (int k = 0; k < K; ++k) {
    std::scanf("%lld", &primes[k]);
    if (primes[k] <= Q || primes[k] >= (1LL << 21)) return 4;
  }
  std::vector<I64> R(size_t(N) * N), B(size_t(N) * N);
  for (size_t i = 0; i < R.size(); ++i) {
    if (std::scanf("%lld", &R[i]) != 1) return 5;
    if (R[i] < 0 || R[i] > Q) return 6;
    B[i] = Q - R[i];
  }
  for (int k = 0; k < K; ++k) {
    I64 r = count_mod(R, N, primes[k]);
    I64 b = count_mod(B, N, primes[k]);
    std::printf("%lld %lld %lld\n", primes[k], r, b);
    std::fflush(stdout);
  }
  return 0;
}
