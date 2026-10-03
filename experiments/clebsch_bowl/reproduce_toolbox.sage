# Prepared from https://arxiv.org/html/2601.06590v1 section 1.3 / 2.4.
# Executed successfully; receipt: reports/toolbox-reproduction-001/run.log.
# Requires the author's SageMath fork, not ordinary SageMath.
# Run: <toolbox-sage> experiments/clebsch_bowl/reproduce_toolbox.sage
# Documented upstream revision: 9a9f84d. Record actual revision with output.
from itertools import combinations

GraphTheory.reset()
try:
    red_k4 = GraphTheory(4, edges=list(combinations(range(4), 2)))
    blue_k4 = GraphTheory(4, edges=[])
    objective = red_k4 + blue_k4
    numerical = GraphTheory.optimize(objective, 6, maximize=False)
    print("N6 K4 plus independent-four numerical lower bound:", numerical)
    rational = GraphTheory.optimize(objective, 6, maximize=False, exact=True,
                                   denom=10**10)
    print("N6 exact rounded lower bound:", rational)
finally:
    GraphTheory.reset()
