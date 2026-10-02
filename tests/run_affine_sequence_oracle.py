#!/usr/bin/env python3
"""Independent affine-sequence oracle, opt-in scale, source-bound JSON receipts.
SANITIZE=1 or CPC_SANITIZE=1 enables ASan+UBSan. No automatic sanitizer retry.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--max', action='store_true', help='500000 initial nodes and 500000 queries instead of small oracle suite')
parser.add_argument('--receipt', type=Path)
args = parser.parse_args()
truth = {'1', 'true', 'yes', 'on'}
san = any(os.environ.get(name, '').lower() in truth for name in ('SANITIZE', 'CPC_SANITIZE'))
mode = ('sanitizer' if san else 'normal') + ('-max' if args.max else '-small')
receipt = args.receipt or ROOT / 'build' / ('affine-sequence-oracle-' + mode + '.json')
receipt.parent.mkdir(parents=True, exist_ok=True)
(ROOT / 'build').mkdir(exist_ok=True)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def sources():
    # Follow quoted local includes, rather than hashing unrelated compact headers.
    pending = [ROOT / 'tests' / 'affine_sequence_oracle.cpp',
               ROOT / 'verify' / 'library_checker' / 'dynamic_sequence_range_affine_range_sum.compact.cpp']
    paths = {Path(__file__).resolve()}
    while pending:
        path = pending.pop().resolve()
        if path in paths:
            continue
        path.relative_to(ROOT)  # Reject dependencies outside the project root.
        paths.add(path)
        for include in re.findall(r'^\s*#\s*include\s*"([^"\n]+)"', path.read_text(), re.MULTILINE):
            dependency = (path.parent / include).resolve()
            if not dependency.is_file():
                raise RuntimeError('missing local include: ' + str(dependency))
            pending.append(dependency)
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}

cxx = shlex.split(os.environ.get('CXX', 'c++'))
flags = ['-std=c++20', '-Wall', '-Wextra', '-Wpedantic']
flags += (['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-sanitize-recover=all'] if san else ['-O2'])
exe = ROOT / 'build' / ('affine_sequence_oracle-' + mode)
cmd = cxx + flags + [str(ROOT / 'tests' / 'affine_sequence_oracle.cpp'), '-o', str(exe)]
env = os.environ.copy()
if san:
    env.setdefault('ASAN_OPTIONS', 'detect_leaks=1:halt_on_error=1')
    env.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
r = {'schema': 1, 'status': 'running', 'mode': mode,
     'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'source_sha256_before': sources(), 'compile_command': cmd,
     'compiler_version': subprocess.check_output(cxx + ['--version'], text=True),
     'compiler_executable_sha256': digest(Path(shutil.which(cxx[0]))),
     'sanitizer_environment': {k: env.get(k) for k in ['SANITIZE','CPC_SANITIZE','ASAN_OPTIONS','UBSAN_OPTIONS']},
     'scope': 'core template oracle only; driver hash recorded but driver not exercised by this test',
     'large_case': {'initial_nodes': 500000, 'queries': 500000} if args.max else None}
started = time.monotonic()
try:
    build = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    r['compile'] = {'returncode': build.returncode, 'stdout': build.stdout, 'stderr': build.stderr}
    if build.returncode:
        raise RuntimeError('compile failed')
    r['binary_sha256'] = digest(exe)
    run_cmd = [str(exe)] + (['--max'] if args.max else [])
    r['run_command'] = run_cmd
    run = subprocess.run(run_cmd, capture_output=True, text=True, env=env, timeout=600)
    r['run'] = {'returncode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}
    if run.returncode or run.stderr or not run.stdout.startswith('PASS affine sequence independent oracle; checks='):
        raise RuntimeError('oracle failed or emitted diagnostics')
    r['source_sha256_after'] = sources()
    if r['source_sha256_before'] != r['source_sha256_after']:
        raise RuntimeError('source changed during verification')
    r['status'] = 'passed'
except Exception as exc:
    r['status'] = 'failed'
    r['error'] = repr(exc)
    raise
finally:
    r['elapsed_seconds'] = round(time.monotonic() - started, 3)
    r['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt.write_text(json.dumps(r, indent=2) + '\n')
print(r['run']['stdout'].strip())
print('Receipt:', receipt)
