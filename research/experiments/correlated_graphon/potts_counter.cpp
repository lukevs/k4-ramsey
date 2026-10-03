// Exact screen for a three-state centered-Potts latent refinement.
//
// For every coarse fractional pair ij and latent types a,b in {0,1,2},
// replace p_ij by p_ij + q*(2 if a=b else -1).  The centered kernel has
// zero row sums, so averaging over either latent endpoint preserves p_ij.
// This program performs direct ordered-index counts on every feasible integer
// q in one process.  It deliberately supplies search evidence, not an
// independent audit of its own output.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

using I = __int128_t;
using L = long long;

static void print_i128(I x) {
  if (x == 0) { std::cout << '0'; return; }
  if (x < 0) { std::cout << '-'; x = -x; }
  std::string s;
  while (x != 0) { s.push_back(char('0' + x % 10)); x /= 10; }
  std::reverse(s.begin(), s.end());
  std::cout << s;
}

static I color_count(const std::vector<std::vector<L>>& p) {
  const int n = int(p.size());
  std::vector<L> a(n);
  I total = 0;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
    const L edge = p[i][j];
    if (edge == 0) continue;
    for (int k = 0; k < n; ++k) a[k] = p[i][k] * p[j][k];
    I sum = 0;
    for (int k = 0; k < n; ++k) if (a[k] != 0)
      for (int l = 0; l < n; ++l)
        sum += I(a[k]) * a[l] * p[k][l];
    total += I(edge) * sum;
  }
  return total;
}

int main() {
  int n;
  L den;
  if (!(std::cin >> n >> den)) return 1;
  std::vector<std::vector<L>> base(n, std::vector<L>(n));
  for (auto& row : base) for (L& value : row) std::cin >> value;
  for (int i = 0; i < n; ++i) {
    if (base[i][i] != 0) return 2;
    for (int j = 0; j < n; ++j)
      if (base[i][j] < 0 || base[i][j] > den || base[i][j] != base[j][i]) return 3;
  }

  L q_min = -den, q_max = den;
  bool supported = false;
  for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) {
    const L p = base[i][j];
    if (p == 0 || p == den) continue;
    supported = true;
    // 0 <= p+2q <= den and 0 <= p-q <= den.
    q_min = std::max(q_min, std::max((-p + 1) / 2 - 1, p - den));
    while (p + 2*q_min < 0 || p - q_min > den) ++q_min;
    q_max = std::min(q_max, std::min((den - p) / 2, p));
    while (p + 2*q_max > den || p - q_max < 0) --q_max;
  }
  if (!supported || q_min > q_max) return 4;

  const int m = 3*n;
  for (L q = q_min; q <= q_max; ++q) {
    std::vector<std::vector<L>> p(m, std::vector<L>(m));
    for (int ia = 0; ia < m; ++ia) for (int jb = 0; jb < m; ++jb) {
      const int i = ia / 3, j = jb / 3;
      const L coarse = base[i][j];
      const bool fractional = i != j && coarse > 0 && coarse < den;
      const L kernel = (ia % 3 == jb % 3) ? 2 : -1;
      p[ia][jb] = coarse + (fractional ? q*kernel : 0);
      if (p[ia][jb] < 0 || p[ia][jb] > den) return 5;
    }
    const I red = color_count(p);
    for (auto& row : p) for (L& value : row) value = den - value;
    const I blue = color_count(p);
    std::cout << q << ' '; print_i128(red); std::cout << ' ';
    print_i128(blue); std::cout << ' '; print_i128(red + blue); std::cout << '\n';
  }
}
