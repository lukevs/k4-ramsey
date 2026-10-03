// Overflow-safe exact ordered-index counter for high-precision Potts screens.
// Inner contractions have an explicit <2^128 bound; a checked 192-bit outer
// accumulator covers the explicit <2^134 global bound. A tiny literal oracle
// runs in the same process.
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

using L = std::uint64_t;
using U = __uint128_t;

struct Big {
  std::uint64_t w[3] = {0,0,0};
  void add_product(std::uint64_t x, U y) {
    const U p0 = U(x) * std::uint64_t(y);
    const U p1 = U(x) * std::uint64_t(y >> 64);
    const U middle = U(std::uint64_t(p0 >> 64)) + std::uint64_t(p1);
    const std::uint64_t part[3] = {
      std::uint64_t(p0), std::uint64_t(middle),
      std::uint64_t(p1 >> 64) + std::uint64_t(middle >> 64)
    };
    U carry = 0;
    for (int i=0;i<3;++i) {
      const U z = U(w[i]) + part[i] + carry;
      w[i] = std::uint64_t(z); carry = z >> 64;
    }
    if (carry) std::abort();
  }
  void add_u128(U x) { add_product(1, x); }
  Big& operator+=(const Big& other) {
    U carry=0;
    for(int i=0;i<3;++i){const U z=U(w[i])+other.w[i]+carry;w[i]=std::uint64_t(z);carry=z>>64;}
    if(carry)std::abort();return *this;
  }
  friend bool operator==(const Big&a,const Big&b){return a.w[0]==b.w[0]&&a.w[1]==b.w[1]&&a.w[2]==b.w[2];}
  friend bool operator!=(const Big&a,const Big&b){return !(a==b);}
  std::string decimal() const {
    Big q=*this;std::string s;
    while(q.w[0]||q.w[1]||q.w[2]){
      U rem=0;
      for(int i=2;i>=0;--i){const U cur=(rem<<64)|q.w[i];q.w[i]=std::uint64_t(cur/10);rem=cur%10;}
      s.push_back(char('0'+rem));
    }
    if(s.empty())return "0";std::reverse(s.begin(),s.end());return s;
  }
};

static Big color_count(const std::vector<std::vector<L>>& p) {
  const int n = int(p.size());
  std::vector<L> a(n);
  Big total;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j) {
    const L edge = p[i][j];
    if (edge == 0) continue;
    for (int k = 0; k < n; ++k) a[k] = p[i][k] * p[j][k];
    U sum = 0;
    for (int k = 0; k < n; ++k) if (a[k] != 0)
      for (int l = 0; l < n; ++l)
        sum += U(a[k]) * a[l] * p[k][l];
    total.add_product(edge, sum);
  }
  return total;
}

static Big literal_color(const std::vector<std::vector<L>>& p) {
  const int n = int(p.size());
  Big total;
  for (int i = 0; i < n; ++i) for (int j = 0; j < n; ++j)
    for (int k = 0; k < n; ++k) for (int l = 0; l < n; ++l)
      total.add_u128(U(p[i][j]) * p[i][k] * p[i][l] * p[j][k] * p[j][l] * p[k][l]);
  return total;
}

static bool self_test() {
  for (const auto& p : std::vector<std::vector<std::vector<L>>>{
    {{0,2},{2,0}},
    {{0,1,4},{1,0,3},{4,3,0}},
    {{2,1,4},{1,3,2},{4,2,0}}
  }) if (color_count(p) != literal_color(p)) return false;
  return true;
}

int main() {
  if (!self_test()) return 10;
  int n, count;
  L den;
  if (!(std::cin >> n >> den >> count)) return 1;
  std::vector<long long> qs(count);
  for (auto& q : qs) std::cin >> q;
  std::vector<std::vector<L>> base(n, std::vector<L>(n));
  for (auto& row : base) for (auto& value : row) std::cin >> value;
  for (int i = 0; i < n; ++i) {
    if (base[i][i] != 0) return 2;
    for (int j = 0; j < n; ++j)
      if (base[i][j] > den || base[i][j] != base[j][i]) return 3;
  }
  const int m = 3*n;
  for (long long q : qs) {
    std::vector<std::vector<L>> p(m, std::vector<L>(m));
    for (int ia = 0; ia < m; ++ia) for (int jb = 0; jb < m; ++jb) {
      const int i = ia/3, j = jb/3;
      const long long coarse = (long long)base[i][j];
      const bool fractional = i != j && coarse > 0 && coarse < (long long)den;
      const long long kernel = (ia%3 == jb%3) ? 2 : -1;
      const long long value = coarse + (fractional ? q*kernel : 0);
      if (value < 0 || value > (long long)den) return 4;
      p[ia][jb] = L(value);
    }
    const Big red = color_count(p);
    for (auto& row : p) for (L& value : row) value = den-value;
    const Big blue = color_count(p);
    Big total=red;total+=blue;
    std::cout << q << ' ' << red.decimal() << ' ' << blue.decimal() << ' ' << total.decimal() << '\n';
  }
}
