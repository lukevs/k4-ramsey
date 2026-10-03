#include <iostream>
#include <iomanip>
#include <vector>
int main(){
 int n;if(!(std::cin>>n))return 1;
 std::vector<std::vector<double>> p(n,std::vector<double>(n));for(auto&r:p)for(auto&v:r)std::cin>>v;
 std::vector<double> r(n),b(n);
 std::cout<<std::setprecision(17);
 for(int i=0;i<n;i++)for(int j=0;j<=i;j++){
  for(int k=0;k<n;k++){r[k]=p[i][k]*p[j][k];b[k]=(1-p[i][k])*(1-p[j][k]);}
  double sr=0,sb=0;
  for(int k=0;k<n;k++){
   sr+=r[k]*r[k]*p[k][k];sb+=b[k]*b[k]*(1-p[k][k]);
   for(int l=0;l<k;l++){sr+=2*r[k]*r[l]*p[k][l];sb+=2*b[k]*b[l]*(1-p[k][l]);}
  }
  std::cout<<i<<" "<<j<<" "<<(i==j?6:12)*(sr-sb)<<"\n";
 }
}
