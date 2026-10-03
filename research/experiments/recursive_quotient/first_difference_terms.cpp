// Exact ordered distinct-label terms for first-difference clique recursion.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

using U64 = std::uint64_t;
using U128 = __uint128_t;

void print_u128(U128 x) {
  if (!x) { std::cout << '0'; return; }
  std::string s;
  while (x) { s.push_back(char('0' + x % 10)); x /= 10; }
  std::reverse(s.begin(), s.end());
  std::cout << s;
}

void emit(const std::vector<std::vector<U64>>& source, U64 q, bool blue) {
  int n = int(source.size());
  std::vector<std::vector<U64>> a(n, std::vector<U64>(n));
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
    a[i][j] = i == j ? 0 : (blue ? q - source[i][j] : source[i][j]);

  U128 s1 = 0, s2 = 0, s3 = 0, s4 = 0;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (i != j) {
    U128 x = a[i][j];
    s1 += x; s2 += x*x; s3 += x*x*x; s4 += x*x*x*x;
  }
  U128 triangle = 0, paired = 0;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) if (j != i)
    for (int k = 0; k < n; ++k) if (k != i && k != j) {
      U128 x = a[i][j], y = a[i][k], z = a[j][k];
      triangle += x*y*z;
      paired += x*x*y*y*z;
    }

  // With diagonal zero, every repeated positional label kills the product;
  // this contraction is exactly the ordered all-distinct K4 term.
  U128 clique4 = 0;
  std::vector<U64> pair(n);
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
    U64 edge = a[i][j];
    if (!edge) continue;
    for (int k = 0; k < n; ++k) pair[k] = a[i][k] * a[j][k];
    U128 inner = 0;
    for (int k = 0; k < n; ++k) if (pair[k])
      for (int l = 0; l < n; ++l)
        inner += U128(pair[k]) * pair[l] * a[k][l];
    clique4 += U128(edge) * inner;
  }
  const U128 values[] = {s1, s2, s3, s4, triangle, paired, clique4};
  for (int i = 0; i < 7; ++i) {
    if (i) std::cout << ' ';
    print_u128(values[i]);
  }
  std::cout << '\n';
}

int main() {
  int n; U64 q;
  if (!(std::cin >> n >> q) || n < 2 || q == 0) return 1;
  std::vector<std::vector<U64>> p(n, std::vector<U64>(n));
  for (auto& row : p) for (auto& x : row) if (!(std::cin >> x) || x > q) return 2;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
    if (p[i][j] != p[j][i]) return 3;
  emit(p, q, false);
  emit(p, q, true);
}
