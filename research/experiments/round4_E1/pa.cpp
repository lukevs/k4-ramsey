// Round4 E1: population annealing vs independent annealing on Cayley graphs
// Cay(G,S), G = product of cyclic groups (abelian). Blow-up value
// t(K4,R)+t(K4,B) with blue diagonal = (F_R+F_B)/n^3, F = #ordered (a,b,c).
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <vector>
#include <random>
#include <algorithm>
#include <string>
#include <map>
#include <set>
using namespace std;
typedef uint64_t W;
int n, words; vector<int> addt, negt; vector<int> reps; // reps: one per inverse pair (excluding 0)
W lastmask;
struct Rep {
  vector<uint8_t> s; vector<W> tr; // tr[x] = S + x bitset
  long long FR=0, FB=0; int lineage=0; double E=0;
};
void build_group(const vector<int>& m){
  n=1; for(int v:m) n*=v; words=(n+63)/64;
  lastmask = (n%64)? ((W(1)<<(n%64))-1) : ~W(0);
  vector<vector<int>> dig(n, vector<int>(m.size()));
  for(int x=0;x<n;x++){int r=x; for(int i=(int)m.size()-1;i>=0;i--){dig[x][i]=r%m[i]; r/=m[i];}}
  auto enc=[&](const vector<int>&d){int x=0; for(size_t i=0;i<m.size();i++) x=x*m[i]+d[i]; return x;};
  addt.assign((size_t)n*n,0); negt.assign(n,0);
  for(int x=0;x<n;x++){ vector<int> d(m.size()); for(size_t i=0;i<m.size();i++) d[i]=(m[i]-dig[x][i])%m[i]; negt[x]=enc(d);
    for(int y=0;y<n;y++){ for(size_t i=0;i<m.size();i++) d[i]=(dig[x][i]+dig[y][i])%m[i]; addt[(size_t)x*n+y]=enc(d);} }
  reps.clear(); for(int x=1;x<n;x++) if(x<=negt[x]) reps.push_back(x);
}
inline void tog(vector<W>& tr,int x,int y){ tr[(size_t)x*words+y/64]^=W(1)<<(y%64); }
void flip(Rep& r,int t){ int u=negt[t];
  r.s[t]^=1; if(u!=t) r.s[u]^=1;
  for(int x=0;x<n;x++){ tog(r.tr,x,addt[(size_t)t*n+x]); if(u!=t) tog(r.tr,x,addt[(size_t)u*n+x]); } }
static W buf[64], nb[64];
long long countF(const Rep& r,bool blue){
  long long F=0; const W* T=r.tr.data();
  auto get=[&](int x,W* o){ const W* p=T+(size_t)x*words; if(!blue) memcpy(o,p,words*8); else {for(int w=0;w<words;w++) o[w]=~p[w]; o[words-1]&=lastmask;} };
  W t0[64]; get(0,t0);
  for(int a=0;a<n;a++){ if(!((t0[a/64]>>(a%64))&1)) continue; // a in S (or B)
    get(a,buf); for(int w=0;w<words;w++) nb[w]=t0[w]&buf[w];
    for(int w=0;w<words;w++){ W bits=nb[w]; while(bits){ int b=64*w+__builtin_ctzll(bits); bits&=bits-1;
      const W* p=T+(size_t)b*words; long long c=0;
      if(!blue) for(int v=0;v<words;v++) c+=__builtin_popcountll(nb[v]&p[v]);
      else { for(int v=0;v<words-1;v++) c+=__builtin_popcountll(nb[v]&~p[v]); c+=__builtin_popcountll(nb[words-1]&~p[words-1]&lastmask);} 
      F+=c; } } }
  return F; }
double energy(Rep& r){ r.FR=countF(r,false); r.FB=countF(r,true); r.E=(double)(r.FR+r.FB)/((double)n*n*n); return r.E; }
void init(Rep& r, mt19937_64& g, double p){ r.s.assign(n,0); r.tr.assign((size_t)n*words,0);
  uniform_real_distribution<double> U(0,1);
  for(int t:reps) if(U(g)<p){ r.s[t]=1; r.s[negt[t]]=1; }
  for(int x=0;x<n;x++) for(int y=0;y<n;y++) if(r.s[y]) tog(r.tr,x,addt[(size_t)y*n+x]);
  energy(r); }
