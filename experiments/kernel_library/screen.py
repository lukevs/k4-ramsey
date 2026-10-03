"""Exact finite-group kernel library screen over frozen coarse motif factors."""

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from itertools import permutations, product
from math import gcd
import hashlib
import json
from pathlib import Path
import shutil
import time

from experiments.association_scheme.phase_optimize import PhaseModel, MOTIFS


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-phase-001"
OUT = ROOT / "reports/kernel-library-001"
DEADLINE_SECONDS = 240
MAX_SWEEPS = 6
EDGES = ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class KernelSpec:
    name: str
    elements: tuple
    identity: object
    mul: object
    inv: object
    value: object
    provenance: str

    @property
    def order(self): return len(self.elements)

    def entry(self, a, b, phase):
        # K_phase(a,b)=f(a^-1 phase b); inverse phase on reverse orientation
        # makes the opposite block the exact transpose when f(g)=f(g^-1).
        return self.value(self.mul(self.mul(self.inv(a),phase),b))

    def diagnostics(self):
        row=[self.entry(self.identity,b,self.identity) for b in self.elements]
        nonzero=[abs(x) for x in row if x]
        return dict(row=row,row_sum=sum(row),minimum=min(row),maximum=max(row),
                    squared_l2=sum(x*x for x in row),primitive_gcd=reduce(gcd,nonzero))


def cyclic(name,row,provenance):
    r=len(row);elements=tuple(range(r))
    return KernelSpec(name,elements,0,lambda a,b:(a+b)%r,lambda a:(-a)%r,
                      lambda a:row[a%r],provenance)


def permutation_mul(p,q): return tuple(p[q[i]] for i in range(3))
def permutation_inv(p):
    answer=[0]*3
    for i,j in enumerate(p):answer[j]=i
    return tuple(answer)
def permutation_sign(p):
    inversions=sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
    return -1 if inversions%2 else 1


def s3(name,standard_weight,sign_weight):
    elements=((0,1,2),)+tuple(p for p in permutations(range(3)) if p!=(0,1,2))
    def value(p):
        standard=sum(p[i]==i for i in range(3))-1
        return standard_weight*standard+sign_weight*permutation_sign(p)
    return KernelSpec(name,elements,(0,1,2),permutation_mul,permutation_inv,value,
        f"S3 class function {standard_weight}*chi_standard + {sign_weight}*chi_sign")


SPECS=(
    cyclic("z4_fourier",(1,0,-1,0),"primitive real two-dimensional Z4 Fourier character"),
    cyclic("z4_mixed",(2,-1,0,-1),"primitive mixture of Z4 frequency-one and sign characters"),
    s3("s3_standard",1,0),
    s3("s3_standard_plus_sign",1,1),
    s3("s3_standard_minus_sign",1,-1),
)


class GenericObjective:
    def __init__(self, frozen_model, spec):
        self.model=frozen_model;self.spec=spec;self.cache={}

    def phase(self,state,sign):
        value=self.spec.elements[state]
        return value if sign>0 else self.spec.inv(value)

    def moment(self,degree,phases):
        key=(degree,phases)
        if key in self.cache:return self.cache[key]
        # Class-function convolution is invariant under simultaneous right
        # multiplication of all four types. Fix type0=e and multiply by |G|.
        answer=0
        for tail in product(self.spec.elements,repeat=3):
            types=(self.spec.identity,*tail);term=1
            for (u,v),phase in zip(MOTIFS[degree],phases):
                term*=self.spec.entry(types[u],types[v],phase)
            answer+=term
        answer*=self.spec.order
        self.cache[key]=answer
        return answer

    def factor_value(self,factor,states):
        degree,signature,weight=factor;phases=[]
        for variable,sign in signature:
            state=states[variable]
            if state<0:return 0
            phases.append(self.phase(state,sign))
        return weight*self.moment(degree,tuple(phases))

    def coefficients(self,states):
        answer={d:0 for d in range(3,7)}
        for factor in self.model.factors:answer[factor[0]]+=self.factor_value(factor,states)
        return answer

    def coordinate_descent(self,states,q,deadline):
        states=list(states);objective=sum(self.factor_value(f,states)*q**f[0] for f in self.model.factors)
        history=[]
        for sweep in range(1,MAX_SWEEPS+1):
            moves=0
            for variable in range(len(states)):
                if time.monotonic()>=deadline:
                    history.append(dict(sweep=sweep,moves=moves,objective=objective,terminated="deadline"))
                    return states,history
                affected=self.model.incident[variable];old=states[variable]
                old_local=sum(self.factor_value(self.model.factors[i],states)*q**self.model.factors[i][0] for i in affected)
                best,best_local=old,old_local
                for trial in (-1,*range(self.spec.order)):
                    if trial==old:continue
                    states[variable]=trial
                    value=sum(self.factor_value(self.model.factors[i],states)*q**self.model.factors[i][0] for i in affected)
                    if value<best_local:best,best_local=trial,value
                states[variable]=best
                if best!=old:objective+=best_local-old_local;moves+=1
            checked=sum(self.factor_value(f,states)*q**f[0] for f in self.model.factors)
            assert checked==objective
            history.append(dict(sweep=sweep,moves=moves,objective=objective,
                                active=sum(x>=0 for x in states)))
            if moves==0:break
        return states,history


