#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using u128 = unsigned __int128;
namespace fs = std::filesystem;
static constexpr int Q = 65536;

std::string u128s(u128 x) {
  if (!x) return "0";
  std::string s;
  while (x) { s.push_back(char('0' + x % 10)); x /= 10; }
  std::reverse(s.begin(), s.end());
  return s;
}
u128 gcd128(u128 a, u128 b) { while (b) { u128 r=a%b; a=b; b=r; } return a; }

struct Group {
  int acted;
  int n = 192;
  std::vector<int> inv;
  std::vector<std::vector<int>> mul;
  std::vector<int> orbit;
  std::vector<std::vector<int>> members;

  int apply_once(int v) const {
    int out=v;
    for (int b=0;b<acted;b++) {
      int x=(v>>(2*b))&1, y=(v>>(2*b+1))&1;
      out &= ~(3<<(2*b));
      out |= (y<<(2*b)) | ((x^y)<<(2*b+1));
    }
    return out;
  }
  int apply(int v,int t) const {
    t=(t%3+3)%3;
    while(t--) v=apply_once(v);
    return v;
  }
  int code(int v,int t) const { return 3*v+t; }
  std::pair<int,int> decode(int g) const { return {g/3,g%3}; }
  Group(int r):acted(r) {
    mul.assign(n,std::vector<int>(n)); inv.assign(n,-1);
    for(int g=0;g<n;g++) {
      auto [v,t]=decode(g);
      inv[g]=code(apply(v,-t),(3-t)%3);
      for(int h=0;h<n;h++) {
        auto [w,s]=decode(h);
        mul[g][h]=code(v^apply(w,t),(t+s)%3);
      }
    }
    orbit.assign(n,-1);
    for(int g=0;g<n;g++) if(orbit[g]<0) {
      int id=members.size(); members.push_back({g}); orbit[g]=id;
      if(inv[g]!=g) { members.back().push_back(inv[g]); orbit[inv[g]]=id; }
    }
    assert(members.size()<256);
  }
  int diff(int g,int h) const { return mul[inv[g]][h]; }
};

struct Row { std::array<uint8_t,6> e; };
std::vector<Row> rows_for(const Group& G) {
  std::vector<Row> rows; rows.reserve(size_t(G.n)*G.n*G.n);
  for(int a=0;a<G.n;a++) for(int b=0;b<G.n;b++) for(int c=0;c<G.n;c++)
    rows.push_back({{uint8_t(G.orbit[a]),uint8_t(G.orbit[b]),uint8_t(G.orbit[c]),
                     uint8_t(G.orbit[G.diff(a,b)]),uint8_t(G.orbit[G.diff(a,c)]),
                     uint8_t(G.orbit[G.diff(b,c)])}});
  return rows;
}

struct Eval { long double f; std::vector<long double> g; };
Eval evaluate(const std::vector<Row>& rows,const std::vector<long double>& p,bool grad=true) {
  long double total=0; std::vector<long double> g(p.size(),0);
  for(const auto& row:rows) {
    long double x[6], y[6], pre[7], preb[7], suf[7], sufb[7];
    pre[0]=preb[0]=1;
    for(int k=0;k<6;k++) { x[k]=p[row.e[k]]; y[k]=1-x[k]; pre[k+1]=pre[k]*x[k]; preb[k+1]=preb[k]*y[k]; }
    total += pre[6]+preb[6];
    if(grad) {
      suf[6]=sufb[6]=1;
      for(int k=5;k>=0;k--) { suf[k]=suf[k+1]*x[k]; sufb[k]=sufb[k+1]*y[k]; }
      for(int k=0;k<6;k++) g[row.e[k]] += pre[k]*suf[k+1]-preb[k]*sufb[k+1];
    }
  }
  long double den=rows.size(); total/=den;
  if(grad) for(auto& z:g) z/=den;
  return {total,std::move(g)};
}

