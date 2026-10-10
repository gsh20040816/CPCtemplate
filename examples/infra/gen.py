#!/usr/bin/env python3
import random
import sys

rng = random.Random(int(sys.argv[1]))
n = rng.randint(1, 12)
a = [rng.randint(-20, 20) for _ in range(n)]
print(n)
print(*a)
