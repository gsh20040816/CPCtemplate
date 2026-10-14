#!/usr/bin/env python3
"""Brute-force game searches confirming every closed form in docs/knowledge-games.tex."""
from functools import lru_cache
from itertools import combinations, product
from math import isqrt
import random
import sys

sys.setrecursionlimit(100000)
checks = 0


def ok(cond, *what):
    global checks
    assert cond, what
    checks += 1


def mex(values):
    s, g = set(values), 0
    while g in s:
        g += 1
    return g


# 1. Bash: one pile, take 1..k; previous player wins when no move.
for k in range(1, 11):
    win = [False] * 81
    for n in range(1, 81):
        win[n] = any(not win[n - t] for t in range(1, min(k, n) + 1))
        ok(win[n] == (n % (k + 1) != 0), 'bash', n, k)


# 2. Nim: XOR of pile sizes.
@lru_cache(None)
def nim_win(piles):
    for i, x in enumerate(piles):
        for y in range(x):
            nxt = tuple(sorted(piles[:i] + (y,) + piles[i + 1:]))
            if not nim_win(nxt):
                return True
    return False


for piles in product(range(8), repeat=3):
    x = piles[0] ^ piles[1] ^ piles[2]
    ok(nim_win(tuple(sorted(piles))) == (x != 0), 'nim', piles)


# 3. Wythoff: remove any from one pile, or the same amount from both.
N = 70
wy = [[False] * (N + 1) for _ in range(N + 1)]
for a in range(N + 1):
    for b in range(N + 1):
        moves = [(a - t, b) for t in range(1, a + 1)] + [(a, b - t) for t in range(1, b + 1)]
        moves += [(a - t, b - t) for t in range(1, min(a, b) + 1)]
        wy[a][b] = any(not wy[x][y] for x, y in moves)
