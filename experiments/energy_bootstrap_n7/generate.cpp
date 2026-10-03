#include <algorithm>
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <numeric>
#include <vector>
#include <cstdint>
#include <csignal>
#include <unistd.h>
using namespace std;
int pos[7][7];
int sub(int bits,const vector<int>&v){int a=0,k=0;for(int i=0;i<v.size();i++)for(int j=i+1;j<v.size();j++,k++)a|=((bits>>pos[v[i]][v[j]])&1)<<k;return a;}
struct Block{int r,s,t,d;vector<int>lookup;};
int main(int argc,char**argv){alarm(175);assert(argc==3);int nb,ng;cin>>nb>>ng;assert(ng==1044);vector<int>graphs(ng);for(int&x:graphs)cin>>x;vector<Block>bs(nb);for(auto&b:bs){cin>>b.r>>b.s>>b.t>>b.d;b.lookup.resize(1<<(b.s*(b.s-1)/2));for(int&x:b.lookup)cin>>x;}
 int k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)pos[i][j]=pos[j][i]=k++;
 vector<int>owner(1<<21,-1),sizes(ng,0);array<int,7>p; iota(p.begin(),p.end(),0);vector<array<int,21>>trans;
 do{array<int,21>a;int k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)a[k++]=pos[p[i]][p[j]];trans.push_back(a);}while(next_permutation(p.begin(),p.end()));
 for(int g=0;g<ng;g++)for(auto&a:trans){int m=0;for(int k=0;k<21;k++)m|=((graphs[g]>>a[k])&1)<<k;assert(owner[m]==-1||owner[m]==g);owner[m]=g;}
 for(int x:owner){assert(x>=0);sizes[x]++;}ofstream o(argv[1],ios::binary);o.write((char*)&nb,4);o.write((char*)&ng,4);
 for(auto&b:bs){vector<uint16_t>C(size_t(ng)*b.d*b.d);vector<int>roots(b.r),left(b.s),right;iota(roots.begin(),roots.end(),0);iota(left.begin(),left.end(),0);right=roots;for(int j=0;j<b.s-b.r;j++)right.push_back(b.s+j);
  for(int m=0;m<(1<<21);m++){if(sub(m,roots)!=b.t)continue;int a=b.lookup[sub(m,left)],c=b.lookup[sub(m,right)];assert(a>=0&&c>=0);C[(size_t(owner[m])*b.d+a)*b.d+c]++;}
  for(int g=0;g<ng;g++){assert(5040%sizes[g]==0);for(int i=0;i<b.d;i++)for(int j=0;j<b.d;j++){size_t at=(size_t(g)*b.d+i)*b.d+j;C[at]*=5040/sizes[g];assert(C[at]<=5040);assert(C[at]==C[(size_t(g)*b.d+j)*b.d+i]||i!=j);}}
  o.write((char*)&b.d,4);o.write((char*)C.data(),C.size()*2);cerr<<"block "<<b.r<<' '<<b.t<<' '<<b.d<<" done\n";
 }
 vector<uint16_t>X(ng),Z(ng),obj(ng);for(int m=0;m<(1<<21);m++){bool a=__builtin_popcount(unsigned(sub(m,{0,1,2})))==1,b=__builtin_popcount(unsigned(sub(m,{3,4,5})))==1;X[owner[m]]+=a;Z[owner[m]]+=a&&b;}
 for(int g=0;g<ng;g++){X[g]*=5040/sizes[g];Z[g]*=5040/sizes[g];for(int a=0;a<7;a++)for(int b=a+1;b<7;b++)for(int c=b+1;c<7;c++)for(int d=c+1;d<7;d++){int t=sub(graphs[g],{a,b,c,d});obj[g]+=144*(t==0||t==63);}}
 for(auto*v:{&X,&Z,&obj})o.write((char*)v->data(),ng*2);
 // Independent six-vertex isomorphism ownership for deletion marginal.
 ifstream f(argv[2]);int n6;f>>n6;assert(n6==156);vector<int>g6(n6);for(int&v:g6)f>>v;vector<int>own6(1<<15,-1);array<int,6>v;iota(v.begin(),v.end(),0);int p6[6][6],e=0;for(int a=0;a<6;a++)for(int b=a+1;b<6;b++)p6[a][b]=p6[b][a]=e++;
 do{for(int g=0;g<n6;g++){int m=0,k=0;for(int a=0;a<6;a++)for(int b=a+1;b<6;b++)m|=((g6[g]>>p6[v[a]][v[b]])&1)<<k++;assert(own6[m]==-1||own6[m]==g);own6[m]=g;}}while(next_permutation(v.begin(),v.end()));
 vector<uint16_t>P(n6*ng);for(int g=0;g<ng;g++)for(int del=0;del<7;del++){vector<int>vs;for(int a=0;a<7;a++)if(a!=del)vs.push_back(a);int idx=own6[sub(graphs[g],vs)];assert(idx>=0);P[idx*ng+g]++;}o.write((char*)P.data(),P.size()*2);assert(o.good());cerr<<"PASS complete labelled coverage\n";
}