struct Partition { long double rank_le_2=0,rank_3=0,rest=0; };
int rank_f2_3(int a,int b,int c) {
  int basis[6]={0,0,0,0,0,0},rank=0;
  for(int x:{a,b,c}) for(int bit=5;bit>=0;bit--) if((x>>bit)&1) {
    if(basis[bit]) x^=basis[bit]; else {basis[bit]=x;rank++;break;}
  }
  return rank;
}
Partition subgroup_partition(const Group& G,const std::vector<Row>& rows,const std::vector<long double>& p) {
  Partition out; size_t idx=0; long double den=rows.size();
  for(int a=0;a<G.n;a++) for(int b=0;b<G.n;b++) for(int c=0;c<G.n;c++,idx++) {
    const auto& row=rows[idx]; long double red=1,blue=1;
    for(int k=0;k<6;k++){long double x=p[row.e[k]];red*=x;blue*=1-x;}
    long double value=(red+blue)/den;
    auto [va,ta]=G.decode(a);auto [vb,tb]=G.decode(b);auto [vc,tc]=G.decode(c);
    if(ta==0&&tb==0&&tc==0) {
      if(rank_f2_3(va,vb,vc)<=2)out.rank_le_2+=value;else out.rank_3+=value;
    } else out.rest+=value;
  }
  return out;
}

long double sigmoid(long double z) {
  if(z>=0) { long double q=expl(-z); return 1/(1+q); }
  long double q=expl(z); return q/(1+q);
}
long double logit(long double p) { return logl(p/(1-p)); }

struct ZEval { long double f; std::vector<long double> g,p; };
ZEval evalz(const std::vector<Row>& rows,const std::vector<long double>& z) {
  std::vector<long double> p(z.size()); for(size_t i=0;i<z.size();i++) p[i]=sigmoid(z[i]);
  auto e=evaluate(rows,p,true); std::vector<long double> g(z.size());
  for(size_t i=0;i<z.size();i++) g[i]=e.g[i]*p[i]*(1-p[i]);
  return {e.f,std::move(g),std::move(p)};
}
long double dot(const std::vector<long double>& a,const std::vector<long double>& b) {
  long double s=0; for(size_t i=0;i<a.size();i++) s+=a[i]*b[i]; return s;
}

struct OptResult { std::string name; long double f; std::vector<long double> p; int iterations; long double gradnorm; u128 exact_red=0,exact_blue=0,exact_total=0; Partition part; };
OptResult optimize(const std::string& name,const std::vector<Row>& rows,std::vector<long double> p0,int max_iterations=45) {
  std::vector<long double> z(p0.size()); for(size_t i=0;i<z.size();i++) z[i]=logit(std::clamp(p0[i],0.002L,0.998L));
  std::vector<std::vector<long double>> ss,ys; std::vector<long double> rhos;
  ZEval cur=evalz(rows,z); int completed=0;
  for(int it=0;it<max_iterations;it++) {
    long double gn=sqrtl(dot(cur.g,cur.g)); if(gn<1e-11L) break;
    std::vector<long double> dir=cur.g, alpha(ss.size());
    for(int j=int(ss.size())-1;j>=0;j--) { alpha[j]=rhos[j]*dot(ss[j],dir); for(size_t i=0;i<dir.size();i++) dir[i]-=alpha[j]*ys[j][i]; }
    if(!ss.empty()) { long double yy=dot(ys.back(),ys.back()), sy=dot(ss.back(),ys.back()); long double h=sy/yy; for(auto& v:dir)v*=h; }
    for(size_t j=0;j<ss.size();j++) { long double beta=rhos[j]*dot(ys[j],dir); for(size_t i=0;i<dir.size();i++) dir[i]+=ss[j][i]*(alpha[j]-beta); }
    for(auto& v:dir) v=-v;
    long double gd=dot(cur.g,dir); if(!(gd<0)) { dir=cur.g; for(auto& v:dir)v=-v; gd=-dot(cur.g,cur.g); ss.clear();ys.clear();rhos.clear(); }
    long double step=1; ZEval trial; std::vector<long double> zn(z.size()); bool accepted=false;
    for(int ls=0;ls<24;ls++) {
      for(size_t i=0;i<z.size();i++) zn[i]=z[i]+step*dir[i];
      trial=evalz(rows,zn);
      if(trial.f <= cur.f + 1e-4L*step*gd) { accepted=true; break; }
      step*=0.5L;
    }
    if(!accepted) break;
    std::vector<long double> s(z.size()),y(z.size());
    for(size_t i=0;i<z.size();i++) {s[i]=zn[i]-z[i];y[i]=trial.g[i]-cur.g[i];}
    long double sy=dot(s,y);
    if(sy>1e-18L) { if(ss.size()==8){ss.erase(ss.begin());ys.erase(ys.begin());rhos.erase(rhos.begin());} ss.push_back(s);ys.push_back(y);rhos.push_back(1/sy); }
    z.swap(zn); cur=std::move(trial); completed=it+1;
  }
  return {name,cur.f,cur.p,completed,sqrtl(dot(cur.g,cur.g))};
}

