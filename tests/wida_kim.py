"""Audit the WIDA day-count weekday against datetime for years from 1970."""
import datetime, hashlib, os, random, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-kim.cpp').read_bytes()
fix = root / 'tests/fixtures/wida_kim'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.cpp').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '618ea300f6df6dd7f8b658fc1e931726a60fcf12'
text = blob.decode().replace('\r\n', '\n')
assert 'for (int i = 1970; i < y; i++)' in text
assert 'return (ans + 2) % 7 + 1;' in text

def month_days(y, m):
    nxt = datetime.date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    return (nxt - datetime.date(y, m, 1)).days

rng = random.Random(9)
dates = [(1970, 1, 1), (2000, 1, 1), (1900, 2, 28), (2000, 2, 29), (2024, 2, 29), (1969, 12, 31)]
for _ in range(40):
    y = rng.randrange(1970, 2100)
    m = rng.randrange(1, 13)
    d = rng.randrange(1, month_days(y, m) + 1)
    dates.append((y, m, d))
lines = [str(len(dates))] + [f'{y} {m} {d}' for y, m, d in dates]
payload = '\n'.join(lines) + '\n'
out = root / 'build/wida-kim'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
src = root / 'tests/wida_kim.cpp'
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe)], input=payload, text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == ''
    early = None
    checked = 0
    for row, (y, m, d) in zip(got.stdout.splitlines(), dates):
        leap, md, day = map(int, row.split())
        real = datetime.date(y, m, d)
        assert leap == int(real.year % 400 == 0 or (real.year % 4 == 0 and real.year % 100 != 0))
        assert md == month_days(y, m)
        expect = real.weekday() + 1
        if y >= 1970:
            assert day == expect
            checked += 1
        else:
            early = (y, m, d, day, expect)
            assert day != expect
    report.append(dict(mode=mode, checked=checked, early_mismatch=early))
    print(mode, checked, 'PASS', early, flush=True)
import json
(root / 'verification/wida-kim.json').write_text(json.dumps(dict(
    scope='Day count from 1970, not the closed Kim Larsen formula. Monday=1 through Sunday=7 for valid dates with year>=1970. Earlier years do not match the civil calendar. No online AC.',
    blob='618ea300f6df6dd7f8b658fc1e931726a60fcf12', runs=report), indent=2) + '\n')