// naive brute recount for testing
long long brute(const Rep& r,bool blue){ long long F=0; auto in=[&](int x){ return blue? !r.s[x] : (bool)r.s[x]; };
  for(int a=0;a<n;a++) if(in(a)) for(int b=0;b<n;b++) if(in(b)&&in(addt[(size_t)b*n+negt[a]])) for(int c=0;c<n;c++)
    if(in(c)&&in(addt[(size_t)c*n+negt[a]])&&in(addt[(size_t)c*n+negt[b]])) F++; return F; }
long long evals=0;
// one Metropolis sweep-step: propose random rep flip
void mstep(Rep& r,double beta,mt19937_64& g){ uniform_int_distribution<int> D(0,(int)reps.size()-1); uniform_real_distribution<double> U(0,1);
  int t=reps[D(g)]; double E0=r.E; long long a=r.FR,b=r.FB; flip(r,t); energy(r); evals++;
  double d=r.E-E0; if(d<=0 || U(g)<exp(-beta*d)) return; flip(r,t); r.FR=a; r.FB=b; r.E=E0; }
void quench(Rep& r){ // steepest 1-flip descent
  while(true){ int bt=-1; double be=r.E; long long a=r.FR,b=r.FB; double E0=r.E;
    for(int t:reps){ flip(r,t); energy(r); evals++; if(r.E<be-1e-15){be=r.E;bt=t;} flip(r,t);} r.FR=a;r.FB=b;r.E=E0;
    if(bt<0) return; flip(r,bt); energy(r);} }
