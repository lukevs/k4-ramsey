"""Exact signed probability-conditioned polarization gate for candidate b93."""

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).with_name("coefficients.cpp")
CERT=ROOT/"reports/graphon-joint-coarse-boundary-face-compressed-001/full-certificate.txt"
GENERATOR=ROOT/"reports/graphon-joint-coarse-boundary-face-compressed-001/typed_kernel_histogram_generator"
CANDIDATE=ROOT/"reports/joint-coarse-boundary-face-001/graphon-candidate.json"
OUT=ROOT/"reports/signed-polarization-b93-001"


TRIANGLES=((0,1,3),(0,2,4),(1,2,5),(3,4,5))
TRIANGLE_OTHER=((2,4,5),(1,3,5),(0,3,4),(0,1,2))
CYCLES=((1,2,3,4),(0,2,3,5),(0,1,4,5))
CYCLE_OTHER=((0,5),(1,4),(2,3))
ENDS=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))


def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_coefficients(matrix,q):
    a3=a4=0
    for vertices in itertools.product(range(len(matrix)),repeat=4):
        p=[matrix[vertices[i]][vertices[j]] for i,j in ENDS]
        c=[(0 if 2*value==q else (1 if 2*value>q else -1)*value*(q-value)) for value in p]
        for selected,other in zip(TRIANGLES,TRIANGLE_OTHER):
            a3+=c[selected[0]]*c[selected[1]]*c[selected[2]]*(
                p[other[0]]*p[other[1]]*p[other[2]]-
                (q-p[other[0]])*(q-p[other[1]])*(q-p[other[2]]))
        for selected,other in zip(CYCLES,CYCLE_OTHER):
            product=1
            for edge in selected: product*=c[edge]
            a4+=product*(p[other[0]]*p[other[1]]+(q-p[other[0]])*(q-p[other[1]]))
    return a3,a4


def payload(matrix,q):
    return f"{len(matrix)} {q}\n"+"\n".join(" ".join(map(str,row)) for row in matrix)+"\n"


def evaluate(binary,certificate,limit=None):
    command=[str(binary),str(certificate)]
    if limit is not None: command.append(str(limit))
    started=time.monotonic()
    lines=subprocess.check_output(command,text=True,timeout=300).splitlines()
    metadata=list(map(int,lines[2].split()))
    return int(lines[0]),int(lines[1]),metadata,time.monotonic()-started


