# Control: literal density of PPSS 768 template (blue diagonal convention).
import json, numpy as np
d=json.load(open('../../data/published_cayley_768.json'))
R=np.array([[c=='1' for c in r] for r in d['red_rows']],dtype=np.int64); n=len(R)
B=1-R; np.fill_diagonal(B,1)
def hom2(M):
    tot=0
    Mf=M.astype(np.float64)
    for a in range(n):
        Na=np.nonzero(M[a])[0]
        S=M[np.ix_(Na,Na)]  # induced on neighbours of a (with loops if a in Na)
        # count hom of K3 in S with a weight: sum_{b,c,d in Na} S_bc S_bd S_cd
        Sf=S.astype(np.float64); tot+=int(round(np.trace(Sf@Sf@Sf)))
    return tot
r=hom2(R); b=hom2(B)
print(r,b,r+b, r+b==10487165184, (r+b)/n**4)