string key(const Rep& r){ char b[64]; snprintf(b,64,"%lld",r.FR+r.FB); return b; }
int main(int argc,char**argv){
  // args: mode(test|pa|ia) dims(e.g. 2x2x2x2x2x2x2x2) R K sweeps_per_temp beta0 beta1 seed out.json
  string mode=argv[1]; vector<int> m; { string s=argv[2]; size_t p=0; while(p<s.size()){ size_t q=s.find('x',p); if(q==string::npos) q=s.size(); m.push_back(atoi(s.substr(p,q-p).c_str())); p=q+1; } }
  build_group(m);
  if(mode=="test"){ mt19937_64 g(1); int bad=0; for(int trial=0;trial<20;trial++){ Rep r; init(r,g,0.5);
      for(int k=0;k<10;k++){ int t=reps[g()%reps.size()]; flip(r,t); energy(r); long long bR=brute(r,false), bB=brute(r,true);
        if(bR!=r.FR||bB!=r.FB){bad++; printf("MISMATCH %lld %lld vs %lld %lld\n",r.FR,r.FB,bR,bB);} } }
    printf("n=%d test mismatches=%d\n",n,bad); return bad; }
  int R=atoi(argv[3]), K=atoi(argv[4]); double sweeps=atof(argv[5]); double b0=atof(argv[6]), b1=atof(argv[7]); uint64_t seed=strtoull(argv[8],0,10); const char* out=argv[9];
  mt19937_64 g(seed); vector<Rep> pop(R); for(int i=0;i<R;i++){ init(pop[i],g,0.5); pop[i].lineage=i; }
  if(getenv("INIT")){ // file of element indices for S (already in this group's encoding)
    FILE* fi=fopen(getenv("INIT"),"r"); vector<uint8_t> s0(n,0); int x; while(fscanf(fi,"%d",&x)==1) s0[x]=1; fclose(fi);
    for(int i=0;i<R;i++){ Rep& r=pop[i]; r.s=s0; r.tr.assign((size_t)n*words,0); for(int xx=0;xx<n;xx++) for(int y=0;y<n;y++) if(r.s[y]) tog(r.tr,xx,addt[(size_t)y*n+xx]); energy(r);} 
    fprintf(stderr,"init E=%.15f\n",pop[0].E); }
  int steps=(int)(sweeps*reps.size()); vector<double> bestTrace; double best=1; Rep bestRep=pop[0];
  vector<int> famTrace;
  double essT = getenv("ESS")? atof(getenv("ESS")) : 0; double betaCur=b0; long long budget=(long long)K*R*steps;
  for(int k=0;k<(essT>0? 100000:K);k++){
    double beta = b0*pow(b1/b0,(double)k/(K-1));
    if(essT>0){ if(k==0) beta=b0; else { double emin=1e9; for(auto&r:pop) emin=min(emin,r.E);
        auto ess=[&](double db){ double s1=0,s2=0; for(auto&r:pop){ double w=exp(-db*(r.E-emin)); s1+=w; s2+=w*w;} return s1*s1/s2/R; };
        double lo=0, hi=b1; if(ess(hi-betaCur)>=essT) beta=b1; else { for(int it=0;it<60;it++){ double md=0.5*(lo+hi); if(ess(md)>=essT) lo=md; else hi=md; } beta=min(b1,betaCur+max(lo,betaCur*1e-3)); } }
      if(evals>=budget) break; }
    if(mode=="pa" && k>0){ double bprev=(essT>0)? betaCur : b0*pow(b1/b0,(double)(k-1)/(K-1)); double db=beta-bprev;
      double emin=1e9; for(auto&r:pop) emin=min(emin,r.E); vector<double> w(R); double Z=0; for(int i=0;i<R;i++){w[i]=exp(-db*(pop[i].E-emin)); Z+=w[i];}
      // systematic resampling, fixed population size
      vector<Rep> np; np.reserve(R); uniform_real_distribution<double> U(0,1); double u=U(g)/R, c=0; int i=0;
      for(int j=0;j<R;j++){ double target=u+(double)j/R; while(c+w[i]/Z<target && i<R-1){ c+=w[i]/Z; i++; } np.push_back(pop[i]); }
      pop.swap(np); }
    for(auto&r:pop){ for(int s=0;s<steps;s++) mstep(r,beta,g); if(r.E<best){best=r.E; bestRep=r;} }
    betaCur=beta;
    set<int> fam; for(auto&r:pop) fam.insert(r.lineage); famTrace.push_back(fam.size());
    double mn=1; for(auto&r:pop) mn=min(mn,r.E); bestTrace.push_back(mn);
    if(k%10==0||k==K-1){ fprintf(stderr,"k=%d beta=%.3g min=%.12f best=%.12f fam=%zu evals=%lld\n",k,beta,mn,best,fam.size(),evals); }
  }
  vector<double> fin; map<string,int> basins; for(auto&r:pop){ quench(r); fin.push_back(r.E); basins[key(r)]++; if(r.E<best){best=r.E;bestRep=r;} }
  set<int> fam; for(auto&r:pop) fam.insert(r.lineage);
  sort(fin.begin(),fin.end());
  FILE* f=fopen(out,"w"); fprintf(f,"{\"mode\":\"%s\",\"dims\":\"%s\",\"n\":%d,\"R\":%d,\"K\":%d,\"sweeps\":%g,\"beta0\":%g,\"beta1\":%g,\"seed\":%llu,\"evals\":%lld,",mode.c_str(),argv[2],n,R,K,sweeps,b0,b1,(unsigned long long)seed,evals);
  fprintf(f,"\"best\":%.15f,\"best_count\":%lld,\"distinct_final_basins\":%zu,\"final_families\":%zu,\"final_sorted\":[",best,bestRep.FR+bestRep.FB,basins.size(),fam.size());
  for(size_t i=0;i<fin.size();i++) fprintf(f,"%s%.15f",i?",":"",fin[i]); fprintf(f,"],\"best_S\":[");
  bool first=true; for(int x=0;x<n;x++) if(bestRep.s[x]){ fprintf(f,"%s%d",first?"":",",x); first=false;} fprintf(f,"],\"fam_trace\":[");
  for(size_t i=0;i<famTrace.size();i++) fprintf(f,"%s%d",i?",":"",famTrace[i]); fprintf(f,"]}\n"); fclose(f);
  printf("best=%.15f basins=%zu fams=%zu evals=%lld\n",best,basins.size(),fam.size(),evals);
}
