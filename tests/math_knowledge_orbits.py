#!/usr/bin/env python3
"""Compile the actual handbook example; compare with canonical orbit enumeration.

No Python packages needed. Uses the repository compiler_config.CXX discovery.
--sanitize reruns the same cases under ASan and UBSan, without changing sources.
All generated source, executables and diagnostics remain in a temporary directory.
"""
import argparse
from collections import Counter
from itertools import product
from pathlib import Path
import os
import re
import shlex
import subprocess
import tempfile

from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
ULL_MAX = (1 << 64) - 1


def canonical(word, flip):
    """Explicitly form equivalent words; no Burnside/counting formula."""
    candidates = [word[i:] + word[:i] for i in range(len(word))]
    if flip:
        reverse = word[::-1]
        candidates += [reverse[i:] + reverse[:i] for i in range(len(word))]
    return min(candidates)


def orbit_inventory(n, k, flip):
    representatives = {canonical(word, flip) for word in product(range(k), repeat=n)}
    return Counter(tuple(word.count(c) for c in range(k)) for word in representatives)


def group_permutations(n, flip):
    # Retain the full formal group, including its kernel when n = 1 or 2.
    for t in range(n):
        yield tuple((i + t) % n for i in range(n))
    if flip:
        for t in range(n):
            yield tuple((t - i) % n for i in range(n))


def cycle_lengths(permutation):
    seen = set()
    lengths = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        current, size = start, 0
        while current not in seen:
            seen.add(current)
            size += 1
            current = permutation[current]
        assert current == start
        lengths.append(size)
    return sorted(lengths)


def fixed_inventory_dp(lengths, k):
    """Coefficients of the cycle product, tested against actual orbit objects."""
    counts = Counter({(0,) * k: 1})
    for length in lengths:
        updated = Counter()
        for inventory, count in counts.items():
            for color in range(k):
                state = list(inventory)
                state[color] += length
                updated[tuple(state)] += count
        counts = updated
    return counts


def fixed_red_dp(lengths, red, mod):
    if not 0 <= red <= sum(lengths):
        return 0
    counts = [0] * (red + 1)
    counts[0] = 1 % mod
    for length in lengths:
        for s in range(red, length - 1, -1):
            counts[s] = (counts[s] + counts[s - length]) % mod
    return counts[red]


