#include <iostream>
#include <vector>
int main(){
 int n;if(!(std::cin>>n))return 1;std::vector<std::vector<int>> a(n,std::vector<int>(n));for(auto&r:a)for(auto&v:r)std::cin>>v;
 long long hist[2][7][7]={};int fact[]={1,1,2,6,24};
 for(int i=0;i<n;i++)for(int j=i;j<n;j++)for(int k=j;k<n;k++)for(int l=k;l<n;l++){
  int vertices[]={i,j,k,l},den=1,run=1;
  for(int t=1;t<4;t++){if(vertices[t]==vertices[t-1])run++;else{den*=fact[run];run=1;}}den*=fact[run];int mult=24/den;
  int types[]={a[i][j],a[i][k],a[i][l],a[j][k],a[j][l],a[k][l]};int p=0,h=0;bool red=true,blue=true;
  for(int c:types){if(c==-1)red=false;else if(c==-2)blue=false;else if(c==0)p++;else if(c==1)h++;else return 2;}
  if(red)hist[0][p][h]+=mult;if(blue)hist[1][p][h]+=mult;
 }
 for(int color=0;color<2;color++)for(int p=0;p<=6;p++)for(int h=0;h<=6;h++)if(hist[color][p][h])std::cout<<color<<" "<<p<<" "<<h<<" "<<hist[color][p][h]<<"\n";
}
