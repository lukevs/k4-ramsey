// Exact unit-weight, blue-diagonal K4 blow-up search primitives.
// The independent certificate check is implemented in Lean, not in this file.
#include <algorithm>
#include <cstdint>
#include <vector>

using Word = uint64_t;
using Count = int64_t;
struct Graph {
    int n, words;
    std::vector<Word> red, blue;
    std::vector<Count> cached;
    explicit Graph(int order, const uint8_t* matrix)
        : n(order), words((n+63)/64), red(n*words), blue(n*words) {
        for (int i=0; i<n; ++i) for (int j=0; j<n; ++j) if (i!=j)
            (matrix[i*n+j] ? red : blue)[i*words+j/64] |= Word(1)<<(j%64);
    }
    bool edge(int i,int j) const { return (red[i*words+j/64]>>(j%64))&1; }
    void flip(int i,int j) {
        if(!cached.empty()) update_cache(i,j);
        for (auto* rows : {&red,&blue}) {
            (*rows)[i*words+j/64] ^= Word(1)<<(j%64);
            (*rows)[j*words+i/64] ^= Word(1)<<(i%64);
        }
    }
    Count induced(const std::vector<Word>& rows, const Word* set) const {
        Count twice=0;
        for (int a=0;a<words;++a) {
            Word bits=set[a];
            while(bits) {
                int v=64*a+__builtin_ctzll(bits); bits&=bits-1;
                for(int b=0;b<words;++b)
                    twice+=__builtin_popcountll(rows[v*words+b]&set[b]);
            }
        }
        return twice/2;
    }
    Count delta(int u,int v) const {
        Word cr[16]={}, cb[16]={}; Count common=0;
        for(int a=0;a<words;++a) {
            cr[a]=red[u*words+a]&red[v*words+a];
            cb[a]=blue[u*words+a]&blue[v*words+a];
            common+=__builtin_popcountll(cb[a]);
        }
        Count add=-14-36*common-24*induced(blue,cb)+24*induced(red,cr);
        return edge(u,v) ? -add : add;
    }
    void enable_cache() {
        if(!cached.empty()) return;
        cached.assign(n*n,0);
        for(int u=0;u<n;++u) for(int v=u+1;v<n;++v)
            cached[u*n+v]=cached[v*n+u]=delta(u,v);
    }
    void add_cached(int u,int v,Count change) {
        cached[u*n+v]+=change;
        cached[v*n+u]+=change;
    }
    // Mixed finite differences, computed entirely BEFORE changing adjacency.
    // Disjoint pairs affect one K4; incident pairs affect triangles and K4s.
    void update_cache(int u,int v) {
        Word cr[16]={}, cb[16]={};
        for(int a=0;a<words;++a) {
            cr[a]=red[u*words+a]&red[v*words+a];
            cb[a]=blue[u*words+a]&blue[v*words+a];
        }
        const bool old=edge(u,v);
        std::vector<int> common(n,-1);
        for(int x=0;x<n;++x) if(x!=u && x!=v) {
            if((cr[x/64]>>(x%64))&1) common[x]=1;
            if((cb[x/64]>>(x%64))&1) common[x]=0;
            for(int center : {u,v}) {
                int other=center==u ? v : u;
                bool color=edge(other,x);
                const auto& rows=color ? red : blue;
                const Word* pair=color ? cr : cb;
                Count triples=0;
                for(int a=0;a<words;++a)
                    triples+=__builtin_popcountll(pair[a]&rows[x*words+a]);
                Count magnitude=24*triples+(color ? 0 : 36);
                add_cached(center,x,old==edge(center,x) ? magnitude : -magnitude);
            }
        }
        for(int x=0;x<n;++x) if(common[x]>=0)
            for(int y=x+1;y<n;++y) if(common[x]==common[y])
                add_cached(x,y,old==edge(x,y) ? 24 : -24);
        cached[u*n+v]=cached[v*n+u]=-cached[u*n+v];
    }
    Count cliques4(const std::vector<Word>& rows) const {
        Count total=0;
        for(int i=0;i<n;++i) for(int j=i+1;j<n;++j)
            if((rows[i*words+j/64]>>(j%64))&1) {
                Word set[16]={};
                for(int a=j/64;a<words;++a) set[a]=rows[i*words+a]&rows[j*words+a];
                set[j/64] &= j%64==63 ? 0 : (~Word(0) << (j%64+1));
                total+=induced(rows,set);
            }
        return total;
    }
    void counts(Count* out) const {
        Count edges=0,tri=0;
        for(auto word:red) edges+=__builtin_popcountll(word);
        edges/=2;
        for(int i=0;i<n;++i) for(int j=i+1;j<n;++j)
            if(!edge(i,j)) for(int a=0;a<words;++a)
                tri+=__builtin_popcountll(blue[i*words+a]&blue[j*words+a]);
        tri/=3;
        out[0]=edges; out[1]=tri;
        out[2]=cliques4(red); out[3]=cliques4(blue);
        out[4]=n+14*(Count(n)*(n-1)/2-edges)+36*tri+24*(out[2]+out[3]);
    }
};
extern "C" {
void* k4_new(int n,const uint8_t* matrix) {
    if(n<1 || n>1024) return nullptr;
    try { return new Graph(n,matrix); } catch(...) { return nullptr; }
}
void k4_free(void* p) { delete static_cast<Graph*>(p); }
void k4_flip(void* p,int u,int v) { static_cast<Graph*>(p)->flip(u,v); }
Count k4_delta(void* p,int u,int v) { return static_cast<Graph*>(p)->delta(u,v); }
void k4_counts(void* p,Count* out) { static_cast<Graph*>(p)->counts(out); }
void k4_deltas(void* p,const int* us,const int* vs,int size,Count* out) {
    auto& g=*static_cast<Graph*>(p);
    for(int k=0;k<size;++k) out[k]=g.delta(us[k],vs[k]);
}
void k4_export(void* p,uint8_t* out) {
    auto& g=*static_cast<Graph*>(p);
    for(int i=0;i<g.n;++i) for(int j=0;j<g.n;++j) out[i*g.n+j]=g.edge(i,j);
}
int k4_enable_cache(void* p) {
    try { static_cast<Graph*>(p)->enable_cache(); return 1; }
    catch(...) { static_cast<Graph*>(p)->cached.clear(); return 0; }
}
Count k4_cached_delta(void* p,int u,int v) {
    auto& g=*static_cast<Graph*>(p);
    return g.cached[u*g.n+v];
}
void k4_cached_deltas(void* p,const int* us,const int* vs,int size,Count* out) {
    auto& g=*static_cast<Graph*>(p);
    for(int k=0;k<size;++k) out[k]=g.cached[us[k]*g.n+vs[k]];
}
void k4_best_cached(void* p,Count* out) {
    auto& g=*static_cast<Graph*>(p);
    out[0]=-1; out[1]=-1; out[2]=0;
    for(int u=0;u<g.n;++u) for(int v=u+1;v<g.n;++v)
        if(out[0]<0 || g.cached[u*g.n+v]<out[2]) {
            out[0]=u; out[1]=v; out[2]=g.cached[u*g.n+v];
        }
}
void k4_best_cached_allowed(void* p,const int* expiry,int step,Count aspiration,Count* out) {
    auto& g=*static_cast<Graph*>(p);
    out[0]=-1; out[1]=-1; out[2]=0;
    for(int u=0;u<g.n;++u) for(int v=u+1;v<g.n;++v) {
        Count value=g.cached[u*g.n+v];
        if((expiry[u*g.n+v]<=step || value<aspiration) && (out[0]<0 || value<out[2])) {
            out[0]=u; out[1]=v; out[2]=value;
        }
    }
}
void k4_best_cached_star(void* p,int per_color,Count* out) {
    auto& g=*static_cast<Graph*>(p);
    out[0]=out[1]=out[2]=-1; out[3]=0;
    std::vector<std::pair<Count,int>> chosen[2];
    for(int u=0;u<g.n;++u) {
        chosen[0].clear(); chosen[1].clear();
        for(int v=0;v<g.n;++v) if(u!=v)
            chosen[g.edge(u,v)].push_back({g.cached[u*g.n+v],v});
        for(auto& choices:chosen) {
            int size=std::min(per_color,static_cast<int>(choices.size()));
            std::partial_sort(choices.begin(),choices.begin()+size,choices.end());
            choices.resize(size);
        }
        for(const auto& first:chosen[0]) for(const auto& second:chosen[1]) {
            int v=first.second,w=second.second;
            bool color=g.edge(v,w);
            const auto& rows=color ? g.red : g.blue;
            Count triples=0;
            for(int a=0;a<g.words;++a)
                triples+=__builtin_popcountll(rows[u*g.words+a]&rows[v*g.words+a]&rows[w*g.words+a]);
            Count value=first.first+second.first-24*triples-(color ? 0 : 36);
            if(value<out[3]) {
                out[0]=u; out[1]=v; out[2]=w; out[3]=value;
            }
        }
    }
}
}
