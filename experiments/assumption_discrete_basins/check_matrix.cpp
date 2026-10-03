// Independent sorted-distinct-clique census plus equality partitions.
#include <vector>
#include <iostream>
#include <string>
#include <cstdint>
#include <unistd.h>
using namespace std;using U=uint64_t;
int main(){alarm(175);int n;cin>>n;int L=(n+63)/64;vector<string> r(n);for(auto&s:r)cin>>s;U total=0;for(int col=0;col<2;col++){vector<vector<U>> hi(n,vector<U>(L));vector<int>loop(n);U singles=0,pairs=0,tri=0,k4=0;for(int a=0;a<n;a++){loop[a]=(r[a][a]-'0'==col);singles+=loop[a];for(int b=a+1;b<n;b++)if(r[a][b]-'0'==col)hi[a][b/64]|=U(1)<<(b%64);}for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(r[a][b]-'0'==col){pairs+=4*(loop[a]+loop[b])+6*loop[a]*loop[b];vector<U>common(L);for(int l=0;l<L;l++)common[l]=hi[a][l]&hi[b][l];for(int l=0;l<L;l++){U z=common[l];while(z){int c=64*l+__builtin_ctzll(z);z&=z-1;tri+=12*(loop[a]+loop[b]+loop[c]);for(int k=0;k<L;k++)k4+=__builtin_popcountll(common[k]&hi[c][k]);}}}U subtotal=singles+pairs+tri+24*k4;cout<<col<<" "<<singles<<" "<<pairs<<" "<<tri<<" "<<k4<<" "<<subtotal<<"\n";total+=subtotal;}cout<<"TOTAL "<<total<<"\n";}
