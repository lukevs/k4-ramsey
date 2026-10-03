from pathlib import Path
import struct,json
from fractions import Fraction as F
import numpy as np
BASE=Path('reports/energy-bootstrap-n7-001');OUT=Path('reports/energy-bootstrap-auto-001');D=5040*16777216

def blocks():
 f=open(BASE/'coefficients.bin','rb');nb,ng=struct.unpack('ii',f.read(8));Cs=[]
 for _ in range(nb):
  d=struct.unpack('i',f.read(4))[0];Cs.append(np.fromfile(f,dtype=np.uint16,count=ng*d*d).reshape(ng,d,d))
 x=np.fromfile(f,dtype=np.uint16,count=ng);z=np.fromfile(f,dtype=np.uint16,count=ng);c=np.fromfile(f,dtype=np.uint16,count=ng);P=np.fromfile(f,dtype=np.uint16,count=156*ng).reshape(156,ng);assert not f.read();f.close()
 # Use previously audited exact tensors directly, in reference order.
 ref=json.loads(Path('reports/global-coupled-pilot-003/full-certificate.json').read_text())
 for b in ref['blocks']:Cs.append(np.einsum('ag,aij->gij',P.astype(np.int64),np.array(b['C_integer'],dtype=np.int64)).astype(np.uint16))
 return Cs,c

def inequalities(cfg):
 obs=json.loads((OUT/'observables.json').read_text());X=np.array([r['X'] for r in obs['rows']],dtype=np.int64).T;J=np.array([r['J'] for r in obs['rows']],dtype=np.int64).transpose(1,2,0)
 a,b,c,d=cfg['box'];grid=cfg['grid'];assert grid in (64,128,256,512,1024,2048,4096);S=16777216;U=S//grid;V=S//(grid*grid)
 lo=[0,a,c,0];hi=[grid-a-c,b,d,grid-a-c];rows=[];labels=[]
 def add(v,label):rows.append(v);labels.append(label)
 for i in range(4):
  add(S*X[i]-lo[i]*U*5040,f'lower_{i}');add(hi[i]*U*5040-S*X[i],f'upper_{i}')
  add((lo[i]+hi[i])*U*X[i]-S*J[i,i]-lo[i]*hi[i]*V*5040,f'secant_{i}')
 if cfg['cross']:
  for i in range(4):
   for j in range(i+1,4):
    for a,b in [(lo[i],lo[j]),(hi[i],hi[j])]:add(S*J[i,j]-U*a*X[j]-U*b*X[i]+a*b*V*5040,f'lower_product_{i}_{j}_{a}_{b}')
    for a,b in [(hi[i],lo[j]),(lo[i],hi[j])]:add(U*a*X[j]+U*b*X[i]-S*J[i,j]-a*b*V*5040,f'upper_product_{i}_{j}_{a}_{b}')
 if cfg['ordered']:add(S*(X[2]-X[1]),'colour_order')
 return np.array(rows),labels,X,J
