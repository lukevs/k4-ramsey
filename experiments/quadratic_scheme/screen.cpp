#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using u128=unsigned __int128;
static std::string dec(u128 x){if(!x)return"0";std::string s;while(x){s.push_back('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());return s;}
static std::ostream& operator<<(std::ostream& out,u128 x){return out<<dec(x);}

struct Row{std::array<uint8_t,6> id;uint64_t count;};
static int qf(int x,int k,bool arf){int q=arf*(((x>>0)&1)^((x>>1)&1));for(int i=0;i<k;i+=2)q^=((x>>i)&1)&((x>>(i+1))&1);return q;}
static int rid(int za,int z,int k,bool arf){return (za!=0)*2*(k+1)+2*__builtin_popcount((unsigned)z)+qf(z,k,arf);}
static uint64_t enc(std::array<uint8_t,6> a,int R){std::sort(a.begin(),a.end());uint64_t x=0;for(auto z:a)x=x*R+z;return x;}
static std::vector<Row> census(int k,bool arf){int M=1<<k,R=4*(k+1);std::unordered_map<uint64_t,uint64_t> h;h.reserve(200000);
 for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)for(int u=0;u<M;u++)for(int v=0;v<M;v++)for(int w=0;w<M;w++){
  std::array<uint8_t,6>x{(uint8_t)rid(a,u,k,arf),(uint8_t)rid(b,v,k,arf),(uint8_t)rid(c,w,k,arf),(uint8_t)rid((b-a+3)%3,u^v,k,arf),(uint8_t)rid((c-a+3)%3,u^w,k,arf),(uint8_t)rid((c-b+3)%3,v^w,k,arf)};h[enc(x,R)]++;}
 std::vector<Row> rows;rows.reserve(h.size());for(auto [key,count]:h){Row r;r.count=count;auto xkey=key;for(int i=5;i>=0;i--){r.id[i]=xkey%R;xkey/=R;}rows.push_back(r);}return rows;}
static double fg(const std::vector<Row>& rows,const std::vector<double>& p,uint64_t mass,std::vector<double>* g=nullptr){if(g)std::fill(g->begin(),g->end(),0);long double f=0;
 for(auto&r:rows){long double red=1,blue=1;for(auto id:r.id){red*=p[id];blue*=1-p[id];}f+=r.count*(red+blue);if(g)for(int j=0;j<6;j++){long double dr=1,db=1;for(int z=0;z<6;z++)if(z!=j){dr*=p[r.id[z]];db*=1-p[r.id[z]];}(*g)[r.id[j]]+=(double)((long double)r.count*(dr-db)/mass);}}
 return (double)(f/mass);}
static double literal(int k,bool arf,const std::vector<double>&p){int M=1<<k;uint64_t mass=27ULL*M*M*M;long double f=0;for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)for(int u=0;u<M;u++)for(int v=0;v<M;v++)for(int w=0;w<M;w++){
 int id[6]={rid(a,u,k,arf),rid(b,v,k,arf),rid(c,w,k,arf),rid((b-a+3)%3,u^v,k,arf),rid((c-a+3)%3,u^w,k,arf),rid((c-b+3)%3,v^w,k,arf)};long double r=1,z=1;for(int x:id){r*=p[x];z*=1-p[x];}f+=r+z;}return(double)(f/mass);}
static void controls(){for(bool arf:{false,true}){int k=4,R=4*(k+1);auto r=census(k,arf);uint64_t mass=27*4096,total=0;for(auto&x:r)total+=x.count;if(total!=mass)throw std::runtime_error("k4 mass");std::vector<double>p(R),pc(R);for(int i=0;i<R;i++){p[i]=.11+.77*((i*37%101)/100.0);pc[i]=1-p[i];}if(fabs(fg(r,p,mass)-literal(k,arf,p))>2e-13||fabs(fg(r,p,mass)-fg(r,pc,mass))>2e-13)throw std::runtime_error("literal/complement controls");std::vector<double>constant(R,.37);double target=pow(.37,6)+pow(.63,6);if(fabs(fg(r,constant,mass)-target)>1e-13)throw std::runtime_error("constant control");}}
int main(int argc,char**argv){try{if(argc<2||argc>3)throw std::runtime_error("usage: screen report.json [k]");controls();int k=argc==3?std::stoi(argv[2]):6,M=1<<k,R=4*(k+1);if(k%2||k<2||k>8)throw std::runtime_error("k must be even and <=8");uint64_t mass=27ULL*M*M*M;std::mt19937_64 rng(260927+k);double best=1;std::vector<double>bp,bhist;std::string bn,bform;size_t bestrows=0;
 for(bool arf:{false,true}){auto rows=census(k,arf);for(int start=0;start<8;start++){std::vector<double>p(R),m(R),v(R),history;std::string name;
  for(int e=0;e<2;e++)for(int d=0;d<=k;d++)for(int q=0;q<2;q++){int id=e*2*(k+1)+2*d+q;if(start==0)p[id]=(q==0);else if(start==1)p[id]=(q==1);else if(start==2)p[id]=(d==0||d==1||d==3||d==4||d==7||d==8);else if(start==3)p[id]=.12+.76*((e+q+d)%2);else if(start==4)p[id]=.5+.18*(q?1:-1);else p[id]=.15+.7*((rng()%1000000)/999999.0);}
  name=start==0?"quadratic_zero":start==1?"quadratic_one":start==2?"hamming_red_clique":start==3?"syndrome_alternating":start==4?"soft_quadratic":"random";
  for(int it=1;it<=1200;it++){std::vector<double>g(R);double f=fg(rows,p,mass,&g);if(it==1||it==100||it==400||it==800||it==1200)history.push_back(f);if(f<best){best=f;bp=p;bhist=history;bn=name;bform=arf?"nonsplit_arf1":"split_arf0";bestrows=rows.size();}double lr=.045*(.15+.85*(1-it/1200.0));for(int i=0;i<R;i++){m[i]=.9*m[i]+.1*g[i];v[i]=.999*v[i]+.001*g[i]*g[i];double mh=m[i]/(1-pow(.9,it)),vh=v[i]/(1-pow(.999,it));p[i]=std::max(0.,std::min(1.,p[i]-lr*mh/(sqrt(vh)+1e-12)));}}
 }}
 auto brows=census(k,bform=="nonsplit_arf1");std::vector<double>bg(R);fg(brows,bp,mass,&bg);double kkt=0;for(int i=0;i<R;i++){double v=(bp[i]<=1e-12)?std::max(0.,-bg[i]):(bp[i]>=1-1e-12)?std::max(0.,bg[i]):fabs(bg[i]);kkt=std::max(kkt,v);}
 const uint64_t Q=65536;std::vector<uint64_t>rp(R);std::vector<double>rpd(R);for(int i=0;i<R;i++){rp[i]=llround(bp[i]*Q);rpd[i]=(double)rp[i]/Q;}u128 exact=0;for(auto&r:brows){u128 red=1,blue=1;for(auto id:r.id){red*=rp[id];blue*=Q-rp[id];}exact+=(u128)r.count*(red+blue);}u128 eden=mass;for(int i=0;i<6;i++)eden*=Q;double rd=fg(brows,rpd,mass);
 std::ofstream out(argv[1]);out<<std::setprecision(17)<<"{\n  \"schema\": \"quadratic-hamming-screen-v1\",\n  \"status\": \"completed\",\n  \"k\": "<<k<<",\n  \"group_order\": "<<3*M<<",\n  \"parameters\": "<<R<<",\n  \"best_histogram_rows\": "<<bestrows<<",\n  \"histogram_mass\": "<<mass<<",\n  \"controls\": \"split and nonsplit k=4 compressed/literal, constant, and complement controls passed\",\n  \"optimizer\": \"projected Adam with box [0,1], 8 motivated/deterministic starts per quadratic form, 1200 steps\",\n  \"quadratic_form\": \""<<bform<<"\",\n  \"best_start\": \""<<bn<<"\",\n  \"best_density\": "<<best<<",\n  \"projected_kkt_inf\": "<<kkt<<",\n  \"best_run_history_prefix_milestones_1_100_400_800_1200\": [";for(size_t i=0;i<bhist.size();i++){if(i)out<<", ";out<<bhist[i];}out<<"],\n  \"rational_denominator\": "<<Q<<",\n  \"rationalized_density\": "<<rd<<",\n  \"rationalized_exact_numerator\": \""<<exact<<"\",\n  \"rationalized_exact_denominator\": \""<<eden<<"\",\n  \"rationalized_parameters\": [";for(int i=0;i<R;i++){if(i)out<<", ";out<<rp[i];}out<<"],\n  \"beats_incumbent\": "<<(rd<.030138904006337588?"true":"false")<<",\n  \"parameters_low_to_high_relation_id\": [";for(int i=0;i<R;i++){if(i)out<<", ";out<<bp[i];}out<<"]\n}\n";
 std::cout<<std::setprecision(17)<<"rows "<<bestrows<<" best "<<best<<" form "<<bform<<" start "<<bn<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