def feasible_interval(base,denominator,model,states,spec):
    values={base[i][j] for (i,j),state in zip(model.edge_list,states) if state>=0}
    if not values:return (0,0)
    kernel_values=[spec.value(x) for x in spec.elements]
    valid=[]
    for q in range(-denominator,denominator+1):
        if all(0<=p+q*k<=denominator for p in values for k in kernel_values):valid.append(q)
    return min(valid),max(valid)


def optimize_q(base,denominator,model,states,spec,coefficients,parent_density):
    lo,hi=feasible_interval(base,denominator,model,states,spec)
    delta=lambda q:sum(coefficients[d]*q**d for d in range(3,7))
    q=min(range(lo,hi+1),key=lambda x:(delta(x),x))
    norm=(spec.order*len(base))**4*denominator**6
    return dict(feasible_q=[lo,hi],selected_q=q,selected_delta_raw=delta(q),
                density=str(parent_density+Fraction(delta(q),norm)),normalization=norm)


def materialize(base,denominator,model,states,spec,q):
    r=spec.order;matrix=[]
    for ia in range(r*len(base)):
        i,a=divmod(ia,r);row=[]
        for jb in range(r*len(base)):
            j,b=divmod(jb,r);value=base[i][j]
            if i!=j and 0<value<denominator:
                edge=(i,j) if i<j else (j,i);state=states[model.edge_index[edge]]
                if state>=0:
                    phase=spec.elements[state]
                    if i>j:phase=spec.inv(phase)
                    value+=q*spec.entry(spec.elements[a],spec.elements[b],phase)
            row.append(value)
        matrix.append(row)
    return matrix


def literal_raw(matrix,denominator):
    answer=0
    for vertices in product(range(len(matrix)),repeat=4):
        red=blue=1
        for u,v in EDGES:
            p=matrix[vertices[u]][vertices[v]];red*=p;blue*=denominator-p
        answer+=red+blue
    return answer


def tiny_falsifier(spec):
    results=[]
    for base,denominator in [([[0,4],[4,0]],10),([[0,4,5],[4,0,6],[5,6,0]],10)]:
        model=PhaseModel(base,denominator);objective=GenericObjective(model,spec)
        states=[i%spec.order for i in range(len(model.edge_list))]
        coefficients=objective.coefficients(states);base_raw=literal_raw(base,denominator)
        for q in (-1,1):
            matrix=materialize(base,denominator,model,states,spec,q)
            if not all(0<=x<=denominator for row in matrix for x in row):continue
            predicted=base_raw*spec.order**4+sum(coefficients[d]*q**d for d in range(3,7))
            actual=literal_raw(matrix,denominator);assert actual==predicted
            results.append(dict(base_order=len(base),q=q,predicted=predicted,actual=actual))
    return results


