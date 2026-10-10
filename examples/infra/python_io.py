import sys

# Input: n followed by n integers, possibly across multiple lines.
it = iter(map(int, sys.stdin.buffer.read().split()))
n = next(it)
a = [next(it) for _ in range(n)]
sys.stdout.write(str(sum(a)) + "\n")
sys.stdout.write(" ".join(map(str, a)) + "\n")
