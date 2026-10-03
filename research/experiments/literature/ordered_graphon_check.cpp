// Independent direct ordered-index count: no multiplicity partitions or classes.
#include <iostream>
#include <vector>
#include <algorithm>
using I=__int128_t;using L=long long;
void print(I x){if(!x){std::cout<<0;return;}std::string s;while(x){s+=char('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());std::cout<<s;}
int main(){
 int n;L den;if(!(std::cin>>n>>den))return 1;
 std::vector<std::vector<L>> p(n,std::vector<L>(n));for(auto&r:p)for(auto&v:r)std::cin>>v;
 I answer=0;std::vector<L> a(n);
 for(int color=0;color<2;color++){
  I total=0;
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   L edge=p[i][j];if(!edge)continue;
   for(int k=0;k<n;k++)a[k]=p[i][k]*p[j][k];
   I sum=0;
   for(int k=0;k<n;k++)if(a[k])for(int l=0;l<n;l++)sum+=(I)a[k]*a[l]*p[k][l];
   total+=edge*sum;
  }
  print(total);std::cout<<"\n";answer+=total;
  for(auto&r:p)for(auto&v:r)v=den-v;
 }
 print(answer);std::cout<<"\n";
}
