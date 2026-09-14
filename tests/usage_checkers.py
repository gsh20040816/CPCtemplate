"""Output certificates, isolated from example selection and proof bookkeeping."""
import itertools
import math


def check_output(example_id, mode, data, stdout, expected):
    if isinstance(expected, str):
        assert stdout.split() == expected.split(), (example_id, mode, stdout, expected)
        if example_id == 'example-48':
            queries = [list(map(int, line.split())) for line in data.splitlines()[1:]]
            lines = stdout.splitlines()
            assert len(lines) == 2 * len(queries), 'Each primitive-root query needs two output lines'
            for i, (_, step) in enumerate(queries):
                count = int(lines[2 * i])
                assert len(lines[2 * i + 1].split()) == count // step
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
