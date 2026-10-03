#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

struct Mono { std::array<int,5> e{}; long double c=0; };

static int code(const std::array<int,5>& e) {
  int x=0,m=1; for(int i=0;i<5;i++){x+=e[i]*m;m*=5;} return x;
}

static long double powi(long double x,int e){long double r=1;while(e--)r*=x;return r;}

static long double eval(const std::vector<Mono>& ms,const std::array<long double,5>& w,
                        std::array<long double,5>* gp=nullptr,
                        std::array<std::array<long double,5>,5>* hp=nullptr) {
  long double f=0; if(gp)gp->fill(0); if(hp)for(auto& r:*hp)r.fill(0);
  for(const auto& m:ms){
    long double base=m.c;for(int i=0;i<5;i++)base*=powi(w[i],m.e[i]);f+=base;
    if(gp)for(int i=0;i<5;i++)if(m.e[i]){
      long double x=m.c*m.e[i];for(int j=0;j<5;j++)x*=powi(w[j],m.e[j]-(i==j));(*gp)[i]+=x;
    }
    if(hp)for(int i=0;i<5;i++)for(int j=0;j<5;j++){
      int factor=m.e[i]*(m.e[j]-(i==j));if(!factor)continue;
      long double x=m.c*factor;for(int k=0;k<5;k++)x*=powi(w[k],m.e[k]-(k==i)-(k==j));(*hp)[i][j]+=x;
    }
  } return f;
}

static void tiny_oracle(){
  constexpr int B=2,T=3,Q=7,D=6,N=B*D; const int mass[T]={1,2,3};
  int p[B][B][T][T];
  for(int a=0;a<B;a++)for(int b=a;b<B;b++)for(int s=0;s<T;s++)for(int t=0;t<T;t++){
    if(a==b && t<s)continue; int v=(1+3*a+5*b+2*s+4*t+s*t)%8;
    p[a][b][s][t]=v;p[b][a][t][s]=v;
  }
  unsigned long long compressed=0,literal=0;
  for(int a=0;a<B;a++)for(int b=0;b<B;b++)for(int c=0;c<B;c++)for(int d=0;d<B;d++)
    for(int s=0;s<T;s++)for(int t=0;t<T;t++)for(int u=0;u<T;u++)for(int v=0;v<T;v++){
      int x[6]={p[a][b][s][t],p[a][c][s][u],p[a][d][s][v],p[b][c][t][u],p[b][d][t][v],p[c][d][u][v]};
      unsigned long long r=1,z=1;for(int e:x){r*=e;z*=Q-e;}compressed+=(r+z)*mass[s]*mass[t]*mass[u]*mass[v];
    }
  std::array<int,D> typ{0,1,1,2,2,2};
  for(int i=0;i<N;i++)for(int j=0;j<N;j++)for(int k=0;k<N;k++)for(int l=0;l<N;l++){
    int ba=i/D,bb=j/D,bc=k/D,bd=l/D,s=typ[i%D],t=typ[j%D],u=typ[k%D],v=typ[l%D];
    int x[6]={p[ba][bb][s][t],p[ba][bc][s][u],p[ba][bd][s][v],p[bb][bc][t][u],p[bb][bd][t][v],p[bc][bd][u][v]};
    unsigned long long r=1,z=1;for(int e:x){r*=e;z*=Q-e;}literal+=r+z;
  }
  if(compressed!=literal)throw std::runtime_error("tiny weighted literal mismatch");
}

