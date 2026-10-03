#include <vector>
#include <random>
#include <fstream>
#include <iostream>
#include <cmath>
#include <chrono>
#include <unistd.h>
#include <cstdint>
#include <array>
using namespace std;using U=uint64_t;using I=int64_t;
int n,L;vector<vector<U>>R;
int get(int a,int b){return (R[a][b/64]>>(b%64))&1;}
void flip(int a,int b){R[a][b/64]^=U(1)<<(b%64);if(a!=b)R[b][a/64]^=U(1)<<(a%64);}
int mono(array<int,4>a){int c=get(a[0],a[1]);for(int i=0;i<4;i++)for(int j=0;j<i;j++)if(get(a[i],a[j])!=c)return 0;return 1;}
I full(){I total=0;vector<U>v(L);for(int col=0;col<2;col++)for(int i=0;i<n;i++)for(int j=0;j<n;j++)if(get(i,j)==col){for(int k=0;k<L;k++)v[k]=(col?R[i][k]:~R[i][k])&(col?R[j][k]:~R[j][k]);if(n%64)v[L-1]&=(U(1)<<(n%64))-1;for(int l=0;l<L;l++){U z=v[l];while(z){int b=64*l+__builtin_ctzll(z);z&=z-1;for(int k=0;k<L;k++)total+=__builtin_popcountll(v[k]&(col?R[b][k]:~R[b][k]));}}}return total;}
I distinct(int u,int v,int col){vector<U>s(L);for(int k=0;k<L;k++)s[k]=(col?R[u][k]:~R[u][k])&(col?R[v][k]:~R[v][k]);if(n%64)s[L-1]&=(U(1)<<(n%64))-1;s[u/64]&=~(U(1)<<(u%64));s[v/64]&=~(U(1)<<(v%64));I count=0;for(int l=0;l<L;l++){U z=s[l];while(z){int a=64*l+__builtin_ctzll(z);z&=z-1;for(int k=0;k<L;k++)count+=__builtin_popcountll(s[k]&(col?R[a][k]:~R[a][k]));count-=get(a,a)==col;}}return count/2;}
I repeats(int u,int v){I ans=0;if(u!=v){for(int a=0;a<n;a++)if(a!=u&&a!=v)ans+=12*(mono({u,u,v,a})+mono({u,v,v,a})+mono({u,v,a,a}));ans+=4*(mono({u,u,u,v})+mono({u,v,v,v}))+6*mono({u,u,v,v});}else{ans+=mono({u,u,u,u});for(int a=0;a<n;a++)if(a!=u){ans+=4*mono({u,u,u,a})+6*mono({u,u,a,a});for(int b=a+1;b<n;b++)if(b!=u)ans+=12*mono({u,u,a,b});}}return ans;}
I delta(int u,int v){int c=get(u,v);I d=u==v?0:24*(distinct(u,v,1-c)-distinct(u,v,c));d-=repeats(u,v);flip(u,v);d+=repeats(u,v);flip(u,v);return d;}
int main(int argc,char**argv){alarm(175);string mode=argv[1];n=atoi(argv[2]);L=(n+63)/64;int seed=atoi(argv[3]),steps=atoi(argv[4]);string init=argv[5],out=argv[6];mt19937 rng(seed);R.assign(n,vector<U>(L));for(int i=0;i<n;i++)for(int j=0;j<=i;j++){int w=__builtin_popcount(unsigned(i^j));int bit=init=="control"?(w==0||w==1||w==3||w==4||w==7||w==8||w==10):rng()%2;if(bit)flip(i,j);}auto start=chrono::steady_clock::now();I cur=full(),initial=cur,best=cur;auto saved=R;int accepted=0,uphill=0;for(int t=0;t<steps;t++){int u=rng()%n,v=rng()%n;double uniform=generate_canonical<double,53>(rng);I d=delta(u,v);if(mode=="validate"){flip(u,v);I q=full();if(q!=cur+d){cerr<<"FAIL "<<u<<" "<<v<<" "<<q-cur<<" "<<d<<endl;return 2;}cur=q;continue;}double temp=double(n)*n*.1*pow(.0001,double(t)/max(1,steps-1));if(d<=0||(mode=="anneal"&&uniform<exp(-double(d)/temp))){flip(u,v);cur+=d;accepted++;uphill+=d>0;if(cur<best){best=cur;saved=R;}}}if(mode=="validate"){cout<<"delta validation passed "<<n<<" "<<steps<<endl;return 0;}R=saved;I recount=full();if(recount!=best)return 3;ofstream f(out);f<<"{\"mode\":\""<<mode<<"\",\"n\":"<<n<<",\"seed\":"<<seed<<",\"steps\":"<<steps<<",\"initialization\":\""<<init<<"\",\"initial_count\":"<<initial<<",\"best_count\":"<<best<<",\"recount\":"<<recount<<",\"denominator\":"<<U(n)*n*n*n<<",\"accepted\":"<<accepted<<",\"uphill\":"<<uphill<<",\"pid\":"<<getpid()<<",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<",\"red_rows\":[";for(int i=0;i<n;i++){if(i)f<<",";f<<"\"";for(int j=0;j<n;j++)f<<get(i,j);f<<"\"";}f<<"]}\n";cout<<out<<" "<<best<<"/"<<U(n)*n*n*n<<" accepted "<<accepted<<" uphill "<<uphill<<endl;
}
