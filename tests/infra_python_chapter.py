import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = sorted((root / 'examples/infra').glob('python_*.py'))
outputs = {}
for file in files:
    data = '4\n-5 8\n3 -2\n' if file.stem == 'python_io' else ''
    r = subprocess.run([sys.executable, str(file)], input=data, text=True,
                       capture_output=True, check=True, timeout=15)
    assert not r.stderr
    outputs[file.name] = r.stdout
assert outputs['python_io.py'] == '4\n-5 8 3 -2\n'
assert outputs['python_table.py'].splitlines()[-1] == '10 144'
# Independently exercise documented failures in a fresh interpreter.
failure_cases = [
    ('pow(2, -1, 4)', 'ValueError'),
    ('import sys; sys.set_int_max_str_digits(640); str(10**640)', 'ValueError'),
    ('from decimal import Decimal; assert Decimal(0.1) != Decimal("0.1")', None),
    ('a = [[0] * 2] * 3; a[0][0] = 7; assert a[2][0] == 7', None),
]
for code, error in failure_cases:
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
    assert (r.returncode != 0) == bool(error)
    if error:
        assert error in r.stderr
report = dict(status='pass', python=sys.version, platform=platform.platform(),
              outputs=outputs, failure_checks=len(failure_cases),
              source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [*files, Path(__file__)]},
              scope='Runs the six exact printed Python sources plus four semantic checks; no Python/PyPy performance ranking.')
(root / 'verification/infra-python-chapter.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Six printed Python programs and four semantic checks PASS')
