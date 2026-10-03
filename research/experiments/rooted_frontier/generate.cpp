// Two-root five-vertex flags glued to eight vertices. Integer event table.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <vector>
#include <unistd.h>
using namespace std;
int main(int argc,char**argv){
 alarm(175);assert(argc==2);int n;cin>>n;vector<int>gs(n);for(auto&g:gs)cin>>g;
 int pos[8][8],k=0;for(int a=0;a<8;a++)for(int b=a+1;b<8;b++)pos[a][b]=pos[b][a]=k++;
 int p5[5][5];k=0;for(int a=0;a<5;a++)for(int b=a+1;b<5;b++)p5[a][b]=p5[b][a]=k++;
 array<int,1024>canon,ids;set<int> reps[2];
 for(int g=0;g<1024;g++){array<int,5>v={0,1,2,3,4};int best=1024;do{int h=0,j=0;for(int a=0;a<5;a++)for(int b=a+1;b<5;b++)h|=((g>>p5[v[a]][v[b]])&1)<<j++;best=min(best,h);}while(next_permutation(v.begin()+2,v.end()));canon[g]=best;reps[g&1].insert(best);}
 vector<int>rs[2];for(int t=0;t<2;t++)rs[t]=vector<int>(reps[t].begin(),reps[t].end());assert(rs[0].size()==rs[1].size());int d=rs[0].size();
 for(int g=0;g<1024;g++)ids[g]=lower_bound(rs[g&1].begin(),rs[g&1].end(),canon[g])-rs[g&1].begin();
 ofstream f(argv[1],ios::binary);int ne=1120;for(int x:{n,d,ne})f.write((char*)&x,4);for(auto&r:rs)f.write((char*)r.data(),r.size()*4);
 for(int g:gs){vector<uint16_t>events;events.reserve(ne*3);
 for(int a=0;a<8;a++)for(int b=0;b<8;b++)if(a!=b){vector<int>rest;for(int c=0;c<8;c++)if(c!=a&&c!=b)rest.push_back(c);
 for(int s=0;s<64;s++)if(__builtin_popcount((unsigned)s)==3){array<int,5>v={a,b},w={a,b};int vi=2,wi=2;for(int j=0;j<6;j++)if(s>>j&1)v[vi++]=rest[j];else w[wi++]=rest[j];auto sub=[&](auto&z){int h=0,j=0;for(int x=0;x<5;x++)for(int y=x+1;y<5;y++)h|=((g>>pos[z[x]][z[y]])&1)<<j++;return h;};int gv=sub(v),gw=sub(w);assert((gv&1)==(gw&1));events.push_back(gv&1);events.push_back(ids[gv]);events.push_back(ids[gw]);}}
 assert(events.size()==ne*3);f.write((char*)events.data(),events.size()*2);}
 assert(f.good());cout<<"graphs="<<n<<" flags/type="<<d<<" events/graph="<<ne<<endl;
}
