"""Exact checks of the scope of the Clebsch operator argument (stdlib only)."""
from fractions import Fraction as F
import json
import random


def counterexample(a):
    weights = [a, 1-a]
    U = [[F(1), F(0)], [F(0), F(0)]]
    d = [sum(weights[j]*U[i][j] for j in range(2)) for i in range(2)]
    p = sum(weights[i]*d[i] for i in range(2))
    D = [[U[i][j]-d[i]-d[j]+p for j in range(2)] for i in range(2)]
    f = [1-a, -a]
    eigenvalue = a*(1-a)
    assert sum(weights[i]*f[i] for i in range(2)) == 0
    for i in range(2):
        assert sum(weights[j]*D[i][j] for j in range(2)) == 0
        assert sum(weights[j]*D[i][j]*f[j] for j in range(2)) == eigenvalue*f[i]
    assert eigenvalue > min(p, 1-p)
    return {"clique_mass": str(a), "edge_density": str(p),
            "centered_operator_norm": str(eigenvalue),
            "ratio_to_invalid_mean_bound": str(eigenvalue/min(p, 1-p)),
            "centered_matrix": [[str(x) for x in row] for row in D]}


def weighted_cs_checks():
    rng = random.Random(29092026)
    cases = 0
    for n in range(1, 7):
        for _ in range(20):
            masses = [rng.randrange(1, 9) for _ in range(n)]
            w = [F(x, sum(masses)) for x in masses]
            U = [[F(0) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    U[i][j] = U[j][i] = F(rng.randrange(8), 7)
            f = [F(rng.randrange(-9, 10), 5) for _ in range(n)]
            for i in range(n):
                degree = sum(w[j]*U[i][j] for j in range(n))
                lhs = degree*sum(w[j]*U[i][j]*f[j]**2 for j in range(n))
                lhs -= sum(w[j]*U[i][j]*f[j] for j in range(n))**2
                rhs = sum(w[j]*w[k]*U[i][j]*U[i][k]*(f[j]-f[k])**2
                          for j in range(n) for k in range(n))/2
                assert lhs == rhs and rhs >= 0
                cases += 1
    return cases


if __name__ == "__main__":
    print(json.dumps({"arithmetic": "exact rational",
                     "constant_degree_transfer_counterexamples":
                         [counterexample(F(1, k)) for k in (3, 4, 8, 16)],
                     "weighted_cs_root_checks": weighted_cs_checks(),
                     "new_global_lower_bound": False}, indent=2))
