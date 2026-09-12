"""Check P5491's root list ordering, single zero root and Hola! protocol."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
cases, expected = [], []
for p in [3, 5, 7, 17, 97, 257]:
    roots = [[] for _ in range(p)]
    for x in range(p):
        roots[x * x % p].append(x)
    for a in range(p):
        cases.append((a, p))
        expected.append(' '.join(map(str, roots[a])) if roots[a] else 'Hola!')
text = str(len(cases)) + '\n' + ''.join(f'{a} {p}\n' for a, p in cases)
for style in ['compact']:
    source = root / f'build/P5491.{style}.cpp'
    exe = root / f'build/P5491.{style}'
    subprocess.run(['python3', str(root / 'tools/bundle.py'),
                    str(root / f'verify/luogu/P5491.{style}.cpp'), str(source)], check=True)
    subprocess.run(['/opt/homebrew/bin/g++-16', '-std=c++20', '-O2', str(source), '-o', str(exe)], check=True)
    got = subprocess.check_output([str(exe)], input=text.encode()).decode().splitlines()
    assert got == expected
    print(f'P5491 {style} bundled driver / exhaustive roots and output protocol PASS')
