#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <unistd.h>
using namespace std;
int main(int argc,char**argv){alarm(175);assert(argc==3);ifstream f(argv[1],ios::binary);int n,d,ne;f.read((char*)&n,4);f.read((char*)&d,4);f.read((char*)&ne,4);f.seekg(8*d,ios::cur);int k;cin>>k;vector<int64_t>v(2*d*k);for(auto&x:v)cin>>x;
 ofstream out(argv[2],ios::binary);out.write((char*)&n,4);out.write((char*)&k,4);
 vector<uint16_t>e(ne*3);vector<int64_t>M(2*k*k);
 for(int g=0;g<n;g++){f.read((char*)e.data(),e.size()*2);fill(M.begin(),M.end(),0);
 for(int a=0;a<ne;a++){int t=e[3*a],i=e[3*a+1],j=e[3*a+2];auto*vi=&v[(t*d+i)*k];auto*vj=&v[(t*d+j)*k];auto*m=&M[t*k*k];for(int b=0;b<k;b++)for(int c=0;c<k;c++)m[b*k+c]+=vi[b]*vj[c];}
 out.write((char*)M.data(),M.size()*8);}
 assert(f.good()&&out.good());cout<<"Projected "<<n<<" graphs to two "<<k<<"x"<<k<<" blocks"<<endl;
}
