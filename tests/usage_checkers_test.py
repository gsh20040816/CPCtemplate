"""Reject invalid certificates after separating checks from runner bookkeeping."""
from usage_checkers import check_output

controls = [
    ('example-73', '', '14\n1 1\n', {'weighted_matching': [[7, 7], [7, 7]]}),
    ('example-72', '', '2\n0 1\n1 2\n', {'matching': (4, [(0, 1), (1, 2)], 2)}),
    ('example-80', '', '11\n0 1\n', {'assignment': [[5, 1], [2, 6]]}),
    ('example-81', '', '2\n0 0\n', {'recurrence': ([0, 1, 1, 2, 3], 2)}),
    ('example-61', '', 'nan 0 0\n', {'values': [1, 0, 0], 'atol': 1e-10}),
    ('example-65', '', '0 0\n', {'diameter_cases': [[(0, 0), (1, 1)]]}),
    ('example-48', '1\n8 1\n', '0\n', '0'),
    ('example-24', '', '1\n3 0\n0 0\n', {'a': [[1, 1]], 'b': [3], 'nullity': 1}),
    ('example-4', '', '1\n3 1 2\n', [(1, 2)])
]
for example, data, output, expected in controls:
    try:
        check_output(example, 'negative-control', data, output, expected)
    except AssertionError:
        continue
    raise AssertionError(f'Invalid certificate accepted: {example}')
check_output('example-73', 'positive-control', '', '14\n2 1\n', {'weighted_matching': [[7, 7], [7, 7]]})
check_output('example-48', 'positive-control', '1\n8 1\n', '0\n\n', '0')
print('Usage checkers: 9 invalid certificates rejected; valid matching and required blank line accepted')
