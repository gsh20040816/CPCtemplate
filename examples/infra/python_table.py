from itertools import product

# Binary strings with no adjacent ones, including the empty string.
counts = []
for n in range(11):
    good = 0
    for a in product(range(2), repeat=n):
        if all(a[i - 1] + a[i] < 2 for i in range(1, n)):
            good += 1
    counts.append(good)
    print(n, good)
assert counts[:2] == [1, 2]
assert all(counts[n] == counts[n - 1] + counts[n - 2]
           for n in range(2, len(counts)))