std::vector<long double> features(const Group& G,int which) {
  std::vector<long double> value(G.members.size(),0);
  for(size_t o=0;o<G.members.size();o++) {
    long double sum=0;
    for(int g:G.members[o]) {
      auto [v,t]=G.decode(g); long double f=0;
      if(which==0) { // real component of C3 character times fixed-coordinate character
        long double ct=(t==0?1:-0.5L); int fixedbit=(2*G.acted<6)?((v>>(2*G.acted))&1):0; f=ct*(fixedbit?-1:1);
      } else if(which==1) { // induced character from a nonzero dual orbit
        int pair=v&3; f=(t==0 ? (pair==0?1:-1.0L/3) : 0);
      } else { // invariant quadratic/nonzero-block parity and shell
        int nz=0; for(int b=0;b<G.acted;b++) nz += ((v>>(2*b))&3)!=0;
        int fixed=__builtin_popcount(unsigned(v>>(2*G.acted)));
        f=((nz+fixed*(fixed-1)/2)&1)?-1:1;
        f*= (t==0?1:-0.5L);
      }
      sum+=f;
    }
    value[o]=sum/G.members[o].size();
  }
  return value;
}

std::vector<long double> start_from(const std::vector<long double>& f,long double scale) {
  std::vector<long double> p(f.size()); for(size_t i=0;i<f.size();i++) p[i]=sigmoid(scale*f[i]); return p;
}

u128 ipow(u128 a,int e) {u128 r=1;while(e--)r*=a;return r;}
std::pair<u128,u128> exact_count(const std::vector<Row>& rows,const std::vector<int>& q) {
  u128 red=0,blue=0;
  for(const auto& row:rows) {u128 r=1,b=1;for(int k=0;k<6;k++){int x=q[row.e[k]];r*=x;b*=Q-x;}red+=r;blue+=b;}
  return {red,blue};
}

void tiny_oracle() {
  Group G(1); // use its first acted block subgroup, isomorphic to A4
  std::vector<int> elems; for(int v=0;v<4;v++)for(int t=0;t<3;t++)elems.push_back(G.code(v,t));
  bool noncomm=false;
  for(int a:elems)for(int b:elems){if(G.mul[a][b]!=G.mul[b][a])noncomm=true;assert(G.mul[G.inv[a]][a]==0);for(int c:elems)assert(G.mul[G.mul[a][b]][c]==G.mul[a][G.mul[b][c]]);}
  assert(noncomm);
  int D=17; std::vector<int> val(G.members.size()); for(size_t o=0;o<val.size();o++)val[o]=(3+5*o)%18;
  u128 literal=0,translated=0;
  auto term=[&](int x1,int x2,int x3,int x4){int vv[4]={x1,x2,x3,x4};u128 r=1,b=1;for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){int x=val[G.orbit[G.diff(vv[i],vv[j])]];r*=x;b*=D-x;}return r+b;};
  for(int a:elems)for(int b:elems)for(int c:elems)for(int d:elems)literal+=term(a,b,c,d);
  for(int a:elems)for(int b:elems)for(int c:elems)translated+=term(0,a,b,c);
  assert(literal==u128(elems.size())*translated);
}

