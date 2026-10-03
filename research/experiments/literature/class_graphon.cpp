#include <iostream>
#include <vector>
#include <algorithm>
using I=__int128_t;
void print(I x){if(!x){std::cout<<0;return;}std::string s;while(x){s+=char('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());std::cout<<s;}
int main(){
 int n,nc; if(!(std::cin>>n>>nc))return 1;
 std::vector<std::vector<int>> classes(n,std::vector<int>(n));
 for(auto&r:classes)for(auto&v:r)std::cin>>v;
 int denominator;std::vector<int> parameters(nc);
 while(std::cin>>denominator){
 for(auto&v:parameters)std::cin>>v;
 I total=0;
 for(int color=0;color<2;color++){
  std::vector<std::vector<I>> p(n,std::vector<I>(n));
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   int c=classes[i][j];I x=c==-1?0:(c==-2?denominator:parameters[c]);
   p[i][j]=color?denominator-x:x;
  }
  I result=0;
  for(int i=0;i<n;i++){
   I x=p[i][i];result+=x*x*x*x*x*x;
   for(int j=i+1;j<n;j++){
    I y=p[j][j],z=p[i][j];
    result+=4*(x*x*x+y*y*y)*z*z*z+6*x*y*z*z*z*z;
    for(int k=j+1;k<n;k++){
     I w=p[k][k],u=p[i][k],v=p[j][k];
     result+=12*(x*z*z*u*u*v+y*z*z*v*v*u+w*u*u*v*v*z);
     I common=z*u*v;
     if(common)for(int l=k+1;l<n;l++)result+=24*common*p[i][l]*p[j][l]*p[k][l];
    }
   }
  }
  total+=result;
 }
 print(total);std::cout<<std::endl;
 }
}
