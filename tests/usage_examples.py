"""Compile the exact printed usage listings with their declared template context."""
from compiler_config import CXX
from usage_checkers import check_output
from pathlib import Path
import argparse
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import records

cases = {
    'example-1': [('4 5 1 4\n1 2 3\n1 3 2\n2 3 1\n2 4 2\n3 4 4\n', '5'), ('2 3 1 2\n1 2 0\n1 2 7\n2 1 10\n', '7')],
    'example-2': [('3 3\n0 1\n1 2\n2 1\n', '2 1 0 2 1 2'), ('1 0\n', '1 1 0')],
    'example-3': [('p cnf 2 2\n1 1 0\n-2 -2 0\n', 's SATISFIABLE v 1 -2 0'), ('p cnf 1 2\n1 1 0\n-1 -1 0\n', 's UNSATISFIABLE')],
    'example-4': [('5 4\n1 2\n2 3\n3 1\n3 4\n', [(1, 2, 3), (3, 4), (5,)]), ('2 2\n1 2\n2 1\n', [(1, 2)])],
    'example-5': [('5 4\n1 2\n2 3\n3 1\n3 4\n', [(1, 2, 3), (4,), (5,)]), ('2 2\n1 2\n2 1\n', [(1, 2)])],
    'example-6': [('4 5\n1 2 3 4\n0 2\n2 3\n0 3\n1 2\n1 3\n', '36'), ('3 3\n998244352 998244352 998244352\n0 1\n1 2\n2 0\n', '998244352')],
    'example-7': [('5 7\n2 1 2\n1 1 2\n2 1 2\n1 3 4\n2 1 4\n1 2 3\n2 1 4\n', 'N Y N Y'), ('1 1\n2 1 1\n', 'Y')]
}
cases.update({'example-100': [('2\n0 1\n1 0\n', '0 1 1 0'), ('2\n1 2\n2 4\n', 'No Solution'), ('1\n2\n', '500000004')], 'example-101': [('2\n0 1\n1 0\n', '0 1 1 0'), ('2\n1 2\n2 4\n', '-1'), ('1\n2\n', '499122177')]})
cases.update({'example-102': [('2\n01\n10\n', '01 10'), ('2\n11\n11\n', '-1'), ('1\n1\n', '1'), ('3\n110\n011\n001\n', '111 011 001')]})
ordered = [('12\n1 5\n1 2\n1 5\n3 5\n4 3\n5 5\n6 2\n2 5\n3 6\n4 2\n2 2\n4 1\n', '2 5 2 5 3 5 5'), ('5\n1 -3\n1 7\n3 -3\n5 7\n6 -3\n', '1 -3 7')]
cases.update({
    'example-8': ordered,
    'example-9': ordered,
    'example-10': [('5 3\n2 4\n1 5\n3 3\n', '5 2 3 4 1'), ('1 2\n1 1\n1 1\n', '1')],
    'example-11': [('3 5\n10 20 30\n0 1 2 99\n0 2 2\n1 2 2\n2 1 1 -7\n4 2 1\n', '20 99 -7'), ('1 3\n7\n0 2 1\n1 1 1 8\n0 2 1\n', '7 7')],
    'example-12': [('3 5 100\n1 2 3\n3 1 3\n1 1 2 3\n2 2 3 5\n3 1 3\n3 2 2\n', '6 22 11'), ('2 3 1\n4 5\n1 1 2 9\n2 1 1 3\n3 1 2\n', '0')]
})
cases.update({
    'example-13': [('6\n1\n2\n4\n561\n1000000007\n1000000000000000000\n', 'No Yes No No Yes No'), ('3\n997\n9991\n998244353\n', 'Yes No Yes')],
    'example-14': [('3\n3 5 2 1\n4 3 2 2\n1 1 0 0\n', '1 5 0'), ('1\n1000000000 2 1 1\n', '250000000000000000')],
    'example-15': [('2\n3 2\n5 3\n', '8'), ('2\n6 4\n8 4\n', '4')],
    'example-16': [('3 2\n1 2 3\n4 5\n', '4 13 22 15'), ('1 1\n998244352\n998244352\n', '1')],
    'example-17': [('3 3\n0 3\n1 6\n2 11\n', '18'), ('1 100\n7 42\n', '42')],
    'example-18': [('4\n1 1 0 0\n', '1 998244352 1 998244352'), ('1\n2\n', '499122177')]
})
cases.update({
    'example-19': [('banana\n', '6 4 2 1 5 3'), ('aaaa\n', '4 3 2 1')],
    'example-20': [('aaa\n', '1 1 2'), ('aba\n', '1 1 1')],
    'example-21': [('aaa\n', '4'), ('ababa\n', '6')],
    'example-22': [('ababa\n', '5 0 3 0 1'), ('aaaa\n', '4 3 2 1')],
    'example-23': [('aba\n', '1 0 3 0 1'), ('abba\n', '1 0 1 4 1 0 1')]
})
cases.update({
    'example-24': [('2 2\n1 0\n0 1\n2 3\n', '0 2 3'), ('1 2\n1 1\n3\n', {'a': [[1, 1]], 'b': [3], 'nullity': 1}), ('2 1\n1\n1\n1 2\n', '-1')],
    'example-25': [('2\n1 2\n3 4\n', '998244351'), ('2\n1 2\n2 4\n', '0')],
    'example-26': [('2 3 2\n1 2 3\n4 5 6\n7 8\n9 10\n11 12\n', '58 64 139 154'), ('1 1 1\n998244352\n998244352\n', '1')],
    'example-27': [('1\n1 2\n3 4\n', '3 18 13 8 11 10'), ('0\n2\n3\n', '6 6 6')]
})
cases.update({
    'example-28': [('4\n1 1 0 0\n', '0 1 499122176 332748118'), ('1\n1\n', '0'), ('3\n1 0 0\n', '0 0 0')],
    'example-29': [('4\n0 1 0 0\n', '1 1 499122177 166374059'), ('1\n0\n', '1'), ('3\n0 0 0\n', '1 0 0')],
    'example-30': [('3 2\n1 2 3\n', '17 14 3'), ('3 0\n998244352 2 3\n', '998244352 2 3'), ('1 998244352\n7\n', '7')],
    'example-31': [('3 3 2 2\n1 2 3\n', '17 57 209'), ('3 3 2 0\n1 2 3\n', '17 1 1'), ('3 3 0 2\n1 2 3\n', '1 1 1'), ('3 3 2 1\n1 2 3\n', '17 17 17'), ('2 2 998244352 998244352\n1 1\n', '0 2')]
})
lca_cases = [('5 5 3\n1 2\n1 3\n3 4\n3 5\n2 4\n1 2\n4 5\n2 2\n3 2\n', '3 1 3 2 3'), ('1 2 1\n1 1\n1 1\n', '1 1'), ('4 3 4\n1 2\n2 3\n3 4\n1 2\n1 3\n4 2\n', '2 3 4')]
cases.update({
    'example-32': lca_cases,
    'example-33': lca_cases,
    'example-34': lca_cases,
    'example-35': [('2 2 3\n1 1\n1 2\n2 1\n', '2'), ('3 2 0\n', '0'), ('3 2 4\n1 1\n1 1\n2 1\n3 2\n', '2')]
})
cases.update({
    'example-36': [('4\n1 2 3 4\n', '7'), ('3\n0 0 0\n', '0'), ('3\n8 8 1\n', '9')],
    'example-37': [('5 4\n5 1 5 3 2\n1 5 3\n2 4 2\n3 3 1\n1 5 5\n', '3 3 5 5'), ('1 1\n0\n1 1 1\n', '0')],
    'example-38': [('5 3\n5 1 5 3 2\n1 2\n1 3\n3 4\n3 5\n2 4 2\n7 5 2\n1 2 1\n', '3 3 1'), ('1 2\n7\n1 1 1\n6 1 1\n', '7 7')],
    'example-39': [('5\n1 2 3 4 0\n4\n3 5\n1 2\n5 5\n2 4\n', '7 3 0 7'), ('3\n8 8 1\n3\n2 2\n1 3\n3 3\n', '8 9 1')]
})
cases.update({
    'example-40': [('3\n2 3 7\n3 3 5\n1 1 2\n', '3 0 0'), ('2\n5 2 3\n4 4 7\n', '0 0')],
    'example-41': [('5 2 12\n', '10'), ('10 3 8\n', '0'), ('10 4 12\n', '6'), ('1000000000000000000 1 1000000\n', '0')],
    'example-42': [('4\n0 7\n2 7\n3 7\n1 3\n', '0 3 4 Hola! 1 2'), ('2\n4 5\n1 1000000007\n', '2 3 1 1000000006')],
    'example-43': [('5\n2\n4\n27\n15\n1000000007\n', 'Prime 2 3 5 Prime'), ('3\n1000000016000000063\n99991\n9998200081\n', '1000000009 Prime 99991')]
})
cases.update({
    'example-44': [('3 7 2 100\n1 2 3\n1 2\n2 3\n2 1 3\n1 1 3 5\n4 2\n3 1 4\n2 1 3\n4 1\n2 2 2\n', '6 21 25 10 7'), ('1 4 1 1\n8\n2 1 1\n1 1 1 3\n3 1 2\n4 1\n', '0 0')],
    'example-45': [('3 10\n1 2 4\n1 1 2\n1 2 3\n0 1 3\n3 2 8\n0 1 3\n2 1 3\n0 1 3\n2 2 3\n1 1 3\n0 2 3\n', '7 13 13 13'), ('1 3\n7\n0 1 1\n3 1 0\n0 1 1\n', '7 0')],
    'example-46': [('5\n1 2 1 3 2\n4\n1 5\n2 4\n3 3\n1 3\n', '3 3 1 2'), ('3\n9 9 9\n2\n1 3\n2 3\n', '1 1')]
})
cases.update({
    'example-47': [('2 7 4\n2 8 4\n2 8 3\n5 9 1\n0 0 0\n', '2 2 No Solution 0'), ('4 14 8\n3 1 8\n0 0 0\n', '3 0')],
    'example-48': [('3\n7 1\n8 1\n9 2\n', '2 3 5 0 2 5'), ('2\n2 2\n5 1\n', '1 2 2 3')],
    'example-49': [('10 2\n1 1\n0 1\n', '55'), ('5 1\n-1\n3\n', '998244350'), ('1 3\n2 3 4\n5 6 7\n', '6'), ('1000000000 1\n1\n9\n', '9')]
})
cases['example-50'] = [('4 9\n5 5 2 7\n1 1 2\n2 2\n2 1\n1 1 3\n1 2 3\n2 2\n2 3\n2 2\n2 2\n', '5 -1 2 -1 5 -1'), ('1 2\n7\n2 1\n2 1\n', '7 -1')]
cases.update({
    'example-51': [('1\n1 2\n3 4\n', '3 10'), ('2\n1 2 3 4\n5 6 7 8\n', '5 16 22 60')],
    'example-52': [('2 1\n1 2 3\n4 5\n', '4 13 22 15'), ('0 0\n9\n9\n', '81'), ('1 1\n0 0\n3 4\n', '0 0 0')],
    'example-53': [('4\n', '0 1 7 6 1'), ('1\n', '0 1'), ('5\n', '0 1 15 25 10 1')],
    'example-54': [('4\n', '0 6 11 6 1'), ('1\n', '0 1'), ('5\n', '0 24 50 35 10 1')]
})
cases.update({
    'example-55': [('4 5 1 4\n1 2 2 1\n1 3 1 3\n2 3 1 0\n2 4 1 2\n3 4 2 1\n', '3 9'), ('3 1 1 3\n1 2 5 7\n', '0 0'), ('2 2 1 2\n1 2 2 3\n1 2 1 1\n', '3 7')],
    'example-56': [('2 3\n0 1 3\n1 2 2\n0 2 1\n3\n0 1\n0 2\n1 2\n', '4 3 3'), ('1 2\n0 1 3\n0 1 4\n1\n0 1\n', '7'), ('2 1\n0 1 5\n2\n0 2\n0 1\n', '0 5')]
})
cases.update({
    'example-57': [('3 4\n1 3\n3 1\n1 2\n2 1\n', '1 2 1 3 1'), ('3 2\n1 2\n1 3\n', 'No'), ('2 3\n1 1\n1 2\n2 1\n', '1 1 2 1')],
    'example-58': [('6 5\n1 2\n2 3\n3 1\n3 4\n5 6\n', '1 3'), ('3 2\n1 2\n1 3\n', '1 1'), ('2 2\n1 2\n1 2\n', '0')],
    'example-59': [('4 5 2\n2 1 5\n2 3 1\n3 1 2\n1 4 3\n3 4 10\n', '3 0 1 6'), ('2 2 1\n1 2 8\n1 2 0\n', '0 0')]
})
cases.update({
    'example-60': [('3\n0 0\n3 4\n9 9\n', '5.0000'), ('2\n0 0\n1 1\n', '1.4142'), ('3\n4 5\n4 5\n8 9\n', '0.0000')],
    'example-61': [('1\n2 3\n', {'values': [0, 2, 3], 'atol': 1e-10}), ('3\n0 0\n6 0\n3 4\n', {'values': [3.125, 3, 0.875], 'atol': 1e-10}), ('3\n0 0\n2 0\n1 0.01\n', {'values': [1, 1, 0], 'atol': 1e-10}), ('2\n-10000 0\n10000 0\n', {'values': [10000, 0, 0], 'atol': 1e-10})],
    'example-62': [('3\n0 0\n1 1\n9 9\n', '2'), ('2\n-10000000 -10000000\n10000000 10000000\n', '800000000000000'), ('3\n2 7\n2 3\n2 4\n', '1')]
})
cases['example-63'] = [('3 6\n5 1 5\nQ 1 3 2\nC 2 7\nQ 1 3 2\nC 1 0\nQ 1 2 1\nQ 2 2 1\n', '5 5 0 7'), ('1 4\n9\nC 1 9\nQ 1 1 1\nC 1 1000000000\nQ 1 1 1\n', '9 1000000000')]
cases['example-64'] = [('3\n0\n3\n2 3\n2 3\n2 3\n4\n0 0\n1 1\n2 2\n1 1\n', '0 1 2 3 2 0 0 2 2'), ('1\n6\n0 0\n2 0\n2 2\n0 2\n1 0\n1 1\n', '4 0 0 2 0 2 2 0 2')]
cases['example-65'] = [('2\n3\n0 0\n3 4\n1 1\n2\n7 8\n7 8\n', {'diameter_cases': [[(0, 0), (3, 4), (1, 1)], [(7, 8), (7, 8)]]}), ('1\n4\n-1000000000 -1000000000\n-1000000000 1000000000\n1000000000 1000000000\n1000000000 -1000000000\n', {'diameter_cases': [[(-1000000000, -1000000000), (-1000000000, 1000000000), (1000000000, 1000000000), (1000000000, -1000000000)]]})]
associative_cases = [('6\n1 5\n0 5 7\n1 5\n0 5 9\n1 5\n1 6\n', '0 7 9 0'), ('4\n0 1000000000000000000 999999999999999999\n1 1000000000000000000\n0 0 0\n1 0\n', '999999999999999999 0')]
cases.update({
    'example-66': [('7\n0 -1 5\n0 0 7\n1 1\n1 0\n0 2 9\n1 4\n1 5\n', '5 5 7 9'), ('3\n0 -1 8\n1 0\n1 0\n', '8 8')],
    'example-67': [('2 10\n2 5\n2 1\n3 5\n4 4\n5 4\n0 2\n1 2\n2 2\n4 4\n5 6\n3 5\n', '2 2 2 5 -1 -1 -1 1'), ('0 4\n2 1\n4 7\n5 7\n3 7\n', '-1 -1 -1 0')],
    'example-68': associative_cases,
    'example-69': associative_cases
})
cases.update({
    'example-70': [('4\na\naa\na\nb\naaa\n', '3 2 3 0'), ('4\nhe\nshe\nhers\nhis\nahishers\n', '1 1 1 1')],
    'example-71': [('ababa\n', '9'), ('aaaa\n', '4'), ('abcbc\n', '12'), ('z\n', '1')]
})
cases.update({
    'example-72': [('4 4\n0 1\n1 2\n2 0\n2 3\n', {'matching': (4, [(0, 1), (1, 2), (2, 0), (2, 3)], 2)}), ('3 3\n0 1\n1 2\n2 0\n', {'matching': (3, [(0, 1), (1, 2), (2, 0)], 1)}), ('5 0\n', {'matching': (5, [], 0)})],
    'example-73': [('2 4\n1 1 1\n1 2 5\n2 1 6\n2 2 2\n', {'weighted_matching': [[1, 5], [6, 2]]}), ('2 2\n1 1 -1\n2 2 -4\n', {'weighted_matching': [[-1, None], [None, -4]]}), ('2 4\n1 1 7\n1 2 7\n2 1 7\n2 2 7\n', {'weighted_matching': [[7, 7], [7, 7]]})]
})
cases['example-74'] = [('3 3\n1 2 -2\n2 3 3\n1 3 5\n', '-1 1000000009 3000000000'), ('3 2\n2 3 -1\n3 2 0\n', '-1'), ('1 1\n1 1 0\n', '0')]
cases.update({
    'example-75': [('4\n2 3 7\n2 4 3\n4 6 2\n1 1 5\n', '1 2 1 2 1 -1 2 1 4 1 1 4 4'), ('2\n1000000000 999999999 1\n1 1 1000000000\n', '1 999999999 999999999 1 1 999999999 999999999')],
    'example-76': [('3 3 0\n1 2 2\n1 3 3\n2 3 5\n', '31'), ('3 4 1\n1 2 2\n1 3 3\n2 3 5\n3 2 7\n', '37'), ('2 1 1\n2 1 7\n', '0'), ('1 1 1\n1 1 9\n', '1')]
})
cases['example-77'] = [('2 4\n2 1\n1 1\n', '1'), ('2 8\n2 4\n1 2\n', '0'), ('0 7\n', '1'), ('2 1\n0 0\n0 0\n', '0'), ('2 1000000000\n1 2\n3 4\n', '999999998')]
cases['example-78'] = [('2 4\n2 1\n3 4\n1 0 2 5\n1 1 1 7\n0 0 1 0\n1 0 2 5\n', '37 7 19'), ('1 3\n0 8\n1 0 1 99\n0 0 998244352 1\n1 0 1 2\n', '8 998244352')]
cases['example-79'] = [('3 5\n1 2 3\n1 0 3\n0 0 2 2 1\n0 1 3 3 4\n1 0 3\n1 1 1\n', '6 35 0'), ('1 4\n5\n0 0 1 0 7\n0 0 1 2 3\n1 0 1\n1 0 0\n', '17 0')]
cases['example-80'] = [('3\n5 1 9\n2 6 3\n4 8 7\n', {'assignment': [[5, 1, 9], [2, 6, 3], [4, 8, 7]]}), ('2\n7 7\n7 7\n', {'assignment': [[7, 7], [7, 7]]}), ('1\n-1000000000\n', {'assignment': [[-1000000000]]})]
cases['example-81'] = [('8\n0 1 1 2 3 5 8 13\n', {'recurrence': ([0, 1, 1, 2, 3, 5, 8, 13], 2)}), ('0\n', {'recurrence': ([], 0)}), ('3\n0 0 0\n', {'recurrence': ([0, 0, 0], 0)}), ('3\n0 0 1\n', {'recurrence': ([0, 0, 1], 3)})]
cases['example-82'] = [('6 6 0\n0 1\n0 2\n1 3\n2 3\n3 4\n4 3\n', '0 0 0 0 3 -1'), ('3 2 2\n2 1\n1 0\n', '1 2 2'), ('1 1 0\n0 0\n', '0')]
cases['example-83'] = [('6 6\n1 2\n1 3\n2 4\n3 4\n4 5\n5 4\n', '5 1 1 2 1 0'), ('4 3\n1 2\n2 3\n3 4\n', '4 3 2 1'), ('1 1\n1 1\n', '1')]
cases['example-84'] = [('4 8\n0 -1 0 1\n0 0 1 2\n1 1 0 2\n1 0 0 2\n0 -1 2 3\n1 4 0 1\n1 4 2 3\n1 -1 3 3\n', '1 0 0 1 1'), ('2 4\n0 -1 0 0\n0 0 0 1\n1 0 0 1\n1 1 0 1\n', '0 1'), ('1 1\n0 -1 0 0\n', '')]
cases['example-85'] = [('6\n1\n2\n5\n10\n20\n10\n', '1 1 2 0 10 -2 32 -1 128 -3 32 -1')]
cases['example-86'] = [('1\n', '1'), ('10\n', '32'), ('20\n', '128')]
cases['example-87'] = [('1 6\n0 3 1 0\n1 0\n1 3\n0 2 5 -1 4\n1 2\n1 4\n1 5\n', '0 INFINITY 2 0 INFINITY'), ('1 1\n-1000000000 1000000000 1000000000 1000000000000000000\n1 999999999\n', '1999999999000000000'), ('1 1\n0 1 1 0\n0 1 2 1 0\n', '')]
cases['example-88'] = [('5\n0 1\n1 1 5 3 5\n0 2\n1 1 4 1 9\n0 1\n', '0 1 2'), ('3\n1 1 5 3 5\n1 3 5 1 5\n0 2\n', '1')]
cases['example-89'] = [('1 4\n1 0\n1 2\n0 -1 0\n1 2\n1 -2\n', '2 -2 -2'), ('1 1\n1000000000 1000000000000000000\n1 1000000000\n', '2000000000000000000'), ('1 1\n0 0\n0 1 2\n', '')]
cases['example-90'] = [('ababa\n', '9'), ('aaaa\n', '4'), ('a\n', '1')]
cases['example-91'] = [('ABABABA\nABA\n', '1 3 5 0 0 1'), ('AAAAA\nAAA\n', '1 2 3 0 1 2'), ('A\nAB\n', '0 0'), ('ABC\nD\n', '0')]
cases['example-92'] = [('3\nab\nb\nabc\nzabcab\n', '0 0 1 3 0 1'), ('0\nabc\n', '0 0 0'), ('2\naa\naaa\naaaa\n', '0 2 2 2')]
cases['example-93'] = [('1 1\n2\n1 5\n0 1 4\n1 1\n5\n1 5\n0 1 4\n', {'exact_text': '4\n\n-1\n\n'}), ('1 1\n0\n2 5\n0 1 3\n0 1 3\n', {'exact_text': '5\n\n'}), ('0 0\n', {'exact_text': '0\n\n'})]
cases['example-94'] = [('3 2 1 3\n1 2 1\n2 3 1\n', '1 0 1 0'), ('2 3 1 2\n1 2 2\n1 2 3\n1 1 1\n', '1 1 1 1 0 0')]
cases['example-95'] = [('2 2 3\n1 1\n1 2\n2 2\n', '2 1 1 0 0 1 1'), ('1 1 2\n1 1\n1 1\n', '1 1 0 1 0'), ('2 1 2\n1 1\n2 1\n', '1 1 0 1 0'), ('0 0 0\n', '0')]
cases['example-96'] = [('4 3\n1 2\n2 3\n3 4\n', {'odd_partition': (4, [(0,1),(1,2),(2,3)])}), ('4 3\n1 2\n1 3\n1 4\n', {'odd_partition': (4, [(0,1),(0,2),(0,3)])}), ('3 3\n1 2\n2 3\n3 1\n', {'odd_partition': (3, [(0,1),(1,2),(2,0)])}), ('0 0\n', {'odd_partition': (0, [])})]
cases['example-97'] = [('4 4 1 4 4\n1 2 1\n2 3 1\n2 3 1\n3 4 1\n1 2 3 4\n', '1 Y??Y'), ('3 3 1 3 2\n1 2 1\n2 3 0\n2 2 1\n1 3\n', '0 N?'), ('2 1 1 2 0\n1 2 2\n', {'exact_text': '2\n\n'})]
cases['example-98'] = [('4 4 1 4\n1 4 2 3\n2 3 2 -4\n3 2 1 1\n2 2 2 -3\n', '2 -3'), ('3 1 1 3\n2 2 5 -2\n', '0 -10'), ('2 2 1 2\n1 2 2 -3\n1 2 1 4\n', '3 -2')]
cases['example-99'] = [('2 1 1 2\n1 2 2 5\n', 'YES 2 2'), ('2 1 1 2\n2 1 0 3\n', 'YES -3 3'), ('3 1 1 3\n1 2 1 1\n', 'NO')]
ap = argparse.ArgumentParser()
ap.add_argument('--only', nargs='+')
args = ap.parse_args()
rows = records()
assert {r['id'] for r in rows} == set(cases), 'Every registered example needs execution cases'
proof_path = root / 'verification/usage-examples.json'
proof = json.loads(proof_path.read_text()) if args.only else {}
selected = set(args.only) if args.only else set(cases)
assert selected <= set(cases)
(root / 'build').mkdir(parents=True, exist_ok=True)
completed = set()
for row in rows:
    assert (root / row['snippet_file']).read_text() == row['snippet'], 'Regenerate printed usage first'
    if row['id'] not in selected:
        assert proof.get(row['id'], {}).get('program_sha256') == row['program_sha256'], 'Unselected example became stale'
        assert proof[row['id']].get('modes') == ['normal', 'sanitizer']
        continue
    source = root / ('build/usage-' + row['id'] + '.cpp')
    source.write_text(row['program'])
    for mode in ['normal', 'sanitizer']:
        flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined']
        exe = root / ('build/usage-' + row['id'] + '-' + mode)
        subprocess.run([CXX, '-std=c++20', *flags, str(source), '-o', str(exe)], check=True)
        for data, expected in cases[row['id']]:
            run = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
            assert not run.stderr, run.stderr
            check_output(row['id'], mode, data, run.stdout, expected)
    proof[row['id']] = dict(program_sha256=row['program_sha256'], modes=['normal', 'sanitizer'],
                           cases_per_mode=len(cases[row['id']]), driver=row['driver'],
                           scope='Printed usage execution only; no new online AC or comprehensive algorithm proof')
    completed.add(row['id'])
assert completed == selected, 'Not every selected example was executed'
(root / 'verification/usage-examples.json').write_text(json.dumps(proof, indent=2) + '\n')
print(f'Usage examples: {len(selected)} exact printed usage programs in normal and ASan/UBSan modes PASS; {len(proof)} current program records')
