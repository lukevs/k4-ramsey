#define main search_main
#include "unrestricted.cpp"
#undef main
int main(){alarm(175);mt19937 rng(1901);int checks=0;for(int size=1;size<=7;size++){n=size;L=1;R.assign(n,vector<U>(1));for(int a=0;a<n;a++)for(int b=0;b<=a;b++)if(rng()%2)flip(a,b);auto oracle=[](){I v=0;for(int a=0;a<n;a++)for(int b=0;b<n;b++)for(int c=0;c<n;c++)for(int d=0;d<n;d++)v+=mono({a,b,c,d});return v;};I cur=oracle();if(cur!=full())return 2;for(int t=0;t<100;t++){int a=rng()%n,b=rng()%n;I d=delta(a,b);flip(a,b);I q=oracle();if(q!=cur+d||q!=full())return 3;cur=q;checks++;}}cout<<"Literal ordered oracle/delta/full tests passed "<<checks<<endl;}
