"""E11: replace the Clebsch scheme by other rank-3 (srg) schemes {I, A, J-I-A}; same 12-block design and rule
(D,Z: 0 on I+A, 1 off; X: 1 on I+A; P: p on I+A; H: h on I, 1 on A)."""
import sys, json, itertools, numpy as np, networkx as nx
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import F
from design import types
from scipy.optimize import minimize
T = types(3, 2)
def build(A, p, h):
    q = len(A); I = np.eye(q); C = I + A
    g = {'Z': 1 - C, 'X': C, 'P': p * C, 'H': h * I + A}
    W = np.zeros((12*q, 12*q))
    for s in range(12):
        for t in range(12): W[s*q:(s+1)*q, t*q:(t+1)*q] = g[T[s][t]]
    return W
def paley(q):
    sq = {(x*x) % q for x in range(1, q)}; G = nx.Graph(); G.add_nodes_from(range(q))
    G.add_edges_from((a, b) for a in range(q) for b in range(a+1, q) if (a-b) % q in sq); return G
def clebsch():
    S = [1,2,4,8,15]; G = nx.Graph(); G.add_edges_from((x, x ^ s) for x in range(16) for s in S); return G
gs = {'clebsch': clebsch(), 'petersen': nx.petersen_graph(), 'C5': nx.cycle_graph(5), 'K33': nx.complete_bipartite_graph(3, 3),
      'K44': nx.complete_bipartite_graph(4, 4), 'paley9': paley(9), 'paley13': paley(13), 'paley17': paley(17),
      'T6': nx.line_graph(nx.complete_graph(6)), 'T7': nx.line_graph(nx.complete_graph(7)),
      'L2(4)': nx.cartesian_product(nx.complete_graph(4), nx.complete_graph(4)),
      'L2(5)': nx.cartesian_product(nx.complete_graph(5), nx.complete_graph(5)),
      'hoffman_singleton': nx.hoffman_singleton_graph(), 'K2x5_cocktail': nx.complement(nx.disjoint_union_all([nx.complete_graph(2)]*5)),
      'K4x4_(4K4)': nx.disjoint_union_all([nx.complete_graph(4)]*4), 'K3x3_(3K3)': nx.disjoint_union_all([nx.complete_graph(3)]*3)}
out = {}
for name, G in gs.items():
    for comp in (False, True):
        H = nx.complement(G) if comp else G
        A = nx.to_numpy_array(H, nodelist=sorted(H.nodes()))
        f = lambda x: F(build(A, *np.clip(x, 0, 1)), [0], [12*len(A)])
        best = min((minimize(f, x0, method='Nelder-Mead', options={'xatol':1e-7,'fatol':1e-13,'maxiter':200}) for x0 in [(0.78,0.53),(0.5,0.2),(0.9,0.9)]), key=lambda r: r.fun)
        key = name + ('^c' if comp else ''); out[key] = {'q': len(A), 'deg': int(A.sum(1)[0]), 'F': best.fun, 'ph': list(np.clip(best.x, 0, 1))}
        print(key, out[key], flush=True)
json.dump(out, open(sys.argv[1] + '/srg.json', 'w'), indent=1, default=float)
