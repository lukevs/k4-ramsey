// Independent enumeration of all labelled seven-vertex graphs and root orders.
// Input contains graph representatives, integer PSD matrices and rooted flag
// lookup tables; it contains no solver-generated product coefficients.
#include <algorithm>
#include <array>
#include <cassert>
#include <iostream>
#include <fstream>
#include <numeric>
#include <vector>
using namespace std;
using I = __int128_t;
void printI(I x) { if(x<0){cout<<'-';x=-x;} if(x>=10)printI(x/10);cout<<char('0'+x%10); }
struct Block {int r,s,t,d; vector<int> flags; vector<long long> q;};
int pos[7][7];
int sub(int bits,const vector<int>& v) {
    int a=0,b=0;
    for(int i=0;i<(int)v.size();++i)for(int j=i+1;j<(int)v.size();++j,++b)
        a|=((bits>>pos[v[i]][v[j]])&1)<<b;
    return a;
}
int main(int argc, char** argv){
    int nb,ng; long long den; cin>>nb>>ng>>den;
    assert(ng==1044 && nb>0 && nb<100 && den>0);
    int e=0;for(int i=0;i<7;++i)for(int j=i+1;j<7;++j)pos[i][j]=pos[j][i]=e++;
    vector<int> graphs(ng);for(int& g:graphs)cin>>g;
    vector<Block> bs(nb);
    for(auto& b:bs){
        cin>>b.r>>b.s>>b.t>>b.d;
        assert(b.r>0 && b.s>b.r && 2*b.s-b.r<=7);
        b.flags.resize(1<<(b.s*(b.s-1)/2));for(int& f:b.flags)cin>>f;
        b.q.resize(b.d*b.d);for(auto& q:b.q)cin>>q;
    }
    assert(cin.good());
    vector<I> score(1<<21,0);
    for(auto& b:bs){
        vector<int> roots(b.r),left(b.s),right;
        iota(roots.begin(),roots.end(),0);iota(left.begin(),left.end(),0);
        right=roots;for(int j=0;j<b.s-b.r;++j)right.push_back(b.s+j);
        for(int mask=0;mask<(1<<21);++mask){
            if(sub(mask,roots)!=b.t)continue;
            int a=b.flags[sub(mask,left)],c=b.flags[sub(mask,right)];
            assert(a>=0 && a<b.d && c>=0 && c<b.d);
            score[mask]+=b.q[a*b.d+c];
        }
    }
    vector<array<int,21>> perms;array<int,7> p; iota(p.begin(),p.end(),0);
    do {array<int,21> m;int z=0;for(int i=0;i<7;++i)for(int j=i+1;j<7;++j)m[z++]=pos[p[i]][p[j]];perms.push_back(m);}
    while(next_permutation(p.begin(),p.end()));
    vector<int> owner(1<<21,-1);
    I lowest=I(1)<<120;
    for(int g=0;g<ng;++g){
        I penalty=0;
        for(auto& m:perms){
            int bits=0;for(int j=0;j<21;++j)bits|=((graphs[g]>>m[j])&1)<<j;
            assert(owner[bits]==-1 || owner[bits]==g);owner[bits]=g;penalty+=score[bits];
        }
        int mono=0;
        for(int a=0;a<7;++a)for(int b=a+1;b<7;++b)for(int c=b+1;c<7;++c)for(int d=c+1;d<7;++d){
            int v=sub(graphs[g],{a,b,c,d});mono+=(v==0 || v==63);
        }
        I numerator=I(mono)*144*den-penalty;
        lowest=min(lowest,numerator);
        printI(numerator);cout<<'\n';
    }
    assert(all_of(owner.begin(),owner.end(),[](int x){return x>=0;}));
    if(argc==2){
        // Optional diagnostic export; original exact verification above is unchanged.
        vector<int> sizes(ng,0);for(int g:owner)++sizes[g];
        vector<double> table(ng*(nb+2),0.0);
        for(int bi=0;bi<nb;++bi){
            auto& b=bs[bi];vector<int> roots(b.r),left(b.s),right;
            iota(roots.begin(),roots.end(),0);iota(left.begin(),left.end(),0);
            right=roots;for(int j=0;j<b.s-b.r;++j)right.push_back(b.s+j);
            vector<I> totals(ng,0);
            for(int mask=0;mask<(1<<21);++mask){
                if(sub(mask,roots)!=b.t)continue;
                int a=b.flags[sub(mask,left)],c=b.flags[sub(mask,right)];
                totals[owner[mask]]+=b.q[a*b.d+c];
            }
            for(int g=0;g<ng;++g)table[g*(nb+2)+bi]=double(totals[g])/sizes[g]/den;
        }
        double bound=double(lowest)/5040/den;
        for(int g=0;g<ng;++g){
            int mono=0;
            for(int a=0;a<7;++a)for(int b=a+1;b<7;++b)for(int c=b+1;c<7;++c)for(int d=c+1;d<7;++d){int v=sub(graphs[g],{a,b,c,d});mono+=(v==0||v==63);}
            double obj=mono/35.0,penalty=0;for(int b=0;b<nb;++b)penalty+=table[g*(nb+2)+b];
            table[g*(nb+2)+nb]=obj-bound-penalty;
            table[g*(nb+2)+nb+1]=obj;
            assert(table[g*(nb+2)+nb]>-1e-12);
        }
        ofstream f(argv[1],ios::binary);f.write((char*)&nb,4);f.write((char*)&ng,4);f.write((char*)&bound,8);
        f.write((char*)owner.data(),owner.size()*4);f.write((char*)table.data(),table.size()*8);assert(f.good());
    }
    cerr<<"PASS: 2097152 labelled graphs, 1044 disjoint orbits, 5040 orders each\n";
}
