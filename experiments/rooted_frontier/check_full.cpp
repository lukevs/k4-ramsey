// Complete independent coefficient recount; no event-table import.
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <unistd.h>
using namespace std;
struct Block{int n,d,nnz;vector<int>p,i;vector<int16_t>v;Block(string path){ifstream f(path,ios::binary);f.read((char*)&n,4);f.read((char*)&d,4);f.read((char*)&nnz,4);p.resize(n+1);i.resize(nnz);v.resize(nnz);f.read((char*)p.data(),p.size()*4);f.read((char*)i.data(),i.size()*4);f.read((char*)v.data(),v.size()*2);assert(f.good());}};
int main(int argc,char**argv){alarm(175);assert(argc==2);int n;cin>>n;vector<int>gs(n);for(int&g:gs)cin>>g;array<int,1024>flag;for(int&v:flag)cin>>v;
 int plus[2][120],minus[2][120],sign[2][120];for(int t=0;t<2;t++){for(int&v:plus[t])cin>>v;for(int&v:minus[t])cin>>v;for(int&v:sign[t])cin>>v;}
 vector<Block>bs;for(string name:{"root0-plus","root0-minus","root1-plus","root1-minus"})bs.emplace_back(string(argv[1])+"/"+name+"-check.bin");
 for(int gi=0;gi<n;gi++){
  bool A[8][8]={};int bit=0;for(int a=0;a<8;a++)for(int b=a+1;b<8;b++)A[a][b]=A[b][a]=(gs[gi]>>bit++)&1;
  vector<vector<int>>M(4);for(int k=0;k<4;k++)M[k].resize(bs[k].d*bs[k].d);vector<vector<int>>cross(2,vector<int>(74*46));
  for(int a=0;a<8;a++)for(int b=0;b<8;b++)if(a!=b){vector<int>r;for(int c=0;c<8;c++)if(c!=a&&c!=b)r.push_back(c);
   for(int i=0;i<6;i++)for(int j=i+1;j<6;j++)for(int k=j+1;k<6;k++){
    array<int,5>v={a,b,r[i],r[j],r[k]},w={a,b};int wi=2;for(int c=0;c<6;c++)if(c!=i&&c!=j&&c!=k)w[wi++]=r[c];
    auto code=[&](auto&x){int h=0,bit=0;for(int i=0;i<5;i++)for(int j=i+1;j<5;j++)h+=int(A[x[i]][x[j]])*(1<<bit++);return h;};int x=flag[code(v)],y=flag[code(w)],t=A[a][b];
    M[2*t][plus[t][x]*74+plus[t][y]]++;
    if(minus[t][x]>=0&&minus[t][y]>=0)M[2*t+1][minus[t][x]*46+minus[t][y]]+=sign[t][x]*sign[t][y];
    if(minus[t][y]>=0)cross[t][plus[t][x]*46+minus[t][y]]+=sign[t][y];
   }
  }
  for(auto&v:cross)for(int x:v)assert(x==0);
  for(int k=0;k<4;k++){auto&B=bs[k];assert(B.n==n);for(int a=B.p[gi];a<B.p[gi+1];a++){assert(M[k][B.i[a]]==B.v[a]);M[k][B.i[a]]=0;}for(int x:M[k])assert(x==0);}
 }
 cout<<"PASS all four complete blocks and zero cross-parity blocks, all "<<n<<" N8 graphs"<<endl;
}
