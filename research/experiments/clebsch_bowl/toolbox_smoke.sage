# Run inside the FlagAlgebraToolbox Sage fork after installation.
GraphTheory.reset()
try:
    triangle = GraphTheory(3, edges=[[0,1],[0,2],[1,2]])
    edge = GraphTheory(2, edges=[[0,1]])
    GraphTheory.exclude(triangle)
    bound = GraphTheory.optimize(edge, 3, maximize=True, exact=True)
    assert bound == QQ(1)/2, bound
    print("PASS: exact Mantel bound", bound)
finally:
    GraphTheory.reset()
