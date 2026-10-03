#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using u128=unsigned __int128;
static std::string dec(u128 x){if(!x)return"0";std::string s;while(x){s.push_back('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());return s;}
static uint64_t fact(int x){uint64_t y=1;for(int i=2;i<=x;i++)y*=i;return y;}
struct Result{std::string name;std::array<int,6>v;u128 current,best,greedy;int bestmask,greedymask;uint64_t tuples;double seconds;};
static Result solve(std::string name,std::array<int,6>v,int n,uint64_t q,std::vector<uint64_t>const&p){
 auto start=std::chrono::steady_clock::now();int bit[6][6],m=0;for(auto&r:bit)for(int&x:r)x=-1;for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)bit[i][j]=bit[j][i]=m++;
 std::vector<int>where(n,-1);for(int i=0;i<6;i++)where[v[i]]=i;
 int z=1<<15,full=z-1;std::vector<u128>A(z),B(z);u128 current=0;uint64_t tuples=0;
 for(int a=0;a<n;a++)for(int b=a;b<n;b++)for(int c=b;c<n;c++)for(int d=c;d<n;d++){
  int x[4]={a,b,c,d};uint64_t w=24;int run=1;for(int i=1;i<=4;i++){if(i<4&&x[i]==x[i-1])run++;else w/=fact(run),run=1;}
  int mask=0,occ=0;u128 red=1,blue=1,cr=1,cb=1;
  for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){
   int u=x[i],t=x[j],wu=where[u],wt=where[t];
   if(u!=t&&wu>=0&&wt>=0){mask|=1<<bit[wu][wt];occ++;}
   else{uint64_t e=p[(size_t)u*n+t];red*=e;blue*=q-e;}
   uint64_t e=p[(size_t)u*n+t];cr*=e;cb*=q-e;
  }
  if(!mask)continue;tuples+=w;current+=(u128)w*(cr+cb);for(int i=0;i<occ;i++)red*=q,blue*=q;A[mask]+=(u128)w*red;B[mask]+=(u128)w*blue;
 }
 auto ZA=A,ZB=B;for(int b=0;b<15;b++)for(int s=0;s<z;s++)if(s&(1<<b))ZA[s]+=ZA[s^(1<<b)],ZB[s]+=ZB[s^(1<<b)];
 auto score=[&](int s){return ZA[s]+ZB[full^s];};int bestmask=0;u128 best=score(0);for(int s=1;s<z;s++){u128 y=score(s);if(y<best)best=y,bestmask=s;}
 int greedy=0;for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)if(p[(size_t)v[i]*n+v[j]]*2>q)greedy|=1<<bit[i][j];
 bool moved=true;while(moved){moved=false;u128 old=score(greedy);for(int b=0;b<15;b++){int t=greedy^(1<<b);u128 y=score(t);if(y<old){greedy=t;old=y;moved=true;}}}
 return{name,v,current,best,score(greedy),bestmask,greedy,tuples,std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()};
}
static u128 literal(std::vector<uint64_t>const&p,int n,uint64_t q){u128 z=0;for(int a=0;a<n;a++)for(int b=0;b<n;b++)for(int c=0;c<n;c++)for(int d=0;d<n;d++){int x[4]={a,b,c,d};u128 r=1,s=1;for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){auto e=p[(size_t)x[i]*n+x[j]];r*=e;s*=q-e;}z+=r+s;}return z;}
static void selftest(){int n=6;uint64_t q=7;std::vector<uint64_t>p(36);for(int i=0;i<n;i++){p[i*n+i]=(2*i+1)%8;for(int j=i+1;j<n;j++)p[i*n+j]=p[j*n+i]=(3*i+5*j+1)%8;}auto R=solve("tiny",{0,1,2,3,4,5},n,q,p);u128 diagonal_constant=0;for(int i=0;i<n;i++){u128 r=1,b=1;for(int e=0;e<6;e++)r*=p[i*n+i],b*=q-p[i*n+i];diagonal_constant+=r+b;}u128 best=~(u128)0;int bestmask=-1;for(int mask=0;mask<(1<<15);mask++){auto x=p;int bit=0;for(int i=0;i<6;i++)for(int j=i+1;j<6;j++,bit++)x[i*n+j]=x[j*n+i]=(mask&(1<<bit))?q:0;u128 y=literal(x,n,q);if(y<best)best=y,bestmask=mask;}if(best!=R.best+diagonal_constant||bestmask!=R.bestmask)throw std::runtime_error("tiny literal exhaustive mismatch");}
int main(int argc,char**argv){try{if(argc!=3)throw std::runtime_error("usage");selftest();std::ifstream in(argv[1]);std::string magic;int n,sets;uint64_t q;in>>magic>>n>>q>>sets;if(magic!="COORD_RECON_V1"||n<6||sets<1)throw std::runtime_error("header");std::vector<uint64_t>p((size_t)n*n);for(auto&x:p)in>>x;for(int i=0;i<n;i++)for(int j=0;j<n;j++)if(p[(size_t)i*n+j]!=p[(size_t)j*n+i]||p[(size_t)i*n+j]>q)throw std::runtime_error("matrix");std::vector<Result>rs;for(int s=0;s<sets;s++){std::string name;std::array<int,6>v;in>>name;for(int&x:v)in>>x;rs.push_back(solve(name,v,n,q,p));}
 const u128 parent=(u128)3244987362620791518ULL*1000000000000000000ULL+(u128)517985192882208768ULL; // exact decimal split
 std::ofstream out(argv[2]);out<<"{\n  \"schema\": \"coordinated-reconstruction-report-v1\",\n  \"tiny_control\": \"literal ordered K4 binary exhaustive passed\",\n  \"parent_total_numerator\": \""<<dec(parent)<<"\",\n  \"sets\": [\n";for(size_t i=0;i<rs.size();i++){auto&r=rs[i];u128 bt=parent-r.current+r.best,gt=parent-r.current+r.greedy;out<<"    {\"name\":\""<<r.name<<"\",\"vertices\":[";for(int j=0;j<6;j++){if(j)out<<',';out<<r.v[j];}out<<"],\"impacted_ordered_tuples\":"<<r.tuples<<",\"current_impacted\":\""<<dec(r.current)<<"\",\"best_impacted\":\""<<dec(r.best)<<"\",\"best_mask\":"<<r.bestmask<<",\"best_total_numerator\":\""<<dec(bt)<<"\",\"greedy_impacted\":\""<<dec(r.greedy)<<"\",\"greedy_mask\":"<<r.greedymask<<",\"greedy_total_numerator\":\""<<dec(gt)<<"\",\"compute_seconds\":"<<r.seconds<<"}"<<(i+1<rs.size()?",":"")<<"\n";}out<<"  ]\n}\n";
 }catch(std::exception const&e){std::cerr<<e.what()<<'\n';return 1;}}
