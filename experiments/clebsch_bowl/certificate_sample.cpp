// Sample independent graphon vertices (repeats allowed) and independent edges.
// Report batch uncertainty; these estimates are not construction certificates.
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace std;
uint64_t state;
uint64_t rnd(){uint64_t z=(state+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
int uniform(int n){uint64_t bound=uint64_t(-uint64_t(n))%n,x;do{x=rnd();}while(x<bound);return x%n;}
double unit(){return (rnd()>>11)*0x1.0p-53;}
int main(int argc,char**argv){
    assert(argc==6 || argc==7);ifstream f(argv[1],ios::binary);int nb,ng;double L;
    f.read((char*)&nb,4);f.read((char*)&ng,4);f.read((char*)&L,8);
    vector<int> owner(1<<21);vector<double> tab(ng*(nb+2));f.read((char*)owner.data(),owner.size()*4);f.read((char*)tab.data(),tab.size()*8);assert(f.good());
    ifstream wfile(argv[2],ios::binary);int n;wfile.read((char*)&n,4);vector<double> W(n*n);wfile.read((char*)W.data(),W.size()*8);assert(wfile.good());
    long long N=stoll(argv[3]);state=stoull(argv[4]);int target=argc==7?stoi(argv[6]):-1;
    assert(target<nb+1);const int batches=40;assert(N%batches==0);
    int dim=nb+2+(target>=0?12:0);vector<double> mean(dim,0),ss(dim,0);
    vector<double> batch_means(batches*dim);
    for(int batch=0;batch<batches;++batch){
        vector<double> sums(dim,0);
        for(long long z=0;z<N/batches;++z){
            array<int,7> v;for(int& a:v)a=uniform(n);
            int mask=0,e=0;array<int,21> cats;
            for(int i=0;i<7;++i)for(int j=i+1;j<7;++j,++e){
                double p=W[v[i]*n+v[j]];if(unit()<p)mask|=1<<e;
                if(target>=0){
                    assert(n==192);int a=v[i]/16,b=v[j]/16,x=(v[i]%16)^(v[j]%16);
                    int ac=a/4,bc=b/4,ae=(a/2)%2,be=(b/2)%2,as=a%2,bs=b%2;
                    int type=as==bs?(ac==bc?(ae==be?0:3):(ae==be?1:0)):(ac==bc?2:0);
                    int cat=x==0?0:((x==1||x==2||x==4||x==8||x==15)?1:2);cats[e]=type*3+cat;
                }
            }
            const double* row=&tab[owner[mask]*(nb+2)];for(int k=0;k<nb+2;++k)sums[k]+=row[k];
            if(target>=0)for(int e=0;e<21;++e){
                double diff=tab[owner[mask|(1<<e)]*(nb+2)+target]-tab[owner[mask&~(1<<e)]*(nb+2)+target];
                sums[nb+2+cats[e]]+=diff;
            }
        }
        for(int k=0;k<dim;++k){double x=sums[k]/(N/batches);batch_means[batch*dim+k]=x;mean[k]+=x/batches;ss[k]+=x*x;}
    }
    ofstream out(argv[5]);out<<setprecision(17)<<"{\"samples\":"<<N<<",\"batches\":"<<batches<<",\"lower_bound\":"<<L<<",\"mean\":[";
    for(int k=0;k<dim;++k)out<<(k?",":"")<<mean[k];out<<"],\"standard_error\":[";
    for(int k=0;k<dim;++k)out<<(k?",":"")<<sqrt(max(0.0,ss[k]-batches*mean[k]*mean[k])/(batches-1)/batches);
    out<<"],\"batch_means\":[";for(int b=0;b<batches;++b){out<<(b?",":"")<<"[";for(int k=0;k<dim;++k)out<<(k?",":"")<<batch_means[b*dim+k];out<<"]";}out<<"]}\n";
}
