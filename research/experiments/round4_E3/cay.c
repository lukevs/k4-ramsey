// Exact K4 counts for 0/1 Cayley graphs Cay(G,S) with blue diagonal, plus orbit-flip descent.
// value = (cR + cB)/n^3 where cX = #{(a,b,c) in X^3 : a^-1 b, a^-1 c, b^-1 c in X}, X in {S, T=G\S (contains e)}.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint64_t W;
static int n, words, m; static int *mul, *inv, *orb, *orbstart, *orbel;
static W *R, *B; // adjacency rows
static uint8_t *S;
static uint64_t rs=88172645463325252ULL;
static inline uint64_t rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
#define BIT(A,r,c) ((A[(r)*words+((c)>>6)]>>((c)&63))&1)
#define TOG(A,r,c) (A[(r)*words+((c)>>6)]^=(W)1<<((c)&63))
void cay_init(int n_, const int* mul_, const int* inv_, int m_, const int* orb_){
  n=n_; words=(n+63)/64; m=m_;
  mul=malloc(sizeof(int)*n*n); memcpy(mul,mul_,sizeof(int)*n*n);
  inv=malloc(sizeof(int)*n); memcpy(inv,inv_,sizeof(int)*n);
  orb=malloc(sizeof(int)*n); memcpy(orb,orb_,sizeof(int)*n);
  R=calloc(n*words,8); B=calloc(n*words,8); S=calloc(n,1);
  orbstart=calloc(m+1,sizeof(int)); orbel=malloc(sizeof(int)*n);
  for(int g=0;g<n;g++) if(orb[g]>=0) orbstart[orb[g]+1]++;
  for(int k=0;k<m;k++) orbstart[k+1]+=orbstart[k];
  int *fill=calloc(m,sizeof(int));
  for(int g=0;g<n;g++) if(orb[g]>=0){ int k=orb[g]; orbel[orbstart[k]+fill[k]++]=g; }
  free(fill);
}
static int64_t count(const W* A, int e){
  // C = row e
  const W* C=A+e*words; int64_t tot=0; W X[64];
  for(int a=0;a<n;a++) if(BIT(C,0,a)){
    const W* Ra=A+a*words; for(int w=0;w<words;w++) X[w]=C[w]&Ra[w];
    for(int w=0;w<words;w++){ W bits=X[w]; while(bits){ int b=64*w+__builtin_ctzll(bits); bits&=bits-1;
      const W* Rb=A+b*words; for(int u=0;u<words;u++) tot+=__builtin_popcountll(X[u]&Rb[u]); } }
  }
  return tot;
}
static int E; // identity index
static void load(const uint8_t* bits){ // bits per orbit
  memset(R,0,8*n*words); memset(B,0,8*n*words);
  for(int g=0;g<n;g++) S[g]= orb[g]>=0 ? bits[orb[g]] : 0;
  for(int g=0;g<n;g++) for(int s=0;s<n;s++){ int h=mul[g*n+s]; if(S[s]) TOG(R,g,h); else TOG(B,g,h); }
}
static void flip(int k){
  for(int i=orbstart[k];i<orbstart[k+1];i++){ int s=orbel[i]; S[s]^=1;
    for(int g=0;g<n;g++){ int h=mul[g*n+s]; TOG(R,g,h); TOG(B,g,h);} }
}
static int64_t total(){ return count(R,E)+count(B,E); }
int64_t cay_eval(int e, const uint8_t* bits, int64_t* out){
  E=e; load(bits); out[0]=count(R,E); out[1]=count(B,E); return out[0]+out[1];
}
// first-improvement descent from bits (modified in place). returns final total; *evals counts evaluations.
int64_t cay_descend(int e, uint8_t* bits, uint64_t seed, int64_t* evals){
  E=e; rs=seed*2654435761ULL+1234567; load(bits); int64_t cur=total(); int64_t ev=1;
  int *perm=malloc(sizeof(int)*m); for(int k=0;k<m;k++) perm[k]=k;
  int improved=1;
  while(improved){ improved=0;
    for(int k=m-1;k>0;k--){ int j=rnd()%(k+1); int t=perm[k]; perm[k]=perm[j]; perm[j]=t; }
    for(int i=0;i<m;i++){ int k=perm[i]; flip(k); int64_t v=total(); ev++;
      if(v<cur){ cur=v; bits[k]^=1; improved=1; } else flip(k); }
  }
  free(perm); *evals=ev; return cur;
}
// tabu: best non-tabu single flip each step (aspiration if beats best). bits <- best found.
int64_t cay_tabu(int e, uint8_t* bits, uint64_t seed, int steps, int tenure, int64_t* evals){
  E=e; rs=seed*6364136223846793005ULL+1442695040888963407ULL; load(bits); int64_t cur=total(), best=cur; int64_t ev=1;
  uint8_t* cb=malloc(m); memcpy(cb,bits,m); int* until=calloc(m,sizeof(int));
  for(int st=1;st<=steps;st++){
    int64_t bv=INT64_MAX; int bk=-1; int ties=0;
    for(int k=0;k<m;k++){ flip(k); int64_t v=total(); ev++; flip(k);
      if(until[k]>st && v>=best) continue;
      if(v<bv){bv=v;bk=k;ties=1;} else if(v==bv){ ties++; if(rnd()%ties==0) bk=k; } }
    if(bk<0) break;
    flip(bk); cb[bk]^=1; cur=bv; until[bk]=st+tenure+(int)(rnd()%(tenure+1));
    if(cur<best){best=cur; memcpy(bits,cb,m);}
  }
  free(cb); free(until); *evals=ev; return best;
}
