import json, numpy as np
def load(path='reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json'):
    d=json.load(open(path))
    Q=d['edge_probability_denominator']; N=np.array(d['red_probability_numerators'],dtype=np.int64)
    w=np.array(d['block_weights'],dtype=float); return N,Q,w/w.sum()
if __name__=='__main__':
    N,Q,w=load(); P=N/Q
    frac=(N>0)&(N<Q)
    print(N.shape, 'sym',(N==N.T).all(),'frac entries',frac.sum(),'per row',np.unique(frac.sum(1)))
    print('rowsums unique',np.unique(N.sum(1))[:10], len(np.unique(N.sum(1))))
    print('distinct values',len(np.unique(N)))
    print('diag',np.unique(np.diag(N)))