for a in range(N + 1):
    for b in range(a, N + 1):
        d = b - a
        ok((not wy[a][b]) == (a == (d + isqrt(5 * d * d)) // 2), 'wythoff', a, b)


# 4. Fibonacci Nim: first move takes 1..n-1, then each move takes 1..2*(previous move).
@lru_cache(None)
def fib_win(n, limit):
    return any(not fib_win(n - t, 2 * t) for t in range(1, min(limit, n) + 1))


fibs = {1, 2}
a, b = 1, 2
while b < 200:
    a, b = b, a + b
    fibs.add(b)
for n in range(2, 160):
    ok((not fib_win(n, n - 1)) == (n in fibs), 'fibonacci', n)
    if n not in fibs:  # winning move: take the smallest Zeckendorf term
        rest, terms = n, []
        for f in sorted(fibs, reverse=True):
            if f <= rest:
                terms.append(f)
                rest -= f
        t = min(terms)
        ok(t <= n - 1 and not fib_win(n - t, 2 * t), 'fibonacci move', n, t)


# 5. Staircase Nim: move t>=1 coins from stair i>=1 to stair i-1; stair 0 is the ground.
@lru_cache(None)
def stair_win(c):
    for i in range(1, len(c)):
        for t in range(1, c[i] + 1):
            d = list(c)
            d[i] -= t
            d[i - 1] += t
            d[0] = 0  # coins on the ground never move again
            if not stair_win(tuple(d)):
                return True
    return False


for k in range(1, 5):
    for c in product(range(4), repeat=k):
        x = 0
        for i in range(1, k + 1, 2):
            x ^= c[i - 1]
        ok(stair_win((0,) + c) == (x != 0), 'staircase', c)


# 6. Anti-Nim (misere): whoever takes the last stone loses.
@lru_cache(None)
def anti_win(piles):
    if not any(piles):
        return True  # the previous player took the last stone and lost
    for i, x in enumerate(piles):
        for y in range(x):
            if not anti_win(tuple(sorted(piles[:i] + (y,) + piles[i + 1:]))):
                return True
    return False


for m in range(1, 4):
    for piles in product(range(7), repeat=m):
        if not any(piles):
            continue
        x = 0
        for p in piles:
            x ^= p
        big = any(p > 1 for p in piles)
        ok(anti_win(tuple(sorted(piles))) == ((not big and x == 0) or (big and x != 0)), 'anti-nim', piles)


# 7. Moore's Nim-k: each move takes >=1 from each of 1..k chosen piles.
def nimk_formula(piles, k):
    return all(sum(p >> bit & 1 for p in piles) % (k + 1) == 0 for bit in range(4))


for k in range(1, 4):
    @lru_cache(None)
    def nimk_win(piles, k=k):
        idx = [i for i, p in enumerate(piles) if p]
        for r in range(1, k + 1):
            for chosen in combinations(idx, r):
                for takes in product(*(range(1, piles[i] + 1) for i in chosen)):
                    d = list(piles)
                    for i, t in zip(chosen, takes):
                        d[i] -= t
                    if not nimk_win(tuple(sorted(d))):
                        return True
        return False
    for piles in product(range(6), repeat=4):
        ok((not nimk_win(tuple(sorted(piles)))) == nimk_formula(piles, k), 'nim-k', piles, k)


# 8. Green Hackenbush on a rooted tree: delete an edge, drop the part cut off from the root.
def hackenbush_sg_brute(parent):
    n = len(parent)
    children = [[] for _ in range(n)]
    for v in range(1, n):
        children[parent[v]].append(v)

    @lru_cache(None)
    def sg(alive):  # alive = frozenset of present non-root vertices (edge v-parent[v])
        options = []
        for v in alive:
            stack, cut = [v], {v}
            while stack:
                u = stack.pop()
                for w in children[u]:
                    if w in alive and w not in cut:
                        cut.add(w)
                        stack.append(w)
            options.append(sg(alive - cut))
        return mex(options)

    return sg(frozenset(range(1, n)))


def hackenbush_formula(parent):
    n = len(parent)
    g = [0] * n
    for v in range(n - 1, 0, -1):  # parents have smaller ids
        g[parent[v]] ^= g[v] + 1
    return g[0]


rng = random.Random(22)
for _ in range(400):
    n = rng.randint(1, 9)
    parent = [0] + [rng.randrange(v) for v in range(1, n)]
    ok(hackenbush_sg_brute(parent) == hackenbush_formula(parent), 'hackenbush', parent)


# 9. Undirected vertex geography: move the token to an unvisited neighbour; no move loses.
def max_matching(n, edges, banned=-1):
    best = 0
    for r in range(len(edges), 0, -1):
        for chosen in combinations(edges, r):
            used = set()
            good = True
            for u, v in chosen:
                if u in used or v in used or banned in (u, v):
                    good = False
                    break
                used |= {u, v}
            if good:
                return r
    return best


for _ in range(300):
    n = rng.randint(1, 7)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.45]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    @lru_cache(None)
    def geo_win(cur, seen):
        return any(not geo_win(v, seen | 1 << v) for v in adj[cur] if not seen >> v & 1)

    full = max_matching(n, edges)
    for s in range(n):
        in_every = max_matching(n, edges, banned=s) < full
        ok(geo_win(s, 1 << s) == in_every, 'geography', n, edges, s)


# 10. Circle of n coins, take 1 or 2 adjacent; last taker wins.
L = 60
line = [0] * (L + 1)
for m in range(1, L + 1):
    opts = set()
    for take in (1, 2):
        for left in range(0, m - take + 1):
            opts.add(line[left] ^ line[m - take - left])
    line[m] = mex(opts)
for n in range(1, L + 2):
    first = any(line[n - t] == 0 for t in (1, 2) if t <= n)
    ok(first == (n <= 2), 'circle', n)


# 11. Chomp: eat a cell and everything below-right; whoever must eat the poisoned corner loses.
@lru_cache(None)
def chomp_win(rows):
    if rows == (1,):
        return False  # only the poisoned corner is left
    for i, length in enumerate(rows):
        for j in range(length):
            if i == 0 and j == 0:
                continue
            d = list(rows[:i]) + [min(r, j) for r in rows[i:]]
            d = tuple(r for r in d if r)
            if not chomp_win(d):
                return True
    return False


for r in range(1, 5):
    for c in range(1, 6):
        if r * c > 1:
            ok(chomp_win(tuple([c] * r)), 'chomp', r, c)

print(f'Classic games: Bash, Nim, Wythoff, Fibonacci, staircase, anti-Nim, Nim-k, Hackenbush, '
      f'vertex geography, circle and Chomp brute searches PASS ({checks} checks)')
