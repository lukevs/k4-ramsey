"""Write 0/1 red adjacency rows (for the compiled Lean check_candidate) from a .red file."""
import sys
lines = open(sys.argv[1]).read().split("\n")
m, k, n = map(int, lines[0].split()); K2 = 1 << k
red = set(int(t) for t in lines[1].split())
sub = lambda x, y: (((x // K2) - (y // K2)) % m) * K2 + ((x % K2) ^ (y % K2))
open(sys.argv[2], "w").write("\n".join("".join("1" if sub(y, x) in red else "0" for y in range(n)) for x in range(n)) + "\n")
