// Independent per-representative permutation oracle, not labelled-orbit accumulation.
#include <algorithm>
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <numeric>
#include <vector>
#include <cstdint>
#include <unistd.h>
using namespace std;
struct Block{int r,s,t,d;vector<int>lookup;vector<uint16_t>C;};
int main(int argc,char**argv){alarm(175);assert(argc==2);int nb,ng;cin>>nb>>ng;vector<int>graphs(ng);for(int&v:graphs)cin>>v;vector<Block>bs(nb);for(auto&b:bs){cin>>b.r>>b.s>>b.t>>b.d;b.lookup.resize(1<<(b.s*(b.s-1)/2));for(int&v:b.lookup)cin>>v;}
 ifstream f(argv[1],ios::binary);int n,m;f.read((char*)&n,4);f.read((char*)&m,4);assert(n==nb&&m==ng);for(auto&b:bs){int d;f.read((char*)&d,4);assert(d==b.d);b.C.resize(size_t(ng)*d*d);f.read((char*)b.C.data(),b.C.size()*2);}
 vector<uint16_t>X(ng),Z(ng),obj(ng);for(auto*v:{&X,&Z,&obj})f.read((char*)v->data(),ng*2);
 int pos[7][7],k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)pos[i][j]=pos[j][i]=k++;
 vector<int>owner(1<<21,-1);long long entries=0;
 for(int g=0;g<ng;g++){
  vector<vector<int>>counts;for(auto&b:bs)counts.emplace_back(b.d*b.d,0);int xc=0,zc=0,oc=0;array<int,7>v;iota(v.begin(),v.end(),0);
  do{int A[7][7]={};int mask=0,k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++){A[i][j]=A[j][i]=(graphs[g]>>pos[v[i]][v[j]])&1;mask|=A[i][j]<<k++;}assert(owner[mask]==-1||owner[mask]==g);owner[mask]=g;
   auto sub=[&](vector<int>w){int code=0,k=0;for(int i=0;i<w.size();i++)for(int j=i+1;j<w.size();j++)code|=A[w[i]][w[j]]<<k++;return code;};
   bool a=A[0][1]+A[0][2]+A[1][2]==1,b=A[3][4]+A[3][5]+A[4][5]==1;xc+=a;zc+=a&&b;int K=sub({0,1,2,3});oc+=K==0||K==63;
   for(int bi=0;bi<nb;bi++){auto&b=bs[bi];vector<int>root(b.r),left(b.s),right;iota(root.begin(),root.end(),0);if(sub(root)!=b.t)continue;iota(left.begin(),left.end(),0);right=root;for(int j=0;j<b.s-b.r;j++)right.push_back(b.s+j);int l=b.lookup[sub(left)],r=b.lookup[sub(right)];assert(l>=0&&r>=0);counts[bi][l*b.d+r]++;}
  }while(next_permutation(v.begin(),v.end()));
  assert(xc==X[g]&&zc==Z[g]&&oc==obj[g]);for(int bi=0;bi<nb;bi++){auto&b=bs[bi];for(int j=0;j<b.d*b.d;j++){assert(counts[bi][j]==b.C[size_t(g)*b.d*b.d+j]);entries++;}}
 }
 assert(all_of(owner.begin(),owner.end(),[](int g){return g>=0;}));cout<<"PASS "<<entries<<" exact entries; 2097152 labelled graphs; 1044 representatives; all observable and objective coefficients\n";
}
