from search import *
for name,n in [('cycle5',5),('clebsch16',16)]:
 W=np.array([[float(((i-j)%5 in (1,4)) if n==5 else ((i^j) in (1,2,4,8,15))) for j in range(n)] for i in range(n)]);m=np.ones(n)/n
 base=fg(W,m)[0]
 for variable in (False,True):
  P,w,meta=optimize(W,m,variable,maxiter=300)
  meta.update(n=n,variable=variable,start_kind='known_base_control_not_independent_start',base=name,base_objective=base,initial_W=W.tolist(),initial_m=m.tolist(),pid=os.getpid())
  save('control-'+name+'-'+('variable' if variable else 'equal'),P,w,meta)
