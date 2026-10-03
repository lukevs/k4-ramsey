#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>

using u128 = unsigned __int128;

static void print_u128(u128 x) {
  if (x >= 10) print_u128(x / 10);
  std::cout << static_cast<char>('0' + x % 10);
}

int main() {
  int n;
  uint64_t q;
  if (!(std::cin >> n >> q) || n <= 0 || q == 0) return 1;
  std::vector<uint64_t> p(static_cast<size_t>(n) * n);
  std::map<uint64_t, int> value_id;
  for (auto &x : p) {
    if (!(std::cin >> x) || x > q) return 2;
    value_id.emplace(x, 0);
  }
  if (value_id.size() > 4) return 3;
  std::vector<uint64_t> values;
  int next = 0;
  for (auto &[value, id] : value_id) {
    id = next++;
    values.push_back(value);
  }
  const int radix = static_cast<int>(values.size());
  size_t states = 1;
  for (int e = 0; e < 6; ++e) states *= radix;
  std::vector<uint64_t> hist(states);
  auto id = [&](int i, int j) { return value_id.at(p[static_cast<size_t>(i) * n + j]); };
  // Vertex transitivity is certified by the Python driver before this fixed-root count.
  for (int j = 0; j < n; ++j) for (int k = 0; k < n; ++k) for (int l = 0; l < n; ++l) {
    size_t code = id(0,j);
    code = code * radix + id(0,k);
    code = code * radix + id(0,l);
    code = code * radix + id(j,k);
    code = code * radix + id(j,l);
    code = code * radix + id(k,l);
    ++hist[code];
  }
  std::array<u128, 64> numerator{};
  for (size_t code0 = 0; code0 < states; ++code0) {
    if (!hist[code0]) continue;
    size_t code = code0;
    std::array<uint64_t, 6> edge{};
    for (int e = 5; e >= 0; --e) { edge[e] = values[code % radix]; code /= radix; }
    for (int mask = 0; mask < 64; ++mask) {
      u128 term = hist[code0];
      for (int e = 0; e < 6; ++e)
        term *= ((mask >> e) & 1) ? edge[e] : q - edge[e];
      numerator[mask] += term;
    }
  }
  u128 denominator = static_cast<u128>(n) * n * n;
  for (int e = 0; e < 6; ++e) denominator *= q;
  std::cout << "DEN "; print_u128(denominator); std::cout << "\n";
  for (int mask = 0; mask < 64; ++mask) {
    std::cout << "MASK " << mask << " "; print_u128(numerator[mask]); std::cout << "\n";
  }
}