int main(int argc,char** argv){
 try{
  if(argc!=3)throw std::runtime_error("usage: screen certificate report.json");tiny_oracle();
  std::ifstream in(argv[1]);int n,q,b,t,k,h;in>>n>>q>>b>>t>>k>>h;
  if(n!=960||b!=192||t!=5)throw std::runtime_error("unexpected certificate metadata");
  std::vector<std::array<int,25>> ker(k);for(auto& a:ker)for(int& x:a)in>>x;
  std::array<long double,3125> coeff{}; uint64_t histmass=0;
  const long double norm=powi((long double)b,4)*powi((long double)q,6);
  for(int row=0;row<h;row++){
    int id[6];uint64_t count;for(int& x:id)in>>x;in>>count;histmass+=count;
    for(int a=0;a<5;a++)for(int c=0;c<5;c++)for(int d=0;d<5;d++)for(int e=0;e<5;e++){
      int x[6]={ker[id[0]][5*a+c],ker[id[1]][5*a+d],ker[id[2]][5*a+e],ker[id[3]][5*c+d],ker[id[4]][5*c+e],ker[id[5]][5*d+e]};
      long double red=1,blue=1;for(int z:x){red*=z;blue*=q-z;}
      std::array<int,5> ex{};ex[a]++;ex[c]++;ex[d]++;ex[e]++;
      coeff[code(ex)]+=(long double)count*(red+blue)/norm;
    }
  }
  if(histmass!=(uint64_t)b*b*b*b)throw std::runtime_error("histogram mass mismatch");
  std::vector<Mono> ms;for(int e0=0;e0<=4;e0++)for(int e1=0;e1<=4-e0;e1++)for(int e2=0;e2<=4-e0-e1;e2++)for(int e3=0;e3<=4-e0-e1-e2;e3++){
    int e4=4-e0-e1-e2-e3;std::array<int,5> ex{e0,e1,e2,e3,e4};ms.push_back({ex,coeff[code(ex)]});
  }
  if(ms.size()!=70)throw std::runtime_error("monomial count mismatch");
  std::array<long double,5> uniform{.2L,.2L,.2L,.2L,.2L},g;std::array<std::array<long double,5>,5> H;
  long double baseline=eval(ms,uniform,&g,&H),gm=0;for(auto x:g)gm+=x;gm/=5;
  long double pg=0;for(auto x:g)pg=std::max(pg,std::abs(x-gm));
  // Projected Hessian minimum, estimated by deterministic tangent power descent.
  long double minrq=1e100L;std::mt19937_64 rng(20260927);
  for(int z=0;z<200;z++){std::array<long double,5> v;long double mean=0;for(auto& x:v){x=(long double)((int)(rng()%2001)-1000);mean+=x;}mean/=5;long double nn=0;for(auto& x:v){x-=mean;nn+=x*x;}for(auto& x:v)x/=sqrtl(nn);
    for(int it=0;it<80;it++){std::array<long double,5> y{};for(int i=0;i<5;i++)for(int j=0;j<5;j++)y[i]+=H[i][j]*v[j];long double ym=0;for(auto x:y)ym+=x;ym/=5;for(auto& x:y)x-=ym;
      long double rq=0;for(int i=0;i<5;i++)rq+=v[i]*y[i]; long double step=0.02L/(1+fabsl(rq));nn=0;for(int i=0;i<5;i++){v[i]-=step*y[i];nn+=v[i]*v[i];}for(auto& x:v)x/=sqrtl(nn);
    }long double rq=0;for(int i=0;i<5;i++)for(int j=0;j<5;j++)rq+=v[i]*H[i][j]*v[j];minrq=std::min(minrq,rq);
  }
  // Continuous softmax Adam, with uniform and deterministic random starts.
  long double best=baseline;std::array<long double,5> bestw=uniform;
  for(int start=0;start<12;start++){std::array<long double,5> y{},m{},v{};if(start)for(auto& x:y)x=((int)(rng()%2001)-1000)/1000.0L;
    for(int it=1;it<=4000;it++){long double mx=*std::max_element(y.begin(),y.end()),sum=0;std::array<long double,5>w;for(int i=0;i<5;i++){w[i]=expl(y[i]-mx);sum+=w[i];}for(auto& x:w)x/=sum;
      std::array<long double,5> gg;long double f=eval(ms,w,&gg,nullptr),dot=0;for(int i=0;i<5;i++)dot+=w[i]*gg[i];if(f<best){best=f;bestw=w;}
      long double lr=.05L*(.15L+.85L*(1-(long double)it/4000));for(int i=0;i<5;i++){long double gy=w[i]*(gg[i]-dot);m[i]=.9L*m[i]+.1L*gy;v[i]=.999L*v[i]+.001L*gy*gy;y[i]-=lr*(m[i]/(1-powl(.9L,it)))/(sqrtl(v[i]/(1-powl(.999L,it)))+1e-18L);}
    }
  }
  // Exhaust all nonnegative integer mass vectors with denominator <=16.
  long double ratbest=baseline;std::array<int,5> bm{1,1,1,1,1};int bd=5;
  for(int D=1;D<=16;D++)for(int a=0;a<=D;a++)for(int c=0;c<=D-a;c++)for(int d=0;d<=D-a-c;d++)for(int e=0;e<=D-a-c-d;e++){
    int f=D-a-c-d-e;std::array<long double,5>w{(long double)a/D,(long double)c/D,(long double)d/D,(long double)e/D,(long double)f/D};long double val=eval(ms,w);
    if(val<ratbest){ratbest=val;bm={a,c,d,e,f};bd=D;}
  }
  std::ofstream out(argv[2]);out<<std::setprecision(20);
  out<<"{\n  \"schema\": \"latent-common-weights-screen-v1\",\n  \"status\": \"completed\",\n  \"tiny_literal_oracle\": \"passed\",\n  \"monomial_count\": 70,\n";
  out<<"  \"baseline\": "<<(double)baseline<<",\n  \"projected_gradient_inf\": "<<(double)pg<<",\n  \"projected_hessian_min_estimate\": "<<(double)minrq<<",\n";
  out<<"  \"gradient\": [";for(int i=0;i<5;i++){if(i)out<<", ";out<<(double)g[i];}out<<"],\n";
  out<<"  \"continuous_best\": "<<(double)best<<",\n  \"continuous_weights\": [";for(int i=0;i<5;i++){if(i)out<<", ";out<<(double)bestw[i];}out<<"],\n";
  out<<"  \"rational_best\": "<<(double)ratbest<<",\n  \"rational_denominator\": "<<bd<<",\n  \"rational_masses\": [";for(int i=0;i<5;i++){if(i)out<<", ";out<<bm[i];}out<<"],\n";
  out<<"  \"decision\": \""<<(ratbest<baseline?"admit_rational_candidate":"stop_no_improving_rational_or_continuous_direction")<<"\"\n}\n";
  std::cout<<std::setprecision(20)<<"baseline "<<(double)baseline<<" pg "<<(double)pg<<" mineig "<<(double)minrq<<" continuous "<<(double)best<<" rational "<<(double)ratbest<<" D "<<bd<<" masses";for(int x:bm)std::cout<<' '<<x;std::cout<<'\n';
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