std::string esc(const std::string& s){std::string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}

int main(int argc,char**argv) {
  if(argc!=2){std::cerr<<"usage: search OUT\n";return 2;}
  tiny_oracle(); auto started=std::chrono::steady_clock::now();
  struct Control {std::string name;long double f;Partition part;};
  struct ActionResult {int r,orbits;std::vector<OptResult> opts;std::vector<Control> controls;};
  std::vector<ActionResult> all; long double bestf=1; u128 besttotal=~u128(0); int bestr=-1; std::vector<long double> bestp; std::vector<Row> bestrows;
  for(int r=1;r<=3;r++) {
    Group G(r); auto rows=rows_for(G); ActionResult ar{r,int(G.members.size()),{}, {}};
    std::vector<std::pair<std::string,std::vector<long double>>> starts;
    starts.push_back({"constant_half",std::vector<long double>(G.members.size(),0.5L)});
    starts.push_back({"real_c3_fixed_character",start_from(features(G,0),3.0L)});
    starts.push_back({"induced_character",start_from(features(G,1),4.0L)});
    starts.push_back({"invariant_quadratic",start_from(features(G,2),3.0L)});
    for(auto& [name,p]:starts) {
      auto base=evaluate(rows,p,false).f;
      std::vector<long double> binary(p.size());for(size_t i=0;i<p.size();i++)binary[i]=p[i]>=0.5L?1:0;
      ar.controls.push_back({name+"_start",base,subgroup_partition(G,rows,p)});
      ar.controls.push_back({name+"_binary",evaluate(rows,binary,false).f,subgroup_partition(G,rows,binary)});
      auto opt=optimize(name,rows,p);
      std::vector<int> rounded(opt.p.size()); for(size_t i=0;i<rounded.size();i++) rounded[i]=std::clamp(int(llround(opt.p[i]*Q)),0,Q);
      auto exact=exact_count(rows,rounded); opt.exact_red=exact.first; opt.exact_blue=exact.second; opt.exact_total=exact.first+exact.second; opt.part=subgroup_partition(G,rows,opt.p);
      if(opt.exact_total<besttotal){besttotal=opt.exact_total;bestf=opt.f;bestr=r;bestp=opt.p;bestrows=rows;}
      ar.opts.push_back(std::move(opt));
    }
    all.push_back(std::move(ar));
  }
  Group BG(bestr); std::vector<int> q(bestp.size());for(size_t i=0;i<q.size();i++)q[i]=std::clamp(int(llround(bestp[i]*Q)),0,Q);
  auto [red,blue]=exact_count(bestrows,q);u128 total=red+blue,den=u128(192)*192*192*ipow(Q,6),gg=gcd128(total,den);
  assert(total==besttotal);
  bool symmetric=true,in_range=true,left_invariant=true;
  for(int i=0;i<192;i++)for(int j=0;j<192;j++) {
    int x=q[BG.orbit[BG.diff(i,j)]],y=q[BG.orbit[BG.diff(j,i)]];
    symmetric &= x==y; in_range &= 0<=x&&x<=Q;
    for(int h=0;h<192;h++) left_invariant &= BG.diff(BG.mul[h][i],BG.mul[h][j])==BG.diff(i,j);
  }
  assert(symmetric&&in_range&&left_invariant&&BG.members.size()==128);
  fs::path out=argv[1];fs::create_directories(out);
  fs::copy_file("experiments/nonabelian_graphon/search.cpp",out/"source_snapshot.cpp",fs::copy_options::overwrite_existing);
  fs::copy_file("experiments/nonabelian_graphon/preregistration.json",out/"preregistration.json",fs::copy_options::overwrite_existing);
  std::ofstream cand(out/"graphon-candidate.json");cand<<"{\n  \"schema\": \"rational-step-graphon-v1\",\n  \"block_weights\": [";for(int i=0;i<192;i++){if(i)cand<<",";cand<<"1";}cand<<"],\n  \"edge_probability_denominator\": "<<Q<<",\n  \"red_probability_numerators\": [\n";
  for(int i=0;i<192;i++){cand<<"    [";for(int j=0;j<192;j++){if(j)cand<<",";cand<<q[BG.orbit[BG.diff(i,j)]];}cand<<"]"<<(i==191?"\n":",\n");}cand<<"  ]\n}\n";cand.close();
  std::ofstream rep(out/"report.json");rep<<std::setprecision(18)<<"{\n  \"schema\": \"nonabelian-cayley-screen-v1\",\n  \"hypothesis\": \"H-NAB-01\",\n  \"tiny_noncommutative_oracle\": \"passed\",\n  \"actions\": [\n";
  for(size_t ai=0;ai<all.size();ai++){
    auto& ar=all[ai];rep<<"    {\"acted_blocks\":"<<ar.r<<",\"inverse_orbits\":"<<ar.orbits<<",\"controls\":[";
    for(size_t i=0;i<ar.controls.size();i++){if(i)rep<<",";auto&c=ar.controls[i];rep<<"{\"name\":\""<<c.name<<"\",\"density\":"<<double(c.f)<<",\"subspace_partition\":["<<double(c.part.rank_le_2)<<","<<double(c.part.rank_3)<<","<<double(c.part.rest)<<"]}";}
    rep<<"],\"optimizations\":[";
    for(size_t i=0;i<ar.opts.size();i++){if(i)rep<<",";auto&o=ar.opts[i];rep<<"{\"name\":\""<<o.name<<"\",\"density\":"<<double(o.f)<<",\"iterations\":"<<o.iterations<<",\"gradient_norm\":"<<double(o.gradnorm)<<",\"rounded_exact_total\":\""<<u128s(o.exact_total)<<"\",\"rounded_exact_decimal\":"<<double((long double)o.exact_total/(long double)den)<<",\"subspace_partition\":["<<double(o.part.rank_le_2)<<","<<double(o.part.rank_3)<<","<<double(o.part.rest)<<"]}";}
    rep<<"]}"<<(ai+1==all.size()?"\n":",\n");
  }
  auto elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
  rep<<"  ],\n  \"best_acted_blocks\": "<<bestr<<",\n  \"best_continuous_density\": "<<double(bestf)<<",\n  \"rounded_q\": "<<Q<<",\n  \"exact_red\": \""<<u128s(red)<<"\",\n  \"exact_blue\": \""<<u128s(blue)<<"\",\n  \"exact_total\": \""<<u128s(total)<<"\",\n  \"exact_denominator\": \""<<u128s(den)<<"\",\n  \"exact_density\": \""<<u128s(total/gg)<<"/"<<u128s(den/gg)<<"\",\n  \"candidate_checks\": {\"symmetric\":true,\"probabilities_in_range\":true,\"left_action_invariant\":true,\"inverse_orbits\":128},\n  \"elapsed_seconds\": "<<elapsed<<",\n  \"scope\": \"Deterministic motivated-start screen; not global optimization or novelty claim.\"\n}\n";
  std::ofstream probs(out/"inverse-orbit-probabilities.json");probs<<"{\n  \"acted_blocks\": "<<bestr<<",\n  \"denominator\": "<<Q<<",\n  \"numerators\": [";for(size_t i=0;i<q.size();i++){if(i)probs<<",";probs<<q[i];}probs<<"]\n}\n";
  std::cout<<std::setprecision(18)<<"best r="<<bestr<<" continuous="<<double(bestf)<<" exact="<<u128s(total/gg)<<"/"<<u128s(den/gg)<<" elapsed="<<elapsed<<"\n";
  return 0;
}
