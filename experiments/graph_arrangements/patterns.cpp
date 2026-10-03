#include <fstream>
#include <vector>
#include <iostream>
int main(int argc,char**argv){std::ifstream f(argv[1]);int n;f>>n;std::vector<int>A(n*n);for(auto &x:A)f>>x;unsigned long long c[729]={};for(int a=0;a<n;a++)for(int b=0;b<n;b++)for(int d=0;d<n;d++)for(int e=0;e<n;e++){int v[4]={a,b,d,e};int code=0,p=1;for(int i=0;i<4;i++)for(int j=i+1;j<4;j++){int r=v[i]==v[j]?2:A[v[i]*n+v[j]];code+=p*r;p*=3;}c[code]++;}for(int k=0;k<729;k++)if(c[k])std::cout<<k<<" "<<c[k]<<"\n";}
