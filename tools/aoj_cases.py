#!/usr/bin/env python3
"""Run a registered printed program on public AOJ data, using a local comparator."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

from usage_examples import records
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compare(actual, expected, tolerance):
    a, b = actual.split(), expected.split()
    if len(a) != len(b):
        return False
    try:
        for x, y in zip(a, b):
            x, y = Decimal(x), Decimal(y)
            if not x.is_finite() or not y.is_finite():
                return False
            if (tolerance == 0 and x != y) or (tolerance > 0 and abs(x - y) >= tolerance):
                return False
    except ArithmeticError:
        return False
    return True


def fetch(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return response.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--usage', required=True)
    ap.add_argument('--atol', required=True, type=Decimal)
    ap.add_argument('--sanitizer', action='store_true')
    ap.add_argument('--report', required=True)
    args = ap.parse_args()
    assert args.atol.is_finite() and args.atol >= 0
    r = next(x for x in records() if x['id'] == args.usage)
    assert r['problem'].startswith('AOJ ')
    pid = r['problem'].split()[1]
    assert pid.replace('_', '').isalnum()
    base = 'https://judgedat.u-aizu.ac.jp/testcases/' + pid
    cache = ROOT / 'build' / 'aoj-data' / pid
    cache.mkdir(parents=True, exist_ok=True)
    raw = fetch(base + '/header')
    refresh = not (cache / 'header.json').exists() or (cache / 'header.json').read_bytes() != raw
    (cache / 'header.json').write_bytes(raw)
    header = json.loads(raw)
    assert header['problemId'] == pid and header['headers']
    assert len({x['serial'] for x in header['headers']}) == len(header['headers'])

    def download(case):
        serial = case['serial']
        assert isinstance(serial, int) and serial > 0
        paths = []
        for ext, field in [('in', 'inputSize'), ('out', 'outputSize')]:
            path = cache / f'{serial}.{ext}'
            if refresh or not path.exists() or len(path.read_bytes()) != case[field]:
                path.write_bytes(fetch(f'{base}/{serial}/{ext}'))
            data = path.read_bytes()
            assert b'terminated because of the limitation' not in data
            paths.append(path)
        sizes = {ext: dict(declared=case[field], received=len(path.read_bytes()))
                 for path, (ext, field) in zip(paths, [('in', 'inputSize'), ('out', 'outputSize')])}
        confirmation = None
        if any(x['declared'] != x['received'] for x in sizes.values()):
            url = f'{base}/{serial}'
            alternate = fetch(url)
            parsed = json.loads(alternate)
            assert parsed['problemId'] == pid and parsed['serial'] == serial
            for path, key in zip(paths, ['in', 'out']):
                assert parsed[key].encode() == path.read_bytes(), (pid, serial, key, sizes)
            confirmation = dict(url=url, sha256=sha(alternate),
                                scope='Header sizes differ; raw and JSON official endpoints agree byte for byte, with no truncation marker.')
        return case, paths, sizes, confirmation

    with ThreadPoolExecutor(max_workers=4) as pool:
        cases = list(pool.map(download, header['headers']))
    print(pid, 'downloaded', len(cases), 'complete public cases', flush=True)
    mode = 'sanitizer' if args.sanitizer else 'normal'
    stem = ROOT / 'build' / f'aoj-{args.usage}-{mode}'
    src = stem.with_suffix('.cpp')
    src.write_text(r['program'])
    flags = ['-O1', '-g', '-fsanitize=address,undefined'] if args.sanitizer else ['-O2']
    subprocess.run([CXX, '-std=c++20', *flags, str(src), '-o', str(stem)], check=True)
    assert compare('1 2', '1 2', args.atol)
    assert not compare('1000000 2', '1 2', args.atol)
    assert not compare('nan', '0', args.atol)
    assert not compare('0 1', '0', args.atol)
    results = []
    for case, (inp, ans), sizes, confirmation in cases:
        result = subprocess.run([str(stem)], input=inp.read_bytes(), capture_output=True, timeout=60, check=True)
        assert not result.stderr, result.stderr.decode(errors='replace')
        actual, expected = result.stdout.decode(), ans.read_text()
        assert compare(actual, expected, args.atol), (pid, case['serial'], actual[:200], expected[:200])
        results.append(dict(serial=case['serial'], name=case['name'], sizes=sizes,
                            size_mismatch_confirmation=confirmation, input_sha256=sha(inp.read_bytes()),
                            expected_sha256=sha(ans.read_bytes()), actual_sha256=sha(result.stdout),
                            verdict='local_comparator_accepted'))
    report = dict(problem=pid, usage=args.usage, mode=mode, driver=r['driver'], program_sha256=r['program_sha256'],
                  scope='Complete public AOJ data from official API, checked with a local numeric comparator; not the official checker, not online AC or a speed rank.',
                  fetched_at_utc=datetime.now(timezone.utc).isoformat(), header_url=base+'/header', header_sha256=sha(raw),
                  comparator=dict(type='absolute error strictly below threshold; exact numeric equality if threshold zero', atol=str(args.atol),
                                  negative_controls='wrong value, NaN and wrong token count rejected'),
                  test_sha256=sha(Path(__file__).read_bytes()), compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
                  flags=flags, cases=results)
    (ROOT / args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(pid, mode, len(results), 'public cases PASS with local comparator', flush=True)


if __name__ == '__main__':
    with localcontext() as ctx:
        ctx.prec = 70
        main()
