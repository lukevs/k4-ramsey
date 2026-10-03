#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <numeric>
#include <unistd.h>
using namespace std;
int main(){alarm(175);int n;cin>>n;assert(n==1044);int pos[7][7],k=0;for(int i=0;i<7;i++)for(int j=i+1;j<7;j++)pos[i][j]=pos[j][i]=k++;
for(int g=0;g<n;g++){int code;cin>>code;int X[4],J[4][4];for(int&i:X)cin>>i;for(auto&r:J)for(int&i:r)cin>>i;int xc[4]={},jc[4][4]={};array<int,7>v;iota(v.begin(),v.end(),0);
do{int a=0,b=0;for(int i=0;i<3;i++)for(int j=i+1;j<3;j++){a+=(code>>pos[v[i]][v[j]])&1;b+=(code>>pos[v[i+3]][v[j+3]])&1;}xc[a]++;jc[a][b]++;}while(next_permutation(v.begin(),v.end()));
for(int i=0;i<4;i++){assert(X[i]==xc[i]);for(int j=0;j<4;j++)assert(J[i][j]==jc[i][j]);}}
cout<<"PASS 1044 graphs, all 4 marginals and 16 joint entries via 5040 permutations per graph\n";
}
