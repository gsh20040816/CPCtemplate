from collections import Counter, defaultdict, deque
from itertools import accumulate, combinations, permutations, product
from heapq import heapify, heappop, heappush
from bisect import bisect_left, bisect_right
from functools import cache

assert list(combinations(range(4), 2))[-1] == (2, 3)
assert len(list(permutations(range(4)))) == 24
assert len(list(product(range(2), repeat=5))) == 32
assert list(accumulate([2, -1, 4], initial=0)) == [0, 2, 1, 5]
assert Counter("ababa")["a"] == 3
g = defaultdict(list)
g[2].append(3)
assert g[2] == [3]
q = deque([1, 2])
q.appendleft(0)
assert q.popleft() == 0
h = [5, 2, 7]
heapify(h)
heappush(h, 1)
assert heappop(h) == 1
a = [1, 2, 2, 4]
assert bisect_right(a, 2) - bisect_left(a, 2) == 2

@cache
def paths(r, c):
    if r == 0 or c == 0:
        return 1
    return paths(r - 1, c) + paths(r, c - 1)

assert paths(10, 10) == 184756
paths.cache_clear()
rows = [[0] * 2 for _ in range(3)]
rows[0][0] = 7
assert rows[1][0] == 0
print("containers: pass")
