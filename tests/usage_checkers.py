"""Output certificates, isolated from example selection and proof bookkeeping."""
import itertools
import math


def check_output(example_id, mode, data, stdout, expected):
    if isinstance(expected, dict) and 'manhattan_mst' in expected:
        values = list(map(int, data.split()))
        n = values[0]
        assert n >= 1 and len(values) == 1 + 2 * n
        points = list(zip(values[1::2], values[2::2]))
        output = list(map(int, stdout.split()))
        assert len(output) == 1 + 2 * (n - 1)
        parent = list(range(n))
        def root(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        cost = 0
        for u, v in zip(output[1::2], output[2::2]):
            assert 0 <= u < n and 0 <= v < n
            a, b = root(u), root(v)
            assert a != b
            parent[a] = b
            cost += abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1])
        assert len({root(i) for i in range(n)}) == 1
        assert output[0] == cost == expected['manhattan_mst']
        return
    if isinstance(expected, dict) and 'tourist_reform' in expected:
        values = list(map(int, data.split()))
        n, m = values[:2]
        edges = list(zip(values[2::2], values[3::2]))
        lines = [list(map(int, line.split())) for line in stdout.splitlines()]
        optimum = expected['tourist_reform']
        assert len(edges) == m and len(lines) == m + 1
        assert lines[0] == [optimum]
        graph = [[] for _ in range(n + 1)]
        for line, (u, v) in zip(lines[1:], edges):
            assert len(line) == 2 and tuple(line) in ((u, v), (v, u))
            graph[line[0]].append(line[1])
        counts = []
        for start in range(1, n + 1):
            seen, order = {start}, [start]
            for u in order:
                for v in graph[u]:
                    if v not in seen:
                        seen.add(v)
                        order.append(v)
            counts.append(len(seen))
        assert min(counts) == optimum
        return
    if isinstance(expected, dict) and 'circulation' in expected:
        values = list(map(int, data.split()))
        n, m = values[:2]
        edges = [values[i:i + 4] for i in range(2, len(values), 4)]
        assert len(edges) == m
        lines = stdout.splitlines()
        if not expected['circulation']:
            assert lines == ['NO'], (example_id, mode, stdout)
            return
        assert len(lines) == m + 1 and lines[0] == 'YES'
        balance = [0] * (n + 1)
        for line, (u, v, lo, hi) in zip(lines[1:], edges):
            assert len(line.split()) == 1
            f = int(line)
            assert lo <= f <= hi
            balance[u] -= f
            balance[v] += f
        assert not any(balance), (example_id, mode, balance)
    elif isinstance(expected, str):
        assert stdout.split() == expected.split(), (example_id, mode, stdout, expected)
        if example_id == 'example-48':
            queries = [list(map(int, line.split())) for line in data.splitlines()[1:]]
            lines = stdout.splitlines()
            assert len(lines) == 2 * len(queries), 'Each primitive-root query needs two output lines'
            for i, (_, step) in enumerate(queries):
                count = int(lines[2 * i])
                assert len(lines[2 * i + 1].split()) == count // step
    elif isinstance(expected, dict) and 'project_plan' in expected:
        profit, needs, cost, best = expected['project_plan']
        lines = stdout.splitlines()
        assert len(lines) == 3, 'Two selection lines and one objective line required'
        a, b = [list(map(int, line.split())) for line in lines[:2]]
        assert len(a) == len(set(a)) and len(b) == len(set(b)), 'Duplicate IDs'
        assert all(1 <= i <= len(profit) for i in a)
        assert all(1 <= j <= len(cost) for j in b)
        tools = {j-1 for j in b}
        assert all(set(needs[i-1]) <= tools for i in a), 'Missing required instrument'
        value = sum(profit[i-1] for i in a) - sum(cost[j-1] for j in b)
        assert lines[2].split() == [str(best)] and value == best
    elif isinstance(expected, dict) and 'xor_system' in expected:
        a, b = expected['xor_system']
        n = len(a[0])
        # Small printed examples: enumerate the entire solution set independently.
        def image(x):
            return ''.join(str(sum(int(u) * int(v) for u, v in zip(row, x)) % 2) for row in a)
        solutions = {''.join(x) for x in itertools.product('01', repeat=n) if image(x) == b}
        if not solutions:
            assert stdout.split() == ['-1']
            return
        lines = stdout.splitlines()
        dim = len(solutions).bit_length() - 1
        assert lines[0] == str(dim) and len(lines) == dim + 2
        assert all(len(v) == n and set(v) <= {'0', '1'} for v in lines[1:])
        produced = set()
        for mask in range(1 << dim):
            x = list(map(int, lines[1]))
            for i, v in enumerate(lines[2:]):
                if mask >> i & 1:
                    x = [u ^ int(w) for u, w in zip(x, v)]
            produced.add(''.join(map(str, x)))
        assert produced == solutions
    elif isinstance(expected, dict) and 'odd_partition' in expected:
        n, edges = expected['odd_partition']
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        seen = set()
        possible = True
        for u in range(n):
            if u in seen:
                continue
            q = [u]
            seen.add(u)
            for v in q:
                for w in g[v]:
                    if w not in seen:
                        seen.add(w)
                        q.append(w)
            possible &= len(q) % 2 == 0
        color = list(map(int, stdout.split()))
        if not possible:
            assert color == [-1]
        else:
            assert len(color) == n and all(1 <= c <= n for c in color)
            degree = [0] * n
            for u, v in edges:
                if color[u] == color[v]:
                    degree[u] += 1
                    degree[v] += 1
            assert all(d % 2 == 1 for d in degree)
    elif isinstance(expected, dict) and 'exact_text' in expected:
        assert stdout == expected['exact_text'], (example_id, mode, stdout, expected)
    elif isinstance(expected, dict) and 'matching' in expected:
        n, edges, size = expected['matching']
        lines = [list(map(int, line.split())) for line in stdout.splitlines()]
        assert lines[0] == [size] and len(lines) == size + 1
        allowed = {tuple(sorted(e)) for e in edges}
        used = set()
        for edge in lines[1:]:
            assert len(edge) == 2
            u, v = edge
            assert 0 <= u < n and 0 <= v < n and u != v
            assert tuple(sorted(edge)) in allowed and u not in used and v not in used
            used.update(edge)
    elif isinstance(expected, dict) and 'recurrence' in expected:
        sequence, order = expected['recurrence']
        output = list(map(int, stdout.split()))
        assert len(output) == order + 1 and output[0] == order
        coefficients = output[1:]
        assert all(0 <= c < 998244353 for c in coefficients)
        for i in range(order, len(sequence)):
            assert sum(c * sequence[i - j - 1] for j, c in enumerate(coefficients)) % 998244353 == sequence[i]
    elif isinstance(expected, dict) and 'assignment' in expected:
        costs = expected['assignment']
        n = len(costs)
        output = list(map(int, stdout.split()))
        assert len(output) == n + 1 and sorted(output[1:]) == list(range(n))
        value = sum(costs[i][j] for i, j in enumerate(output[1:]))
        optimum = min(sum(costs[i][p[i]] for i in range(n))
                      for p in itertools.permutations(range(n)))
        assert output[0] == value == optimum
    elif isinstance(expected, dict) and 'weighted_matching' in expected:
        weights = expected['weighted_matching']
        n = len(weights)
        output = list(map(int, stdout.split()))
        assert len(output) == n + 1 and sorted(output[1:]) == list(range(1, n + 1))
        matched_weights = [weights[u - 1][v] for v, u in enumerate(output[1:])]
        assert all(w is not None for w in matched_weights)
        optimum = max(sum(weights[p[v]][v] for v in range(n))
                      for p in itertools.permutations(range(n))
                      if all(weights[p[v]][v] is not None for v in range(n)))
        assert output[0] == sum(matched_weights) == optimum
    elif isinstance(expected, dict) and 'closest_cases' in expected:
        lines = stdout.splitlines()
        assert len(lines) == len(expected['closest_cases'])
        for line, points in zip(lines, expected['closest_cases']):
            a, b = map(int, line.split())
            assert 0 <= a < len(points) and 0 <= b < len(points) and a != b
            distance = lambda p, q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
            assert distance(points[a], points[b]) == min(distance(p, q) for p, q in itertools.combinations(points, 2))
    elif isinstance(expected, dict) and 'diameter_cases' in expected:
        lines = stdout.splitlines()
        assert len(lines) == len(expected['diameter_cases'])
        for line, points in zip(lines, expected['diameter_cases']):
            a, b = map(int, line.split())
            assert 0 <= a < len(points) and 0 <= b < len(points) and a != b
            distance = lambda p, q: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
            assert distance(points[a], points[b]) == max(distance(p, q) for p in points for q in points)
    elif isinstance(expected, dict) and 'values' in expected:
        actual = list(map(float, stdout.split()))
        assert len(actual) == len(expected['values'])
        assert all(math.isfinite(x) and abs(x - y) <= expected['atol']
                   for x, y in zip(actual, expected['values'])), (example_id, mode, actual, expected)
    elif isinstance(expected, dict) and 'mixed_euler_demo' in expected:
        from mixed_euler_demo import check_output as check_mixed_euler_demo
        check_mixed_euler_demo(data, stdout)
    elif isinstance(expected, dict):
        lines = [list(map(int, line.split())) for line in stdout.splitlines()]
        dim = expected['nullity']
        assert dim in (0, 1), 'These certificates only establish independence for at most one basis vector'
        assert lines[0] == [dim] and len(lines) == dim + 2
        m = len(expected['a'][0])
        assert all(len(v) == m and all(0 <= x < 998244353 for x in v) for v in lines[1:])
        for a, b in zip(expected['a'], expected['b']):
            assert sum(x * y for x, y in zip(a, lines[1])) % 998244353 == b
            for v in lines[2:]:
                assert sum(x * y for x, y in zip(a, v)) % 998244353 == 0
        if dim:
            assert any(lines[2])
    else:
        lines = stdout.splitlines()
        assert int(lines[0]) == len(lines) - 1
        actual = []
        for line in lines[1:]:
            nums = list(map(int, line.split()))
            assert nums[0] == len(nums) - 1
            actual.append(tuple(sorted(nums[1:])))
        assert sorted(actual) == sorted(expected), (example_id, mode, actual)
