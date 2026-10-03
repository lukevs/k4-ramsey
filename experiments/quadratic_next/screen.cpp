#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using u128=unsigned __int128;
static std::string dec(u128 x){if(!x)return"0";std::string s;while(x){s.push_back('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());return s;}
struct Row{std::array<uint8_t,6> id;uint64_t count;};
static int qminus(int z){int q=((z>>0)&1)^((z>>1)&1);for(int i=0;i<6;i+=2)q^=((z>>i)&1)&((z>>(i+1))&1);return q;}
static int oldid(int za,int z){return(za!=0)*14+2*__builtin_popcount((unsigned)z)+qminus(z);}
static int mi(int a,int b){if(a>b)std::swap(a,b);int k=0;for(int x=0;x<4;x++)for(int y=x;y<4;y++,k++)if(x==a&&y==b)return k;throw std::runtime_error("multiset");}
static int newid(int za,int z){return(za!=0)*40+(z&3)*10+mi((z>>2)&3,(z>>4)&3);}
static uint64_t enc(std::array<uint8_t,6>a,int R){std::sort(a.begin(),a.end());uint64_t x=0;for(auto z:a)x=x*R+z;return x;}
static std::vector<Row> census(int k){int M=1<<k,R=k==6?80:((k==4)?0:0);if(k!=6)throw std::runtime_error("census only k6");std::unordered_map<uint64_t,uint64_t>h;h.reserve(100000);
 for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)for(int u=0;u<M;u++)for(int v=0;v<M;v++)for(int w=0;w<M;w++){
  std::array<uint8_t,6>x{(uint8_t)newid(a,u),(uint8_t)newid(b,v),(uint8_t)newid(c,w),(uint8_t)newid((b-a+3)%3,u^v),(uint8_t)newid((c-a+3)%3,u^w),(uint8_t)newid((c-b+3)%3,v^w)};h[enc(x,R)]++;}
 std::vector<Row>r;r.reserve(h.size());for(auto [key,n]:h){Row z;z.count=n;auto xkey=key;for(int i=5;i>=0;i--){z.id[i]=xkey%R;xkey/=R;}r.push_back(z);}return r;}
static double fg(const std::vector<Row>&rows,const std::vector<double>&p,uint64_t mass,std::vector<double>*g=nullptr){if(g)std::fill(g->begin(),g->end(),0);long double f=0;for(auto&r:rows){long double a=1,b=1;for(auto id:r.id){a*=p[id];b*=1-p[id];}f+=r.count*(a+b);if(g)for(int j=0;j<6;j++){long double x=1,y=1;for(int k=0;k<6;k++)if(k!=j){x*=p[r.id[k]];y*=1-p[r.id[k]];}(*g)[r.id[j]]+=(double)((long double)r.count*(x-y)/mass);}}return(double)(f/mass);}
static double literal6(const std::vector<double>&p){int M=64;uint64_t mass=27ULL*M*M*M;long double f=0;for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)for(int u=0;u<M;u++)for(int v=0;v<M;v++)for(int w=0;w<M;w++){
 int id[6]={newid(a,u),newid(b,v),newid(c,w),newid((b-a+3)%3,u^v),newid((c-a+3)%3,u^w),newid((c-b+3)%3,v^w)};long double x=1,y=1;for(int z:id){x*=p[z];y*=1-p[z];}f+=x+y;}return(double)(f/mass);}
int main(int argc,char**argv){try{if(argc!=2)throw std::runtime_error("usage: screen report.json");constexpr int R=80,Q=65536;constexpr uint64_t MASS=27ULL*64*64*64;const int parent[28]={0,57672,58343,0,0,58343,58343,0,0,58343,58343,0,7864,58343,65536,7864,0,65536,65536,0,0,65536,65536,0,0,65536,57672,0};
 auto rows=census(6);uint64_t hm=0;for(auto&r:rows)hm+=r.count;if(hm!=MASS)throw std::runtime_error("mass");std::vector<int>old(R),binmass(R);std::vector<double>p(R);for(int za=0;za<3;za++)for(int z=0;z<64;z++){int j=newid(za,z);old[j]=oldid(za,z);binmass[j]++;}for(int j=0;j<R;j++)p[j]=(double)parent[old[j]]/Q;
 double baseline=fg(rows,p,MASS);if(fabs(baseline-0.030140621056356332)>2e-14)throw std::runtime_error("matched parent control");std::vector<double>pc(R);for(int j=0;j<R;j++)pc[j]=1-p[j];if(fabs(fg(rows,pc,MASS)-baseline)>2e-14)throw std::runtime_error("complement control");
 // The compressed evaluator itself is the translated literal sum regrouped by
 // signature.  Re-evaluate the lifted parent literally as an independent k6
 // control; 7.08m terms is still cheap in native code.
 if(fabs(literal6(p)-baseline)>2e-14)throw std::runtime_error("literal control");
 std::vector<double>g(R),res(R);fg(rows,p,MASS,&g);double maxres=0,energy=0;int splitbins=0;
 for(int oid=0;oid<28;oid++){if(parent[oid]==0||parent[oid]==Q)continue;long double sw=0,sh=0;for(int j=0;j<R;j++)if(old[j]==oid){sw+=binmass[j];sh+=g[j];}double mean=(double)(sh/sw);for(int j=0;j<R;j++)if(old[j]==oid){res[j]=g[j]/binmass[j]-mean;maxres=std::max(maxres,fabs(res[j]));energy+=binmass[j]*res[j]*res[j];splitbins++;}}
 double initialmax=maxres;double predicted=maxres?-.01/maxres*energy:0;double best=baseline;std::vector<double>bestp=p;std::vector<double>history{baseline};
 // Full Hessian in the refined probabilities, then restrict to directions
 // preserving the mass-weighted mean inside every old fractional relation.
 std::vector<std::vector<double>> H(R,std::vector<double>(R));
 for(auto&r:rows)for(int a=0;a<6;a++)for(int b=a+1;b<6;b++){long double x=1,y=1;for(int c=0;c<6;c++)if(c!=a&&c!=b){x*=p[r.id[c]];y*=1-p[r.id[c]];}double z=(double)((long double)r.count*(x+y)/MASS);int i=r.id[a],j=r.id[b];if(i==j)H[i][i]+=2*z;else{H[i][j]+=z;H[j][i]+=z;}}
 std::vector<std::vector<double>> basis;
 for(int oid=0;oid<28;oid++){if(parent[oid]==0||parent[oid]==Q)continue;std::vector<int> ch;for(int j=0;j<R;j++)if(old[j]==oid&&binmass[j])ch.push_back(j);if(ch.size()<2)continue;int ref=ch.back();for(size_t a=0;a+1<ch.size();a++){std::vector<double>v(R);v[ch[a]]=1;v[ref]=-(double)binmass[ch[a]]/binmass[ref];basis.push_back(v);}}
 int D=basis.size();std::vector<std::vector<double>> A(D,std::vector<double>(D)),V(D,std::vector<double>(D));for(int i=0;i<D;i++){V[i][i]=1;for(int j=0;j<D;j++)for(int a=0;a<R;a++)if(basis[i][a])for(int b=0;b<R;b++)if(basis[j][b])A[i][j]+=basis[i][a]*H[a][b]*basis[j][b];}
 for(int it=0;it<100*std::max(1,D*D);it++){int u=0,v=0;double mx=0;for(int i=0;i<D;i++)for(int j=i+1;j<D;j++)if(fabs(A[i][j])>mx){mx=fabs(A[i][j]);u=i;v=j;}if(mx<1e-18)break;double phi=.5*atan2(2*A[u][v],A[v][v]-A[u][u]),c=cos(phi),s=sin(phi);for(int k=0;k<D;k++){double x=A[k][u],y=A[k][v];A[k][u]=c*x-s*y;A[k][v]=s*x+c*y;}for(int k=0;k<D;k++){double x=A[u][k],y=A[v][k];A[u][k]=c*x-s*y;A[v][k]=s*x+c*y;}for(int k=0;k<D;k++){double x=V[k][u],y=V[k][v];V[k][u]=c*x-s*y;V[k][v]=s*x+c*y;}}
 double mineig=D?A[0][0]:0;int mini=0;for(int i=1;i<D;i++)if(A[i][i]<mineig){mineig=A[i][i];mini=i;}double hstepdelta=0;
 if(mineig<-1e-15){std::vector<double>d(R);for(int i=0;i<D;i++)for(int j=0;j<R;j++)d[j]+=basis[i][j]*V[i][mini];double dm=0;for(double x:d)dm=std::max(dm,fabs(x));for(double&x:d)x/=dm;double cap=.1;for(int j=0;j<R;j++)if(d[j]>0)cap=std::min(cap,(1-p[j])/d[j]);else if(d[j]<0)cap=std::min(cap,-p[j]/d[j]);for(double step=.8*cap;step>1e-14;step*=.5){auto trial=p;for(int j=0;j<R;j++)trial[j]+=step*d[j];double val=fg(rows,trial,MASS);if(val<best-1e-16){p=trial;best=val;bestp=p;hstepdelta=val-baseline;history.push_back(val);break;}}}
 for(int it=0;it<200;it++){
  double cur=fg(rows,p,MASS,&g);std::fill(res.begin(),res.end(),0);maxres=0;
  for(int oid=0;oid<28;oid++){if(parent[oid]==0||parent[oid]==Q)continue;long double sw=0,sh=0;for(int j=0;j<R;j++)if(old[j]==oid){sw+=binmass[j];sh+=g[j];}double mean=(double)(sh/sw);for(int j=0;j<R;j++)if(old[j]==oid){res[j]=g[j]/binmass[j]-mean;maxres=std::max(maxres,fabs(res[j]));}}
  if(maxres<1e-14)break;for(double&x:res)x/=-maxres;double cap=.05;for(int j=0;j<R;j++)if(res[j]>0)cap=std::min(cap,(1-p[j])/res[j]);else if(res[j]<0)cap=std::min(cap,-p[j]/res[j]);bool moved=false;
  for(double step=.8*cap;step>1e-14;step*=.5){auto trial=p;for(int j=0;j<R;j++)trial[j]+=step*res[j];double val=fg(rows,trial,MASS);if(val<cur-1e-16){p=trial;moved=true;if(val<best){best=val;bestp=p;}break;}}
  if(!moved)break;if(it==0||it==4||it==19||it==99||it==199)history.push_back(best);
 }
 std::vector<uint64_t>rp(R);std::vector<double>rpd(R);for(int j=0;j<R;j++){rp[j]=llround(bestp[j]*Q);rpd[j]=(double)rp[j]/Q;}double rd=fg(rows,rpd,MASS);u128 exact=0;for(auto&r:rows){u128 a=1,b=1;for(auto id:r.id){a*=rp[id];b*=Q-rp[id];}exact+=(u128)r.count*(a+b);}u128 den=MASS;for(int i=0;i<6;i++)den*=Q;
 std::ofstream out(argv[1]);out<<std::setprecision(17)<<"{\n  \"schema\": \"quadratic-witt-refinement-v1\",\n  \"status\": \"completed\",\n  \"histogram_rows\": "<<rows.size()<<",\n  \"histogram_mass\": "<<MASS<<",\n  \"refined_bins\": 80,\n  \"fractional_split_bins\": "<<splitbins<<",\n  \"controls\": \"matched exact parent, componentwise complement, and independent literal translated enumeration passed\",\n  \"baseline\": "<<baseline<<",\n  \"initial_centered_gradient_max\": "<<initialmax<<",\n  \"initial_centered_gradient_energy\": "<<energy<<",\n  \"predicted_delta_for_normalized_step_0.01\": "<<predicted<<",\n  \"constrained_hessian_dimension\": "<<D<<",\n  \"constrained_hessian_min_eigenvalue_basis_coordinates\": "<<mineig<<",\n  \"hessian_step_delta\": "<<hstepdelta<<",\n  \"optimized_density\": "<<best<<",\n  \"history\": [";for(size_t i=0;i<history.size();i++){if(i)out<<", ";out<<history[i];}out<<"],\n  \"rational_denominator\": "<<Q<<",\n  \"rationalized_density\": "<<rd<<",\n  \"exact_numerator\": \""<<dec(exact)<<"\",\n  \"exact_denominator\": \""<<dec(den)<<"\",\n  \"beats_current_best\": "<<(rd<.03013890356539909?"true":"false")<<",\n  \"rationalized_parameters\": [";for(int j=0;j<R;j++){if(j)out<<", ";out<<rp[j];}out<<"]\n}\n";
 std::cout<<std::setprecision(17)<<"rows "<<rows.size()<<" baseline "<<baseline<<" maxres "<<maxres<<" predicted "<<predicted<<" best "<<best<<" rational "<<rd<<"\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
