"""Reject invalid certificates after separating checks from runner bookkeeping."""
from usage_checkers import check_output

controls = [
    ('example-143', '', '3\n000\n100\n010\n100\n', {'xor_system': (['000'], '0')}),
    ('example-143', '', '1\n10\n11\n', {'xor_system': (['11'], '0')}),
    ('example-143', '', '-1\n', {'xor_system': (['1'], '0')}),
    ('example-134', '', '0 0\n', {'closest_cases': [[(0,0),(0,0)]]}),
    ('example-134', '', '0 2\n', {'closest_cases': [[(0,0),(1,0),(5,0)]]}),
    ('example-96', '', '1 1 1 1\n', {'odd_partition': (4, [(0,1),(1,2),(2,3)])}),
    ('example-93', '', '4\n', {'exact_text': '4\n\n'}),
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
mixed = '1\nC 3 2 0 0\n1 2 1\n1 2 0\n'
marker = {'mixed_euler_demo': True}
for bad in ('NO\n', 'YES\nVERTICES 3 2 1 2\nEDGES 2 1 2\n',
            'YES\nVERTICES 3 1 2 1\nEDGES 2 1 1\n',
            'YES\nVERTICES 3 1 2 1\nEDGES 1 1\n'):
    controls.append(('example-206', mixed, bad, marker))
controls.append(('example-206', mixed.replace('C 3 2 0 0', 'P 3 2 2 2'),
                 'YES\nVERTICES 3 1 2 1\nEDGES 2 1 2\n', marker))
check_output('example-206', 'control', mixed,
             'YES\nVERTICES 3 1 2 1\nEDGES 2 1 2\n', marker)
free = '1\nA 2 1 0 0\n1 2 0\n'
check_output('example-206', 'control', free, 'YES\nVERTICES 2 1 2\nEDGES 1 1\n', marker)
check_output('example-206', 'control', free, 'YES\nVERTICES 2 2 1\nEDGES 1 1\n', marker)

square = '4\n0 0\n1 0\n0 1\n1 1\n'
for valid in ('3\n0 1\n1 3\n3 2\n', '3\n0 2\n2 3\n3 1\n'):
    check_output('example-236', 'positive-control', square, valid, {'manhattan_mst': 3})
for invalid in ('4\n0 1\n1 3\n3 2\n', '4\n0 1\n0 3\n0 2\n',
                '3\n0 1\n0 1\n2 3\n', '3\n0 0\n1 3\n3 2\n',
                '3\n0 4\n1 3\n3 2\n', '3\n0 1\n1 3\n',
                '3\n0 1\n1 3\n3 2\n0 2\n'):
    controls.append(('example-236', square, invalid, {'manhattan_mst': 3}))
check_output('example-236', 'positive-control', '1\n0 0\n', '0\n', {'manhattan_mst': 0})
check_output('example-236', 'positive-control', '2\n7 8\n7 8\n', '0\n0 1\n', {'manhattan_mst': 0})

for example, data, output, expected in controls:
    try:
        check_output(example, 'negative-control', data, output, expected)
    except AssertionError:
        continue
    raise AssertionError(f'Invalid certificate accepted: {example}')
check_output('example-73', 'positive-control', '', '14\n2 1\n', {'weighted_matching': [[7, 7], [7, 7]]})
check_output('example-48', 'positive-control', '1\n8 1\n', '0\n\n', '0')
check_output('example-93', 'positive-control', '', '4\n\n', {'exact_text': '4\n\n'})
check_output('example-96', 'positive-control', '', '1 1 2 2\n', {'odd_partition': (4, [(0,1),(1,2),(2,3)])})
check_output('example-134', 'positive-control', '', '1 0\n', {'closest_cases': [[(0,0),(0,0)]]})
check_output('example-143', 'positive-control', '', '1\n11\n11\n', {'xor_system': (['11'], '0')})
check_output('example-143', 'positive-control', '', '-1\n', {'xor_system': (['0'], '1')})
print(f'Usage checkers: {len(controls)} invalid certificates rejected; alternative MST trees and existing valid certificates accepted')
