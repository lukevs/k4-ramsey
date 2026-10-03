#include <iostream>
#include <vector>
#include <cstdint>
using I=std::int64_t;
int main(){
 int n; if(!(std::cin>>n)) return 1;
 std::vector<std::vector<I>> a(n,std::vector<I>(n));
 for(auto &r:a) for(auto &v:r) std::cin>>v;
 I total=0;
 for(int color=0;color<2;color++){
  auto p=a; if(color)for(auto&r:p)for(auto&v:r)v=4-v;
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
  std::cout<<result<<"\n";total+=result;
 }
 std::cout<<total<<"\n";
}