def inventory_from_cycles(n, k, flip):
    total = Counter()
    for permutation in group_permutations(n, flip):
        total.update(fixed_inventory_dp(cycle_lengths(permutation), k))
    h = n * (2 if flip else 1)
    assert all(count % h == 0 for count in total.values())
    return Counter({inventory: count // h for inventory, count in total.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    cases, expected = [], []
    inventory_cases = 0
    binary_dp_cases = 0
    reflection_cases = 0
    objects = 0
    cache = {}

    for n in range(1, 9):
        for k in range(5):
            objects += k ** n
            for flip in (False, True):
                inventory = orbit_inventory(n, k, flip)
                cache[n, k, flip] = inventory
                count = sum(inventory.values())
                h = n * (2 if flip else 1)
                for mod in (1, 2, 3, 4, 6, 8, 12, 97, 998244353, ULL_MAX // h):
                    cases.append(f"{n} {k} {mod} {int(flip)}")
                    expected.append(count % mod)
                if k <= 3:
                    got = inventory_from_cycles(n, k, flip)
                    assert got == inventory, (n, k, flip, got, inventory)
                    inventory_cases += max(1, len(inventory))

        for t in range(n):
            permutation = tuple((t - i) % n for i in range(n))
            lengths = cycle_lengths(permutation)
            if n % 2:
                want = [1] + [2] * ((n - 1) // 2)
            elif t % 2 == 0:
                want = [1, 1] + [2] * ((n - 2) // 2)
            else:
                want = [2] * (n // 2)
            assert lengths == want, (n, t, lengths, want)
            reflection_cases += 1

        # Binary coefficient DP, including out-of-range inventories, checked
        # against individually enumerated fixed words, without cycle coloring.
        for permutation in group_permutations(n, True):
            lengths = cycle_lengths(permutation)
            fixed = Counter()
            for word in product(range(2), repeat=n):
                if all(word[i] == word[permutation[i]] for i in range(n)):
                    fixed[sum(word)] += 1
            for red in range(-1, n + 2):
                for mod in (1, 2, 4, 12, 97):
                    got = fixed_red_dp(lengths, red, mod)
                    assert got == fixed[red] % mod, (n, permutation, red, mod, got)
                    binary_dp_cases += 1

    # n = 1: choose one color. n = 2: choose an unordered pair with repetition.
    # These elementary object counts independently exercise huge k and products.
    wide_cases = 0
    for n in (1, 2):
        for k in (1 << 32, (1 << 63) - 1, 1 << 63, ULL_MAX):
            count = k if n == 1 else k * (k + 1) // 2
            for flip in (False, True):
                h = n * (2 if flip else 1)
                for mod in (1, 2, 3, 6, 8, 12, (1 << 32) - 1, ULL_MAX // h):
                    cases.append(f"{n} {k} {mod} {int(flip)}")
                    expected.append(count % mod)
                    wide_cases += 1

    # Larger lengths with zero or one color have an immediate object oracle.
    for n in (9, 17, 100, 999, 10000):
        for k in (0, 1):
            for flip in (False, True):
                h = n * (2 if flip else 1)
                for mod in (1, 6, ULL_MAX // h):
                    cases.append(f"{n} {k} {mod} {int(flip)}")
                    expected.append(k % mod)

    # Published examples and small degeneracies.
    assert sum(cache[4, 2, False].values()) == 6
    assert sum(cache[6, 2, False].values()) == 14
    assert sum(cache[6, 2, True].values()) == 13
    assert sum(cache[5, 3, False].values()) == 51
    assert sum(cache[5, 3, True].values()) == 39
    assert cache[6, 2, False][3, 3] == 4
    assert cache[6, 2, True][3, 3] == 3

    # "Position 0 is red" is not rotation invariant. Its restricted fixed-point
    # average is 3, whereas 5 full rotation orbits have a red-first representative.
    subset = [word for word in product(range(2), repeat=4) if word[0] == 1]
    intersecting = {canonical(word, False) for word in subset}
    invalid_sum = sum(all(word[i] == word[p[i]] for i in range(4))
                      for p in group_permutations(4, False) for word in subset)
    assert invalid_sum == 12 and len(intersecting) == 5
    assert any(word[p[0]] != 1 for p in group_permutations(4, False) for word in subset)

    # The additive lifting claim uses ordinary integer division after reduction.
    assert (24 % 32) // 4 == 6 and (24 % 8) // 4 != 6

    text = (ROOT / "docs/knowledge-orbits.tex").read_text()
    snippets = re.findall(
        r"% BEGIN orbit-counting-example\s*\\begin\{lstlisting\}\n(.*?)"
        r"\\end\{lstlisting\}\s*% END orbit-counting-example", text, flags=re.S)
    assert len(snippets) == 1, "Expected one actual compilable handbook example"
    with tempfile.TemporaryDirectory(prefix="cpc-orbits-") as temp:
        cpp, exe = Path(temp) / "example.cpp", Path(temp) / "example"
        cpp.write_text(snippets[0])
        flags = ["-std=c++20", "-Wall", "-Wextra"]
        if args.sanitize:
            flags += ["-O1", "-g", "-fsanitize=address,undefined",
                      "-fno-omit-frame-pointer", "-no-pie"]
        else:
            flags += ["-O2"]
        subprocess.run(shlex.split(CXX) + flags
                       + ["-I", str(ROOT), str(cpp), "-o", str(exe)], check=True)
        env = os.environ.copy()
        if args.sanitize:
            # LeakSanitizer cannot run under the executor's ptrace sandbox.
            env["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
            env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        result = subprocess.run([str(exe)], input="\n".join(cases) + "\n",
                                text=True, capture_output=True, env=env)
        assert result.returncode == 0, (result.returncode, result.stderr)
    actual = list(map(int, result.stdout.split()))
    assert len(actual) == len(expected), (len(actual), len(expected))
    for case, got, want in zip(cases, actual, expected):
        assert got == want, (case, got, want)
    assert not result.stderr, result.stderr
    mode = "ASan/UBSan" if args.sanitize else "optimized"
    print(f"PASS: {len(cases)} extracted C++ cases ({mode}), including {wide_cases} wide cases")
    print(f"PASS: {objects} labeled words per symmetry mode; {inventory_cases} inventory orbits checks")
    print(f"PASS: {binary_dp_cases} binary DP checks; {reflection_cases} reflection cycle checks")
    print("Limits: exhaustive n=1..8, k=0..4; inventory k<=3; extra n<=10000 and 64-bit k/M")
    print("Local knowledge-example tests only; no new OJ claim")


if __name__ == "__main__":
    main()
