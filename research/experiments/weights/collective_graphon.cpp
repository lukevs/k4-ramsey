// Direct ordered-index mass derivatives; separate from class-probability search.
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using I=__int128_t; using L=long long;
void print(I x) {if(x<0){std::cout<<'-';x=-x;} if(!x){std::cout<<0;return;} std::string s;while(x){s+=char('0'+x%10);x/=10;}std::reverse(s.begin(),s.end());std::cout<<s;}
int main(){
 int n; L den; if(!(std::cin>>n>>den)||n<1||n>192||den<1||den>4096)return 1;
 std::vector<std::vector<L>> p(n,std::vector<L>(n));
 for(auto&r:p)for(auto&v:r){if(!(std::cin>>v)||v<0||v>den)return 2;}
 for(int i=0;i<n;i++){if(p[i][i]!=0)return 3;for(int j=0;j<n;j++)if(p[i][j]!=p[j][i])return 4;}
 std::vector<I> gradient(n);std::vector<std::vector<I>> h(n,std::vector<I>(n));
 I answer=0;std::vector<L>a(n);
 for(int color=0;color<2;color++){
  for(int i=0;i<n;i++)for(int j=0;j<n;j++){
   L edge=p[i][j];if(!edge)continue;
   for(int k=0;k<n;k++)a[k]=p[i][k]*p[j][k];
   I sum=0;
   for(int k=0;k<n;k++)if(a[k])for(int l=0;l<n;l++)sum+=(I)a[k]*a[l]*p[k][l];
   I term=edge*sum;answer+=term;gradient[i]+=4*term;h[i][j]+=12*term;
  }
  for(auto&r:p)for(auto&v:r)v=den-v;
 }
 print(answer);std::cout<<'\n';
 for(I g:gradient){print(g);std::cout<<' ';}std::cout<<'\n';
 for(auto&r:h){for(I value:r){print(value);std::cout<<' ';}std::cout<<'\n';}
}
