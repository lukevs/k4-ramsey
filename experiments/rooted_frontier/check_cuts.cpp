// Independent square-coefficient recount using injected full labelled flag lookup.
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <unistd.h>
using namespace std;
int main(int argc,char**argv){alarm(175);assert(argc==2);int n,d,nc;cin>>n>>d>>nc;
 vector<uint32_t>gs(n);for(auto&v:gs)cin>>v;array<int,1024>flag;for(auto&v:flag)cin>>v;
 vector<int>types(nc);vector<vector<int64_t>>vs(nc,vector<int64_t>(d));for(int c=0;c<nc;c++){cin>>types[c];for(auto&v:vs[c])cin>>v;}
 ifstream f(argv[1],ios::binary);vector<int64_t>want(nc*n);f.read((char*)want.data(),want.size()*8);assert(f.gcount()==want.size()*8);
 for(int gi=0;gi<n;gi++){
  bool A[8][8]={};int bit=0;for(int a=0;a<8;a++)for(int b=a+1;b<8;b++)A[a][b]=A[b][a]=(gs[gi]>>bit++)&1;
  vector<int64_t>sum(nc);
  for(int root1=0;root1<8;root1++)for(int root2=0;root2<8;root2++)if(root1!=root2){vector<int>r;for(int a=0;a<8;a++)if(a!=root1&&a!=root2)r.push_back(a);
   for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)for(int k=j+1;k<6;k++){
    array<int,5>v={root1,root2,r[i],r[j],r[k]},w={root1,root2};int wi=2;for(int a=0;a<6;a++)if(a!=i&&a!=j&&a!=k)w[wi++]=r[a];
    auto code=[&](auto&x){int code=0,b=0;for(int a=0;a<5;a++)for(int c=a+1;c<5;c++)code+=int(A[x[a]][x[c]])*(1<<b++);return code;};int a=flag[code(v)],b=flag[code(w)],t=A[root1][root2];
    for(int c=0;c<nc;c++)if(types[c]==t)sum[c]+=vs[c][a]*vs[c][b];
   }
  }
  for(int c=0;c<nc;c++)assert(sum[c]==want[c*n+gi]);
 }
 cout<<"PASS independently recounted "<<nc<<" square inequalities on all "<<n<<" N8 representatives"<<endl;
}
