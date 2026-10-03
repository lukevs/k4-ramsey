// Exact K4 counts for a vertex-transitive step graphon: for each listed row b,
// output inner(b) = sum_{c,d} w_c w_d M_bc M_bd M_cd, w = M[0], for M = red and q-red.
// Input: n q r, then r rep indices, then n*n numerators.
#include <cstdio>
#include <vector>
#include <string>
typedef unsigned __int128 u128; typedef unsigned long long u64;
std::string s128(u128 x){ if(!x) return "0"; std::string s; while(x){ s.insert(s.begin(), char('0'+ (int)(x%10))); x/=10;} return s; }
// requires n<4096 so the inner u64 sum stays <= 2^60
int main(){ int n,r; u64 q; if(scanf("%d %llu %d",&n,&q,&r)!=3) return 1; std::vector<int> reps(r);
 for(auto&x:reps) scanf("%d",&x); std::vector<u64> R((size_t)n*n);
 for(auto&x:R) scanf("%llu",&x);
 for(int col=0; col<2; col++){ std::vector<u64> M((size_t)n*n); for(size_t i=0;i<M.size();i++) M[i]= col? q-R[i]:R[i];
  // symmetric check
  for(int i=0;i<n;i++) for(int j=0;j<n;j++) if(M[(size_t)i*n+j]!=M[(size_t)j*n+i]) { printf("ASYM\n"); return 2; }
  for(int t=0;t<r;t++){ int b=reps[t]; std::vector<u64> a(n); for(int c=0;c<n;c++) a[c]=M[c]*M[(size_t)b*n+c]; // w_c M_bc <= 2^32
   u128 tot=0; for(int c=0;c<n;c++){ if(!a[c]) continue; const u64* Mc=&M[(size_t)c*n]; u64 s=0; for(int d=0; d<n; d++) s+=a[d]*Mc[d]; tot+=(u128)s*a[c]; }
   printf("%d %d %s\n",col,b,s128(tot).c_str()); } }
 return 0; }
