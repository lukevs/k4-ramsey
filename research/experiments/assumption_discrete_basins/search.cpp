#include <vector>
#include <random>
#include <fstream>
#include <iostream>
#include <cmath>
#include <chrono>
#include <unistd.h>
#include <cstdint>
using namespace std;
using U=uint64_t;
int n,L,kind; vector<int>s; vector<vector<U>> R;
int diff(int a,int b){return kind==0?(a^b):(b-a+n)%n;}
void build(){R.assign(n,vector<U>(L));for(int a=0;a<n;a++)for(int b=0;b<n;b++)if(s[diff(a,b)])R[a][b/64]|=U(1)<<(b%64);}
U count(){build();U total=0;vector<U> v(L);for(int col=0;col<2;col++)for(int a=0;a<n;a++)if(s[a]==col){for(int l=0;l<L;l++){U x=col?R[0][l]:~R[0][l],y=col?R[a][l]:~R[a][l];v[l]=x&y;}if(n%64)v[L-1]&=(U(1)<<(n%64))-1;for(int l=0;l<L;l++){U z=v[l];while(z){int b=64*l+__builtin_ctzll(z);z&=z-1;for(int k=0;k<L;k++)total+=__builtin_popcountll(v[k]&(col?R[b][k]:~R[b][k]));}}}return total;}
U literal(){U tot=0;for(int a=0;a<n;a++)for(int b=0;b<n;b++)for(int c=0;c<n;c++)for(int d=0;d<n;d++){int x=s[diff(a,b)];if(s[diff(a,c)]==x&&s[diff(a,d)]==x&&s[diff(b,c)]==x&&s[diff(b,d)]==x&&s[diff(c,d)]==x)tot++;}return tot;}
void flip(int x){s[x]^=1;int y=diff(x,0);if(y!=x)s[y]^=1;}
int main(int argc,char**argv){alarm(175);string mode=argv[1];kind=atoi(argv[2]);n=atoi(argv[3]);L=(n+63)/64;int seed=atoi(argv[4]),steps=atoi(argv[5]);mt19937 rng(seed);s.assign(n,0);if(mode=="validate"){for(int t=0;t<12;t++){for(int i=0;i<n;i++)if(i<=diff(i,0)){s[i]=rng()%2;s[diff(i,0)]=s[i];}U a=count()*n,b=literal();if(a!=b)return 2;}cout<<"tiny pass "<<n<<endl;return 0;}
string init=argv[6],out=argv[7];if(init=="control"||init=="damaged"){for(int i=0;i<n;i++){int w=__builtin_popcount((unsigned)i);s[i]=(w==0||w==1||w==3||w==4||w==7||w==8||w==10);}if(init=="damaged")for(int j=0;j<8;j++)flip(rng()%n);}else{for(int i=0;i<n;i++)if(i<=diff(i,0)){s[i]=rng()%2;s[diff(i,0)]=s[i];}}
auto st=chrono::steady_clock::now();U cur=count(),best=cur,initial=cur;vector<int>bs=s;int accepted=0,uphill=0;for(int t=0;t<steps;t++){int x=rng()%n;double uniform=generate_canonical<double,53>(rng);flip(x);U q=count();double temp=double(n)*n*.20*pow(.0001,double(t)/max(1,steps-1));bool ok=q<=cur||(mode=="anneal"&&uniform<exp(-(double(q)-double(cur))/temp));if(ok){accepted++;uphill+=q>cur;cur=q;if(q<best){best=q;bs=s;}}else flip(x);}s=bs;U recount=count();ofstream f(out);f<<"{\"mode\":\""<<mode<<"\",\"group\":\""<<(kind==0?"F2":"cyclic")<<"\",\"n\":"<<n<<",\"seed\":"<<seed<<",\"steps\":"<<steps<<",\"initialization\":\""<<init<<"\",\"initial_rooted_count\":"<<initial<<",\"best_rooted_count\":"<<best<<",\"recount\":"<<recount<<",\"denominator\":"<<U(n)*n*n<<",\"accepted\":"<<accepted<<",\"uphill\":"<<uphill<<",\"pid\":"<<getpid()<<",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-st).count()<<",\"generators\":[";for(int i=0;i<n;i++)f<<(i?",":"")<<s[i];f<<"]}\n";cout<<out<<" "<<best<<"/"<<U(n)*n*n<<" accepted "<<accepted<<" uphill "<<uphill<<endl;
}
