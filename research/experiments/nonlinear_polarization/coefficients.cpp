#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct U256 {
  std::array<uint64_t,4> limb{};
  U256()=default;
  U256(uint64_t value) { limb[0]=value; }
};

static U256 add(U256 left,const U256& right) {
  unsigned __int128 carry=0;
  for (int i=0;i<4;++i) {
    const unsigned __int128 value=static_cast<unsigned __int128>(left.limb[i])+right.limb[i]+carry;
    left.limb[i]=uint64_t(value); carry=value>>64;
  }
  if (carry) throw std::overflow_error("U256 add overflow");
  return left;
}

static U256 mul(U256 value,uint64_t factor) {
  unsigned __int128 carry=0;
  for (int i=0;i<4;++i) {
    const unsigned __int128 product=static_cast<unsigned __int128>(value.limb[i])*factor+carry;
    value.limb[i]=uint64_t(product);carry=product>>64;
  }
  if (carry) throw std::overflow_error("U256 mul overflow");
  return value;
}

static int compare(const U256& left,const U256& right) {
  for (int i=3;i>=0;--i) if (left.limb[i]!=right.limb[i]) return left.limb[i]<right.limb[i]?-1:1;
  return 0;
}

static U256 subtract(U256 left,const U256& right) {
  if (compare(left,right)<0) throw std::runtime_error("negative U256 subtraction");
  uint64_t borrow=0;
  for (int i=0;i<4;++i) {
    const unsigned __int128 sub=static_cast<unsigned __int128>(right.limb[i])+borrow;
    const uint64_t next=left.limb[i]-uint64_t(sub);
    borrow=(static_cast<unsigned __int128>(left.limb[i])<sub);
    left.limb[i]=next;
  }
  return left;
}

static bool nonzero(const U256& value) { return value.limb[0]||value.limb[1]||value.limb[2]||value.limb[3]; }

static std::string decimal(U256 magnitude,bool negative=false) {
  if (!nonzero(magnitude)) return "0";
  std::string answer;
  while (nonzero(magnitude)) {
    unsigned __int128 remainder=0;
    for (int i=3;i>=0;--i) {
      const unsigned __int128 current=(remainder<<64)|magnitude.limb[i];
      magnitude.limb[i]=uint64_t(current/10);remainder=current%10;
    }
    answer.push_back(char('0'+unsigned(remainder)));
  }
  if (negative) answer.push_back('-');
  std::reverse(answer.begin(),answer.end());
  return answer;
}

int main(int argc, char** argv) {
  try {
    if (argc < 2 || argc > 3) throw std::runtime_error("usage: coefficients certificate [row_limit]");
    std::ifstream in(argv[1]);
    uint64_t n=0,q=0,base=0,types=0,kernel_count=0,row_count=0;
    if (!(in>>n>>q>>base>>types>>kernel_count>>row_count) || !types || types>16)
      throw std::runtime_error("bad header");
    uint64_t limit=row_count;
    if (argc==3) limit=std::min<uint64_t>(limit,std::stoull(argv[2]));
    std::vector<std::vector<uint64_t>> kernels(kernel_count,std::vector<uint64_t>(types*types));
    for (auto& kernel:kernels) for (auto& value:kernel)
      if (!(in>>value) || value>q) throw std::runtime_error("bad kernel");
    const std::array<std::array<int,3>,4> triangles{{{{0,1,3}},{{0,2,4}},{{1,2,5}},{{3,4,5}}}};
    const std::array<std::array<int,3>,4> triangle_other{{{{2,4,5}},{{1,3,5}},{{0,3,4}},{{0,1,2}}}};
    const std::array<std::array<int,4>,3> cycles{{{{1,2,3,4}},{{0,2,3,5}},{{0,1,4,5}}}};
    const std::array<std::array<int,2>,3> cycle_other{{{{0,5}},{{1,4}},{{2,3}}}};
    U256 a3_positive,a3_minus,a4;
    uint64_t processed=0,mass=0;
    for (uint64_t row=0;row<row_count;++row) {
      std::array<uint64_t,6> ids{}; uint64_t count=0;
      for (auto& id:ids) if (!(in>>id) || id>=kernel_count) throw std::runtime_error("bad id");
      if (!(in>>count)) throw std::runtime_error("bad count");
      if (row>=limit) continue;
      ++processed; mass+=count;
      for (uint64_t s0=0;s0<types;++s0) for (uint64_t s1=0;s1<types;++s1)
      for (uint64_t s2=0;s2<types;++s2) for (uint64_t s3=0;s3<types;++s3) {
        const std::array<uint64_t,4> s{s0,s1,s2,s3};
        const std::array<std::array<int,2>,6> ends{{{{0,1}},{{0,2}},{{0,3}},{{1,2}},{{1,3}},{{2,3}}}};
        std::array<uint64_t,6> p{},c{};
        for (int e=0;e<6;++e) {
          p[e]=kernels[ids[e]][s[ends[e][0]]*types+s[ends[e][1]]];
          c[e]=p[e]*(q-p[e]);
        }
        for (int h=0;h<4;++h) {
          U256 term(c[triangles[h][0]]);
          term=mul(term,c[triangles[h][1]]); term=mul(term,c[triangles[h][2]]);
          uint64_t red=p[triangle_other[h][0]];
          uint64_t blue=q-p[triangle_other[h][0]];
          for (int z=1;z<3;++z) {
            red*=p[triangle_other[h][z]];
            blue*=q-p[triangle_other[h][z]];
          }
          term=mul(term,red>=blue?red-blue:blue-red);term=mul(term,count);
          if (red>=blue) a3_positive=add(a3_positive,term); else a3_minus=add(a3_minus,term);
        }
        for (int h=0;h<3;++h) {
          U256 term(c[cycles[h][0]]);
          for (int z=1;z<4;++z) term=mul(term,c[cycles[h][z]]);
          uint64_t red=p[cycle_other[h][0]]*p[cycle_other[h][1]];
          uint64_t blue=(q-p[cycle_other[h][0]])*(q-p[cycle_other[h][1]]);
          term=mul(term,red+blue);term=mul(term,count);a4=add(a4,term);
        }
      }
    }
    const bool a3_negative=compare(a3_positive,a3_minus)<0;
    const U256 a3= a3_negative ? subtract(a3_minus,a3_positive) : subtract(a3_positive,a3_minus);
    std::cout<<decimal(a3,a3_negative)<<"\n"<<decimal(a4)<<"\n"<<n<<' '<<q<<' '<<base<<' '<<types<<' '
             <<kernel_count<<' '<<row_count<<' '<<processed<<' '<<mass<<"\n";
  } catch (const std::exception& error) {
    std::cerr<<error.what()<<"\n"; return 1;
  }
}
