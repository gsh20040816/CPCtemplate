import math
import random
import subprocess
import tempfile
from pathlib import Path

assert (-3) // 2 == -2
assert pow(3, -1, 7) == 5
try:
    pow(2, -1, 4)
except ValueError:
    pass
else:
    raise AssertionError('non-invertible modular inverse must fail')
assert math.isqrt(10**30) == 10**15
assert math.isqrt(10**30 - 1) == 10**15 - 1
rng = random.Random(20260913)
assert 1 <= rng.randrange(1, 100) < 100

rows = [[0] for _ in range(2)]
alias = rows
shallow = rows[:]
rows[0][0] = 7
assert alias is rows and shallow is not rows
assert shallow[0][0] == 7 and rows[1][0] == 0

with tempfile.TemporaryDirectory(prefix='cpc-infra-') as tmp:
    path = Path(tmp)
    script = '''set -euo pipefail
name="file with spaces.txt"
printf '%s\\n' 'literal $value' > "$name"
cat < "$name"
'''
    result = subprocess.run(
        ['bash', '-c', script], cwd=path, text=True, capture_output=True, check=True
    )
    assert not result.stderr and result.stdout == 'literal $value\n'
    different = path / 'different.txt'
    different.write_text('different\n')
    result = subprocess.run(
        ['diff', '-u', 'file with spaces.txt', different.name],
        cwd=path, text=True, capture_output=True
    )
    assert result.returncode == 1 and not result.stderr
    result = subprocess.run(
        ['bash', '-c', 'set -euo pipefail\nfalse | cat\nprintf unreachable'],
        cwd=path, text=True, capture_output=True
    )
    assert result.returncode != 0 and not result.stdout

print('Infra Python/Bash examples: exact arithmetic, inverse failure, list aliases, '
      'quoted file paths, diff status and pipefail PASS')
