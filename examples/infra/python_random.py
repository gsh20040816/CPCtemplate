import random

rng = random.Random(2026)
a = rng.randint(-5, 5)
b = rng.randrange(2, 10, 2)
c = rng.choice("abc")
v = rng.sample(range(100), 10)
rng.shuffle(v)
assert -5 <= a <= 5
assert b in (2, 4, 6, 8)
assert c in "abc"
assert len(set(v)) == 10
rng.seed(42)
first = [rng.randrange(1000) for _ in range(10)]
rng.seed(42)
assert first == [rng.randrange(1000) for _ in range(10)]
print("random: pass")
