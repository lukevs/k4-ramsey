#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
#include <Accelerate/Accelerate.h>

using I128=__int128_t; using U128=__uint128_t; using U64=uint64_t;
static std::string dec(I128 x){if(!x)return"0";bool neg=x<0;U128 u=neg?U128(-x):U128(x);std::string s;while(u){s.push_back(char('0'+u%10));u/=10;}if(neg)s.push_back('-');std::reverse(s.begin(),s.end());return s;}

static I128 formula_c2(const std::vector<std::vector<U64>>&p,const std::vector<std::vector<int>>&d,U64 q){
 int n=p.size();I128 adj=0,dis=0;
 for(int i=0;i<n;i++)for(int j=0;j<n;j++)for(int k=0;k<n;k++){
  I128 zr=0,zb=0;for(int l=0;l<n;l++){zr+=I128(p[i][l])*p[j][l]*p[k][l];zb+=I128(q-p[i][l])*(q-p[j][l])*(q-p[k][l]);}
  adj+=I128(d[i][j])*d[i][k]*(I128(p[j][k])*zr+I128(q-p[j][k])*zb);
  for(int l=0;l<n;l++)dis+=I128(d[i][j])*d[k][l]*(I128(p[i][k])*p[i][l]*p[j][k]*p[j][l]+I128(q-p[i][k])*(q-p[i][l])*(q-p[j][k])*(q-p[j][l]));
 }
 return 12*adj+3*dis;
}
static I128 literal_c2(const std::vector<std::vector<U64>>&p,const std::vector<std::vector<int>>&d,U64 q){
 int n=p.size();I128 answer=0;const int ends[6][2]={{0,1},{0,2},{0,3},{1,2},{1,3},{2,3}};
 for(int a=0;a<n;a++)for(int b=0;b<n;b++)for(int c=0;c<n;c++)for(int e=0;e<n;e++){
  int v[4]={a,b,c,e};U64 x[6],y[6];int z[6];for(int h=0;h<6;h++){x[h]=p[v[ends[h][0]]][v[ends[h][1]]];y[h]=q-x[h];z[h]=d[v[ends[h][0]]][v[ends[h][1]]];}
  for(int h=0;h<6;h++)for(int g=h+1;g<6;g++){I128 red=1,blue=1;for(int t=0;t<6;t++)if(t!=h&&t!=g){red*=x[t];blue*=y[t];}answer+=I128(z[h])*z[g]*(red+blue);}
 }
 return answer;
}
static double assembled_dense_c2(const std::vector<std::vector<U64>>&p,const std::vector<std::vector<int>>&d,U64 q){
 int n=p.size(),m=n*(n-1)/2;std::vector<std::vector<int>>id(n,std::vector<int>(n,-1));std::vector<std::vector<std::pair<int,int>>>inc(n);std::vector<int>dv;
 for(int i=0;i<n;i++)for(int j=0;j<i;j++){int e=dv.size();id[i][j]=id[j][i]=e;inc[i].push_back({j,e});inc[j].push_back({i,e});dv.push_back(d[i][j]);}
 std::vector<std::vector<double>>x(n,std::vector<double>(n));for(int i=0;i<n;i++)for(int j=0;j<n;j++)x[i][j]=double(p[i][j])/q;std::vector<double>C(size_t(m)*m);
 for(int i=0;i<n;i++)for(auto[j,e]:inc[i])for(auto[k,f]:inc[i]){double zr=0,zb=0;for(int l=0;l<n;l++){zr+=x[i][l]*x[j][l]*x[k][l];zb+=(1-x[i][l])*(1-x[j][l])*(1-x[k][l]);}C[size_t(e)*m+f]+=12*(x[j][k]*zr+(1-x[j][k])*zb);}
 std::vector<std::array<int,3>>oriented;for(int i=0;i<n;i++)for(auto[j,e]:inc[i])oriented.push_back({i,j,e});for(auto a:oriented)for(auto b:oriented){int i=a[0],j=a[1],e=a[2],k=b[0],l=b[1],f=b[2];C[size_t(e)*m+f]+=3*(x[i][k]*x[i][l]*x[j][k]*x[j][l]+(1-x[i][k])*(1-x[i][l])*(1-x[j][k])*(1-x[j][l]));}
 double answer=0;for(int e=0;e<m;e++)for(int f=0;f<m;f++)answer+=double(dv[e])*dv[f]*C[size_t(e)*m+f];return answer;
}
static void selftest(){
 const U64 q=7;
 std::vector<std::pair<std::vector<std::vector<U64>>,std::vector<std::vector<int>>>> tests;
 tests.push_back({{{0,2},{2,5}},{{1,2},{2,-1}}});
 tests.push_back({{{0,2,5},{2,1,3},{5,3,4}},{{0,1,-1},{1,0,0},{-1,0,0}}});
 tests.push_back({{{0,2,5,1},{2,1,3,6},{5,3,4,2},{1,6,2,0}},{{0,0,1,0},{0,0,0,-1},{1,0,0,0},{0,-1,0,0}}});
 for(auto&[p,d]:tests){auto a=formula_c2(p,d,q),b=literal_c2(p,d,q);if(a!=b)throw std::runtime_error("tiny Hessian mismatch");auto pc=p;auto dc=d;for(auto&r:pc)for(auto&x:r)x=q-x;for(auto&r:dc)for(auto&x:r)x=-x;if(formula_c2(pc,dc,q)!=a)throw std::runtime_error("complement Hessian mismatch");}
 // Exercise the production incidence-matrix assembly itself, independently
 // of the symbolic formula, on several deterministic off-diagonal directions.
 for(int which=0;which<3;which++)for(auto&[p,unused]:tests)if(p.size()>=2){int n=p.size();std::vector<std::vector<int>>d(n,std::vector<int>(n));for(int i=0;i<n;i++)for(int j=0;j<i;j++)d[i][j]=d[j][i]=((i*7+j*11+which*5)%7)-3;I128 exact=literal_c2(p,d,q);double want=double(exact)/std::pow(double(q),4),got=assembled_dense_c2(p,d,q);if(std::abs(got-want)>1e-10*(1+std::abs(want)))throw std::runtime_error("dense assembly mismatch");}
}
struct Edge{int i,j;U64 p;I128 gradient;int cls;};
int main(){try{
 selftest();int n;U64 q;if(!(std::cin>>n>>q)||n<=0||!q)throw std::runtime_error("bad header");std::vector<std::vector<U64>>p(n,std::vector<U64>(n));for(auto&r:p)for(auto&x:r)if(!(std::cin>>x)||x>q)throw std::runtime_error("bad matrix");for(int i=0;i<n;i++)for(int j=0;j<n;j++)if(p[i][j]!=p[j][i])throw std::runtime_error("asymmetric");
 std::vector<Edge>edges;std::vector<std::vector<int>>id(n,std::vector<int>(n,-1));std::vector<std::vector<std::pair<int,int>>>inc(n);
 for(int i=0;i<n;i++)for(int j=0;j<i;j++)if(p[i][j]&&p[i][j]<q){int e=edges.size();edges.push_back({i,j,p[i][j],0,-1});id[i][j]=id[j][i]=e;inc[i].push_back({j,e});inc[j].push_back({i,e});}
 int m=edges.size();if(!m)throw std::runtime_error("no fractional edges");
 const I128 gradient_bound=I128(12)*n*n*I128(q)*q*q*q*q;
 std::map<I128,int> classes;
 for(auto&edge:edges){int i=edge.i,j=edge.j;I128 sr=0,sb=0;for(int k=0;k<n;k++)for(int l=0;l<n;l++){sr+=I128(p[i][k])*p[j][k]*p[i][l]*p[j][l]*p[k][l];sb+=I128(q-p[i][k])*(q-p[j][k])*(q-p[i][l])*(q-p[j][l])*(q-p[k][l]);}edge.gradient=12*(sr-sb);if(edge.gradient>gradient_bound||edge.gradient<-gradient_bound)throw std::runtime_error("gradient bound");auto[it,fresh]=classes.emplace(edge.gradient,classes.size());edge.cls=it->second;}
 int class_count=classes.size();std::vector<std::vector<int>>members(class_count);for(int e=0;e<m;e++)members[edges[e].cls].push_back(e);
 const double iq=1.0/double(q);std::vector<std::vector<double>>x(n,std::vector<double>(n));for(int i=0;i<n;i++)for(int j=0;j<n;j++)x[i][j]=p[i][j]*iq;
 std::vector<double>C(size_t(m)*m,0.0);
 for(int i=0;i<n;i++)for(auto[j,e]:inc[i])for(auto[k,f]:inc[i]){double zr=0,zb=0;for(int l=0;l<n;l++){zr+=x[i][l]*x[j][l]*x[k][l];zb+=(1-x[i][l])*(1-x[j][l])*(1-x[k][l]);}double z=x[j][k]*zr+(1-x[j][k])*zb;C[size_t(e)*m+f]+=12*z;}
 std::vector<std::array<int,3>>oriented;for(int i=0;i<n;i++)for(auto[j,e]:inc[i])oriented.push_back({i,j,e});
 for(auto a:oriented)for(auto b:oriented){int i=a[0],j=a[1],e=a[2],k=b[0],l=b[1],f=b[2];double z=x[i][k]*x[i][l]*x[j][k]*x[j][l]+(1-x[i][k])*(1-x[i][l])*(1-x[j][k])*(1-x[j][l]);C[size_t(e)*m+f]+=3*z;}
 double symmetry=0,alpha=0;for(int e=0;e<m;e++){double rowsum=0;for(int f=0;f<m;f++){symmetry=std::max(symmetry,std::abs(C[size_t(e)*m+f]-C[size_t(f)*m+e]));rowsum+=std::abs(C[size_t(e)*m+f]);}alpha=std::max(alpha,2*rowsum);}
 std::vector<double>gvec(m);long double gscale=0;for(auto&e:edges)gscale=std::max(gscale,std::abs((long double)e.gradient));long double gnorm=0;for(int e=0;e<m;e++){gvec[e]=double((long double)edges[e].gradient/gscale);gnorm+=(long double)gvec[e]*gvec[e];}gnorm=std::sqrt(gnorm);for(double&z:gvec)z/=double(gnorm);
 auto project=[&](std::vector<double>&v){double dot=0;for(int e=0;e<m;e++)dot+=gvec[e]*v[e];for(int e=0;e<m;e++)v[e]-=dot*gvec[e];};
 auto apply=[&](const std::vector<double>&v){std::vector<double>w(m);for(int e=0;e<m;e++){double z=0;for(int f=0;f<m;f++)z+=C[size_t(e)*m+f]*v[f];w[e]=z;}project(w);return w;};
 // Form P C P explicitly for the full codimension-one exact-gradient
 // hyperplane.  The gradient direction becomes the sole null direction.
 std::vector<double>cg(m);for(int e=0;e<m;e++)for(int f=0;f<m;f++)cg[e]+=C[size_t(e)*m+f]*gvec[f];double grand=0;for(int e=0;e<m;e++)grand+=gvec[e]*cg[e];
 std::vector<double>A(size_t(m)*m);for(int e=0;e<m;e++)for(int f=0;f<m;f++)A[size_t(e)*m+f]=C[size_t(e)*m+f]-cg[e]*gvec[f]-gvec[e]*cg[f]+grand*gvec[e]*gvec[f];
 double projected_symmetry=0;for(int e=0;e<m;e++)for(int f=0;f<m;f++)projected_symmetry=std::max(projected_symmetry,std::abs(A[size_t(e)*m+f]-A[size_t(f)*m+e]));std::vector<double>pg=gvec;project(pg);double pg_residual=0;for(double z:pg)pg_residual+=z*z;pg_residual=std::sqrt(pg_residual);std::vector<double>probe(m);for(int e=0;e<m;e++)probe[e]=std::sin(e+1.0);project(probe);auto twice=probe;project(twice);double idempotence=0;for(int e=0;e<m;e++)idempotence=std::max(idempotence,std::abs(twice[e]-probe[e]));
 __LAPACK_int nn=m,lda=m,info=0,lwork=-1,liwork=-1;char job='V',uplo='U';double work_query;__LAPACK_int iwork_query;std::vector<double>eval(m);
 dsyevd_(&job,&uplo,&nn,A.data(),&lda,eval.data(),&work_query,&lwork,&iwork_query,&liwork,&info);if(info)throw std::runtime_error("dsyevd workspace query failed");
 lwork=__LAPACK_int(work_query);liwork=iwork_query;std::vector<double>work(lwork);std::vector<__LAPACK_int>iwork(liwork);
 dsyevd_(&job,&uplo,&nn,A.data(),&lda,eval.data(),work.data(),&lwork,iwork.data(),&liwork,&info);if(info)throw std::runtime_error("dsyevd failed");
 double best=1e300,bestres=1e300;int bestindex=-1;std::vector<double>bestv;
 for(int z=0;z<m;z++){double gdot=0;for(int e=0;e<m;e++)gdot+=gvec[e]*A[size_t(z)*m+e];if(std::abs(gdot)>1e-7)continue;if(eval[z]<best){best=eval[z];bestindex=z;bestv.assign(A.begin()+size_t(z)*m,A.begin()+size_t(z+1)*m);}}
 if(bestindex<0)throw std::runtime_error("no constrained eigendirection");auto av=apply(bestv);double ray=0;for(int e=0;e<m;e++)ray+=bestv[e]*av[e];for(int e=0;e<m;e++)av[e]-=ray*bestv[e];bestres=0;for(double z:av)bestres+=z*z;bestres=std::sqrt(bestres);
 double bestgdot=0;for(int e=0;e<m;e++)bestgdot+=gvec[e]*bestv[e];
 std::cout<<std::setprecision(17)<<m<<' '<<class_count<<' '<<symmetry<<' '<<alpha<<' '<<ray<<' '<<bestres<<' '<<bestindex<<' '<<m<<' '<<dec(gradient_bound)<<' '<<bestgdot<<' '<<pg_residual<<' '<<idempotence<<' '<<projected_symmetry;
 for(int z=0;z<std::min(m,8);z++)std::cout<<' '<<eval[z];std::cout<<"\n";
 for(int e=0;e<m;e++)std::cout<<edges[e].i<<' '<<edges[e].j<<' '<<edges[e].p<<' '<<edges[e].cls<<' '<<dec(edges[e].gradient)<<' '<<std::setprecision(17)<<bestv[e]<<"\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