def main():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,OUT/"source_snapshot.py");shutil.copy2(HERE/"preregistration.json",OUT/"preregistration.json")
    parent_bytes=(PARENT/"graphon-candidate.json").read_bytes();parent=json.loads(parent_bytes)
    parent_report=json.loads((PARENT/"report.json").read_text());control=json.loads((CONTROL/"report.json").read_text())
    base=parent["red_probability_numerators"];denominator=parent["edge_probability_denominator"]
    parent_density=Fraction(parent_report["density"]);control_density=Fraction(control["actual_density"])
    model=PhaseModel(base,denominator);assert len(model.edge_list)==1248
    screens=[];tiny={}
    for spec in SPECS:
        diagnostics=spec.diagnostics();assert diagnostics["row_sum"]==0 and diagnostics["primitive_gcd"]==1
        assert all(spec.value(spec.inv(x))==spec.value(x) for x in spec.elements)
        tiny[spec.name]=tiny_falsifier(spec)
        objective=GenericObjective(model,spec);states=[0]*len(model.edge_list)
        coefficients=objective.coefficients(states)
        result=optimize_q(base,denominator,model,states,spec,coefficients,parent_density)
        screens.append(dict(name=spec.name,order=spec.order,provenance=spec.provenance,
                            diagnostics=diagnostics,coefficients=coefficients,**result))
    best_screen=min(screens,key=lambda x:Fraction(x["density"]))
    spec=next(x for x in SPECS if x.name==best_screen["name"]);objective=GenericObjective(model,spec)
    states=[0]*len(model.edge_list);deadline=time.monotonic()+DEADLINE_SECONDS
    states,history=objective.coordinate_descent(states,best_screen["selected_q"],deadline)
    coefficients=objective.coefficients(states)
    optimized=optimize_q(base,denominator,model,states,spec,coefficients,parent_density)
    optimized.update(name=spec.name,order=spec.order,coefficients=coefficients,history=history,
                     active=sum(x>=0 for x in states),phase_histogram={str(s):states.count(s) for s in (-1,*range(spec.order))})
    admit=Fraction(optimized["density"])<control_density
    report=dict(schema="kernel-library-screen-v1",status="candidate_predicted" if admit else "completed_no_admission",
        hypothesis="Centered relation spectra can improve triangle reward relative to higher motif costs",
        parent=str(PARENT.relative_to(ROOT)),parent_candidate_sha256=hashlib.sha256(parent_bytes).hexdigest(),
        control=str(CONTROL.relative_to(ROOT)),control_density=str(control_density),library_screens=screens,
        selected_kernel=best_screen["name"],optimized=optimized,tiny_falsifiers=tiny,
        coefficient_recomputation="U3..U6 and feasibility recomputed independently for every kernel; none transferred",
        representation="uniform equal-mass group types; primitive integer inverse-invariant class functions; reverse phase uses group inverse",
        library_quotient="No pair differs only by integer scaling, global sign (absorbed by q sign), or listed group automorphism",
        scope_limit="Finite-group class-function kernels are translation-invariant and do not cover arbitrary centered symmetric matrices or unequal type masses",
        admitted_to_checker=admit,total_seconds=time.monotonic()-start,source_sha256=sha256(Path(__file__)),
        evidence="Exact sparse degree3..6 motif polynomial with tiny literal ordered-tuple falsifiers; no full candidate recount")
    if admit:
        matrix=materialize(base,denominator,model,states,spec,optimized["selected_q"])
        assert all(0<=x<=denominator for row in matrix for x in row)
        assert all(matrix[i][j]==matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix)))
        write_json(OUT/"phase-assignment.json",{f"{i},{j}":s for (i,j),s in zip(model.edge_list,states)})
        write_json(OUT/"graphon-candidate.json",dict(schema="rational-step-graphon-v1",block_weights=[1]*len(matrix),
            edge_probability_denominator=denominator,red_probability_numerators=matrix))
        report["candidate_sha256"]=sha256(OUT/"graphon-candidate.json")
        report["phase_assignment_sha256"]=sha256(OUT/"phase-assignment.json")
    write_json(OUT/"report.json",report)
    print(json.dumps({"status":report["status"],"screens":[(x["name"],x["density"]) for x in screens],
        "optimized":optimized,"control_density":str(control_density),"candidate_sha256":report.get("candidate_sha256")},indent=2))


if __name__=="__main__":main()
