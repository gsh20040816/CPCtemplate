#!/usr/bin/env python3
"""Source-bound static ModInt unit checks in full and minimal copied contexts."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import shutil
import subprocess
import tempfile
import time
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None, '', '0'):
        raise SystemExit('Validation requires Python assertions')
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['normal', 'sanitizer'], default='sanitizer' if os.environ.get('CPC_SANITIZE', os.environ.get('SANITIZE', '0')) == '1' else 'normal')
    args = parser.parse_args()
    mode = args.mode
    directory = Path(tempfile.mkdtemp(prefix=f'static-modint-{mode}-', dir=ROOT / 'build'))
    report = {'schema': 'cpc-static-modint-units-v1', 'status': 'running', 'mode': mode,
              'scope': 'Current static type, minimal printed class, valid release use, explicit rejected preconditions; not a full suite or online AC',
              'directory': str(directory), 'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'commands': [], 'contexts': [], 'benchmarks': [], 'failures': []}
    path = directory / 'report.json'
    files = [ROOT / 'tests/static_modint.cpp', Path(__file__), ROOT / 'tests/compiler_config.py', ROOT / 'docs/generated.tex', ROOT / 'docs/catalog.json'] + sorted((ROOT / 'src').rglob('*.hpp'))
    before = {str(p.relative_to(ROOT)): sha(p) for p in files}
    report['source_sha256_before'] = before
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    frontend = Path(subprocess.check_output([str(compiler), '-print-prog-name=cc1plus'], text=True).strip()).resolve()
    report['compiler'] = {'path': str(compiler), 'sha256_before': sha(compiler), 'frontend': str(frontend), 'frontend_sha256_before': sha(frontend), 'version': subprocess.check_output([str(compiler), '--version'], text=True).splitlines()[0]}
    report['environment'] = {k: os.environ.get(k) for k in ['ASAN_OPTIONS', 'UBSAN_OPTIONS', 'CPLUS_INCLUDE_PATH']}
    report['leak_sanitizer_claim'] = False
    flags = ['-std=c++20', '-O2'] if mode == 'normal' else ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']

    def no_core():
        _, hard = resource.getrlimit(resource.RLIMIT_CORE)
        resource.setrlimit(resource.RLIMIT_CORE, (0, hard))

    def run(label, argv, expected=0, core=False, timeout=240):
        start = time.monotonic()
        p = subprocess.run([str(x) for x in argv], text=True, capture_output=True, timeout=timeout, preexec_fn=no_core if core else None)
        stdout, stderr = directory / f'{label}.stdout', directory / f'{label}.stderr'
        stdout.write_text(p.stdout); stderr.write_text(p.stderr)
        report['commands'].append({'label': label, 'argv': [str(x) for x in argv], 'returncode': p.returncode, 'expected_returncode': expected, 'elapsed_seconds': time.monotonic() - start, 'stdout': str(stdout), 'stdout_sha256': sha(stdout), 'stderr': str(stderr), 'stderr_sha256': sha(stderr), 'output': p.stdout, 'diagnostics': p.stderr})
        assert p.returncode == expected, (label, p.returncode, p.stderr[-3000:])
        return p

    try:
        source = (ROOT / 'src/compact/number_theory.hpp').read_text()
        code = re.search(r'template <int mod> struct ModInt\n\{.*?\n\};', source, re.S).group(0)
        printed = (ROOT / 'docs/generated.tex').read_text().split(r'\label{compact-ModInt}', 1)[1].split(r'\label{compact-', 1)[0]
        listings = list(re.finditer(r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,firstnumber=(\d+))?\]\{\.\./src/compact/number_theory.hpp\}', printed))
        assert listings
        ranges = [(int(m[1]), int(m[2])) for m in listings]
        assert all(ranges[i - 1][1] + 1 == ranges[i][0] for i in range(1, len(ranges)))
        for match in listings:
            if match[3]: assert int(match[3]) == int(match[1]) - ranges[0][0] + 1
        actual = '\n'.join(line for lo, hi in ranges for line in source.splitlines()[lo-1:hi])
        assert actual.rstrip('\n') == code, 'printed listings differ from complete current class'
        report['printed_listing_ranges'] = ranges
        report['printed_listing_sha256'] = hashlib.sha256(actual.encode()).hexdigest()
        minimal = directory / 'minimal.hpp'
        minimal.write_text('#include <cassert>\n#include <optional>\n#include <utility>\nusing namespace std;\n' + code + '\n')
        report['minimal_header_sha256'] = sha(minimal)
        report['class_sha256'] = hashlib.sha256(code.encode()).hexdigest()
        for context in ['full_header', 'minimal_standard', 'minimal_ndebug']:
            exe = directory / context
            extra = [] if context == 'full_header' else ['-DSTATIC_MODINT_MINIMAL', '-include', str(minimal), '-pedantic-errors']
            if context == 'minimal_ndebug': extra.append('-DNDEBUG')
            run(context + '-compile', [compiler, *flags, *extra, ROOT / 'tests/static_modint.cpp', '-o', exe], timeout=360)
            result = run(context + '-run', [exe])
            assert not result.stderr and 'PASS' in result.stdout
            report['contexts'].append({'name': context, 'binary_sha256': sha(exe), 'passed': True})
            if context != 'minimal_ndebug':
                parent_limits = resource.getrlimit(resource.RLIMIT_CORE)
                rejected = run(context + '-reject', [exe, 'reject'], expected=-signal.SIGABRT, core=True)
                assert 'Assertion' in rejected.stderr and resource.getrlimit(resource.RLIMIT_CORE) == parent_limits
            for repeat in range(3):
                result = run(f'{context}-benchmark-{repeat}', [exe, 'benchmark'])
                assert not result.stderr
                m = re.fullmatch(r'benchmark_us (\d+) (\d+) checksum (\d+)\n', result.stdout)
                assert m
                report['benchmarks'].append({'context': context, 'repeat': repeat, 'fermat_us': int(m[1]), 'euclid_us': int(m[2]), 'checksum': int(m[3]), 'scope': '200000 fixed nonzero prime residues; local timing, no general performance guarantee'})
        for modulus in [0, -1, 1]:
            probe = directory / f'modulus-{modulus}.cpp'
            probe.write_text(f'#include "minimal.hpp"\nint main() {{ ModInt<{modulus}> a; return a.try_inv().has_value() ? 0 : 1; }}\n')
            exe = directory / f'modulus-{modulus}'
            result = run(f'modulus-{modulus}-compile', [compiler, '-std=c++20', '-O2', '-pedantic-errors', probe, '-o', exe], expected=0 if modulus == 1 else 1)
            if modulus == 1: run('modulus-one-control', [exe])
            else: assert 'static assertion failed' in result.stderr
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'; report['failures'].append(repr(error)); raise
    finally:
        report['source_sha256_after'] = {str(p.relative_to(ROOT)): sha(p) for p in files}
        report['compiler']['sha256_after'] = sha(compiler)
        report['compiler']['frontend_sha256_after'] = sha(frontend)
        report['inputs_unchanged'] = before == report['source_sha256_after'] and report['compiler']['sha256_before'] == sha(compiler) and report['compiler']['frontend_sha256_before'] == sha(frontend)
        if not report['inputs_unchanged']: report['status'] = 'failed'
        report['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        path.write_text(json.dumps(report, indent=2) + '\n')
        print(f'Static ModInt {mode}: {report["status"]}; receipt {path}', flush=True)
    assert report['status'] == 'passed'


if __name__ == '__main__':
    main()