def main():
    started=time.monotonic()
    OUT.mkdir(parents=True,exist_ok=False)
    binary=OUT/"coefficients"
    subprocess.run(["/usr/bin/clang++","-O3","-std=c++17",str(SOURCE),"-o",str(binary)],check=True)
    shutil.copy2(SOURCE,OUT/"coefficients_snapshot.cpp")
    shutil.copy2(Path(__file__),OUT/"run_snapshot.py")
    tiny=[]
    fixtures=[
        ([[0,1],[1,3]],5,1),
        ([[0,1,4,2],[1,3,2,5],[4,2,1,0],[2,5,0,4]],7,2),
        ([[0,2,5,1,4,3],[2,1,3,6,0,5],[5,3,4,2,1,0],[1,6,2,0,5,4],[4,0,1,5,3,2],[3,5,0,4,2,1]],7,3),
    ]
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory)
        for index,(matrix,q,types) in enumerate(fixtures):
            matrix_path=temp/f"m{index}.txt";cert_path=temp/f"c{index}.txt"
            matrix_path.write_text(payload(matrix,q))
            subprocess.run([str(GENERATOR),str(matrix_path),str(types),str(cert_path)],check=True,capture_output=True,text=True)
            expected=literal_coefficients(matrix,q)
            got3,got4,metadata,seconds=evaluate(binary,cert_path)
            assert (got3,got4)==expected
            complement=[[q-value for value in row] for row in matrix]
            comp_path=temp/f"mc{index}.txt";comp_cert=temp/f"cc{index}.txt"
            comp_path.write_text(payload(complement,q))
            subprocess.run([str(GENERATOR),str(comp_path),str(types),str(comp_cert)],check=True,capture_output=True,text=True)
            comp3,comp4,_,_=evaluate(binary,comp_cert)
            assert (comp3,comp4)==(got3,got4)
            tiny.append({"order":len(matrix),"types":types,"q":q,"a3_numerator":got3,
                         "a4_numerator":got4,"complement_sign_control":True,"seconds":seconds})
    constant=[[2,2],[2,2]];constant3,constant4=literal_coefficients(constant,5)
    c=-2*3
    assert constant3==2**4*4*c**3*(2**3-3**3)
    assert constant4==2**4*3*c**4*(2**2+3**2)

    # Extrapolate from the first1,000 of28,272 histogram signatures.
    _,_,estimate_meta,estimate_seconds=evaluate(binary,CERT,1000)
    estimate=estimate_seconds*estimate_meta[5]/estimate_meta[6]
    if estimate>300:
        raise RuntimeError(f"estimated full coefficient cost {estimate:.1f}s exceeds5min gate")
    a3_num,a4_num,metadata,production_seconds=evaluate(binary,CERT)
    n,q,base,types,kernels,rows,processed,mass=metadata
    assert n==960 and q==65536 and base==192 and types==5 and processed==rows and mass==base**4
    a3=Fraction(a3_num,n**4*q**9);a4=Fraction(a4_num,n**4*q**10)
    a3_absolute_bound=4*n**4*q**9
    a4_bound=6*n**4*q**10
    assert a3_absolute_bound.bit_length()<255 and a4_bound.bit_length()<255
    options=[(Fraction(0),Fraction(0)),(Fraction(-1),-a3+a4),(Fraction(1),a3+a4)]
    stationary=None
    if a4:
        candidate_stationary=-Fraction(3)*a3/(4*a4)
        if candidate_stationary and -1<=candidate_stationary<=1:
            stationary=candidate_stationary
            options.append((stationary,a3*stationary**3+a4*stationary**4))
    epsilon,delta=min(options,key=lambda pair:pair[1])
    child_denominator=epsilon.denominator*q*q
    normalization_bits=(n*2)**4*child_denominator**6
    report={"schema":"signed-polarization-coefficient-gate-v1",
            "status":"exact_coefficients_complete",
            "candidate":str(CANDIDATE.relative_to(ROOT)),"candidate_sha256":sha256(CANDIDATE),
            "certificate":str(CERT.relative_to(ROOT)),"certificate_sha256":sha256(CERT),
            "a3_raw_numerator":a3_num,"a3_raw_denominator":n**4*q**9,"a3":str(a3),"a3_decimal":float(a3),
            "a4_raw_numerator":a4_num,"a4_raw_denominator":n**4*q**10,"a4":str(a4),"a4_decimal":float(a4),
            "optimal_epsilon":str(epsilon),"optimal_epsilon_decimal":float(epsilon),
            "nonzero_stationary_epsilon":None if stationary is None else str(stationary),
            "evaluated_options":[{"epsilon":str(x),"delta":str(y),"delta_decimal":float(y)} for x,y in options],
            "optimal_delta":str(delta),"optimal_delta_decimal":float(delta),
            "predicted_density":str(Fraction(1375401591138773841968807740019,45635421608216258453881315393536)+delta),
            "predicted_density_decimal":float(Fraction(1375401591138773841968807740019,45635421608216258453881315393536)+delta),
            "child_probability_denominator":child_denominator,
            "materialized_order":n*2,"normalization_bits":normalization_bits.bit_length(),
            "u256_safe":normalization_bits.bit_length()<=256,
            "accumulator_bounds":{"a3_absolute_bound":a3_absolute_bound,
                                  "a3_bound_bits":a3_absolute_bound.bit_length(),
                                  "a4_bound":a4_bound,"a4_bound_bits":a4_bound.bit_length(),
                                  "signed_int256_safe":True,
                                  "derivation":"|S3|<=4*N^4*Q^9 and |S4|<=6*N^4*Q^10 using |signed c|<=Q^2, four triangles, three cycles, and red+blue<=2Q^2"},
            "tiny_literal_controls":tiny,"estimate_seconds":estimate,"production_seconds":production_seconds,
            "metadata":{"order":n,"q":q,"base":base,"types":types,"kernels":kernels,"histogram_rows":rows,"coarse_mass":mass},
            "source_sha256":sha256(SOURCE),"seconds":time.monotonic()-started,
            "evidence":"Exact signed-C evaluation from the candidate-bound typed-kernel histogram; three literal tiny controls; no materialized child recount.",
            "scope":"Complete one-step signed-C scalar epsilon line on candidate b93; endpoints and every feasible nonzero stationary point compared without a quartic-sign assumption; no repeated-level or novelty claim."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("a3_decimal","a4_decimal","optimal_epsilon","optimal_delta_decimal","predicted_density_decimal","child_probability_denominator","normalization_bits","u256_safe","estimate_seconds","production_seconds","seconds")},sort_keys=True))


if __name__=="__main__":main()
