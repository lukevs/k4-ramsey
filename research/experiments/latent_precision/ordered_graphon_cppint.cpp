// Direct ordered-index graphon recount with a 256-bit outer sum.
// Inner products have explicit bounds below 2^128; only the O(n^2) outer
// accumulator needs more than 128 bits at Q=65536,n=384.
#include <algorithm>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

using U128 = __uint128_t;
using U64 = std::uint64_t;

struct U256 {
  U64 limb[4] = {0, 0, 0, 0};

  void add(U128 value) {
    const U64 low = static_cast<U64>(value);
    const U64 high = static_cast<U64>(value >> 64);
    const U64 old0 = limb[0];
    limb[0] += low;
    U64 carry = limb[0] < old0;
    const U64 old1 = limb[1];
    limb[1] += high;
    const U64 carry_high = limb[1] < old1;
    const U64 before_carry = limb[1];
    limb[1] += carry;
    carry = carry_high || limb[1] < before_carry;
    for (int i = 2; carry && i < 4; ++i) {
      const U64 old = limb[i];
      ++limb[i];
      carry = limb[i] < old;
    }
    if (carry) std::abort();
  }

  void add(const U256& other) {
    U64 carry = 0;
    for (int i = 0; i < 4; ++i) {
      const U64 old = limb[i];
      limb[i] += other.limb[i];
      const U64 first_carry = limb[i] < old;
      const U64 before_carry = limb[i];
      limb[i] += carry;
      carry = first_carry || limb[i] < before_carry;
    }
    if (carry) std::abort();
  }

  std::string decimal() const {
    U64 work[4] = {limb[0], limb[1], limb[2], limb[3]};
    std::string digits;
    while (work[0] || work[1] || work[2] || work[3]) {
      U128 remainder = 0;
      for (int i = 3; i >= 0; --i) {
        const U128 current = (remainder << 64) | work[i];
        work[i] = static_cast<U64>(current / 10);
        remainder = current % 10;
      }
      digits.push_back(static_cast<char>('0' + static_cast<unsigned>(remainder)));
    }
    if (digits.empty()) return "0";
    std::reverse(digits.begin(), digits.end());
    return digits;
  }
};

int main() {
  int n;
  U64 denominator;
  if (!(std::cin >> n >> denominator)) return 1;
  if (n <= 0 || denominator == 0) return 2;

  std::vector<std::vector<U64>> p(n, std::vector<U64>(n));
  for (auto& row : p) {
    for (auto& value : row) {
      if (!(std::cin >> value) || value > denominator) return 3;
    }
  }

  U256 answer;
  std::vector<U64> pair_products(n);
  for (int color = 0; color < 2; ++color) {
    U256 total;
    for (int i = 0; i < n; ++i) {
      for (int j = 0; j < n; ++j) {
        const U64 edge = p[i][j];
        if (edge == 0) continue;
        for (int k = 0; k < n; ++k) {
          pair_products[k] = p[i][k] * p[j][k];
        }
        U128 sum = 0;
        for (int k = 0; k < n; ++k) {
          if (pair_products[k] == 0) continue;
          for (int l = 0; l < n; ++l) {
            sum += static_cast<U128>(pair_products[k]) * pair_products[l] * p[k][l];
          }
        }
        total.add(static_cast<U128>(edge) * sum);
      }
    }
    std::cout << total.decimal() << '\n';
    answer.add(total);
    for (auto& row : p) {
      for (auto& value : row) value = denominator - value;
    }
  }
  std::cout << answer.decimal() << '\n';
}
