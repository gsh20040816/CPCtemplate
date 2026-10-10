#!/usr/bin/env python3
import sys

data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
a = data[1:]
assert len(a) == n
# Nonempty maximum subarray sum.
print(max(sum(a[l:r]) for l in range(n) for r in range(l + 1, n + 1)))
