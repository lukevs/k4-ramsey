// Sparse N8 -> N7 marginal and disjoint four-pattern counts.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <vector>
#include <unistd.h>
using namespace std;
int main(int argc,char**argv){alarm(175);assert(argc==2);int n7,n8;cin>>n7>>n8;assert(n7==1044&&n8==12346);vector<int>g7(n7),g8(n8);for(int&v:g7)cin>>v;for(int&v:g8)cin>>v;array<int,64>type;for(int&v:type)cin>>v;int pos7[7][7],pos8[8][8],k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)pos7[i][j]=pos7[j][i]=k++;k=0;for(int i=0;i<8;i++)for(int j=i+1;j<8;j++)pos8[i][j]=pos8[j][i]=k++;
vector<int16_t>owner(1<<21,-1);array<int,7>v;iota(v.begin(),v.end(),0);vector<array<int,21>>maps;do{array<int,21>m;int k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)m[k++]=pos7[v[i]][v[j]];maps.push_back(m);}while(next_permutation(v.begin(),v.end()));
for(int g=0;g<n7;g++)for(auto&m:maps){int bits=0;for(int k=0;k<21;k++)bits|=((g7[g]>>m[k])&1)<<k;assert(owner[bits]==-1||owner[bits]==g);owner[bits]=g;}for(int v:owner)assert(v>=0);
vector<uint16_t>P(n8*8),J(n8*121),X(n8*11);
for(int g=0;g<n8;g++){
 auto sub=[&](const vector<int>&v){int bits=0,k=0;for(int i=0;i<v.size();i++)for(int j=i+1;j<v.size();j++)bits|=((g8[g]>>pos8[v[i]][v[j]])&1)<<k++;return bits;};
 for(int omit=0;omit<8;omit++){vector<int>v;for(int i=0;i<8;i++)if(i!=omit)v.push_back(i);P[g*8+omit]=owner[sub(v)];}
 for(int a=0;a<8;a++)for(int b=a+1;b<8;b++)for(int c=b+1;c<8;c++)for(int d=c+1;d<8;d++){
  vector<int>vs={a,b,c,d},ws;for(int i=0;i<8;i++)if(i!=a&&i!=b&&i!=c&&i!=d)ws.push_back(i);int i=type[sub(vs)],j=type[sub(ws)];X[g*11+i]++;J[g*121+i*11+j]++;
 }
}
ofstream f(argv[1],ios::binary);f.write((char*)&n7,4);f.write((char*)&n8,4);for(auto*p:{&P,&X,&J})f.write((char*)p->data(),p->size()*2);assert(f.good());cout<<"PASS: N7 labelled coverage, N8 deletion indices and 70 ordered disjoint four-set partitions per graph\n";
}
