#!/usr/bin/env python3
"""Check example-213 against the clean, pinned Library Checker corpus.

Unlike the generic official_cases.py, this focused receipt records Linux wait4
peak RSS, explicit sanitizer settings, and partial/failed attempts. Run prepare,
then normal and sanitizer. Outputs remain local evidence, never an online AC.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import tomllib

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / 'build/library-checker-problems-multipoint'
PROBLEM = 'convolution_mod_1000000007'
FOLDER = UP / 'convolution' / PROBLEM
PIN = 'e64660561a995c357cdc61ddee1bde68b80528db'
DRIVER = 'verify/library_checker/convolution_mod_1000000007.garner.compact.cpp'
USAGE = 'example-213'
CXX = os.environ.get('CXX') or shutil.which('g++-16') or 'g++'
DIAGNOSTIC = re.compile(r'ERROR: (?:AddressSanitizer|LeakSanitizer)|runtime error:|SUMMARY: (?:AddressSanitizer|UndefinedBehaviorSanitizer)|AddressSanitizer:DEADLYSIGNAL')


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def reference():
    commit = subprocess.check_output(['git', '-C', str(UP), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == PIN, commit
    assert not subprocess.check_output(['git', '-C', str(UP), 'diff', 'HEAD', '--']), 'Modified tracked upstream source'
    assert not subprocess.check_output(['git', '-C', str(UP), 'ls-files', '--others', '--exclude-standard']), 'Unexpected upstream files'
    meta = tomllib.loads((FOLDER / 'info.toml').read_text())
    expected = {f"{Path(t['name']).stem}_{i:02d}" for t in meta['tests'] for i in range(t['number'])}
    assert len(expected) == 48
    assert {p.stem for p in (FOLDER / 'in').glob('*.in')} == expected
    assert {p.stem for p in (FOLDER / 'out').glob('*.out')} == expected
    manifest = json.loads((FOLDER / 'hash.json').read_text())
    actual = {p.name: sha(p) for ext, part in [('in', 'in'), ('out', 'out')]
              for p in (FOLDER / part).glob('*.' + ext)}
    assert actual == manifest, 'Pinned input/answer hashes differ'
    return meta, sorted(expected), actual


def prepare():
    command = [sys.executable, str(UP / 'generate.py'), '-p', PROBLEM]
    log = ROOT / 'build/garner-upstream-generate.log'
    with log.open('wb') as f:
        run(command, stdout=f, stderr=subprocess.STDOUT)
    meta, names, hashes = reference()
    flags = ['-O2', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-Wno-unused-result', '-I', str(UP / 'common')]
    run([CXX, *flags, str(FOLDER / 'verifier.cpp'), '-o', str(FOLDER / 'verifier')])
    cases = []
    for name in names:
        with (FOLDER / 'in' / (name + '.in')).open('rb') as f:
            n, m = map(int, f.readline().split())
        with (FOLDER / 'in' / (name + '.in')).open('rb') as f:
            result = run([str(FOLDER / 'verifier')], stdin=f, capture_output=True, timeout=30)
        cases.append(dict(case=name, n=n, m=m, input_sha256=hashes[name + '.in'],
                          answer_sha256=hashes[name + '.out'], pinned_hash_manifest_match=True,
                          official_input_verifier_exit_code=result.returncode))
    tracked = subprocess.check_output(['git', '-C', str(UP), 'ls-files', 'generate.py', 'common', 'convolution/' + PROBLEM], text=True).splitlines()
    report = dict(problem=PROBLEM, scope='Pinned local official corpus provenance; not online submission or AC',
                  repository='https://github.com/yosupo06/library-checker-problems', reference_commit=PIN,
                  checkout=str(UP.relative_to(ROOT)), reference_tracked_files_unmodified=True,
                  acquisition='Reused clean pinned public checkout; no credentials or network used',
                  generator_command=command, generator_exit_code=0, generator_log=str(log.relative_to(ROOT)),
                  generator_log_sha256=sha(log), source_sha256={p: sha(UP / p) for p in tracked},
                  compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
                  metadata_case_count=len(names), pinned_manifest_matched_files=len(hashes),
                  helper_sha256=sha(__file__), preparation_attempt_receipt='verification/garner-official-preparation-attempts.json',
                  constraints=dict(min_length=1, max_length=meta['params']['N_AND_M_MAX'], modulus=meta['params']['MOD'],
                                   coefficient_min=0, coefficient_max=meta['params']['MOD'] - 1),
                  official_normal_time_limit_seconds=meta['timelimit'], input_validation='All 48 inputs accepted by actual upstream verifier',
                  verifier_binary_sha256=sha(FOLDER / 'verifier'), checker_binary_sha256=sha(FOLDER / 'checker'),
                  recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=cases)
    write(ROOT / 'verification/garner-official-provenance.json', report)
    print('48 generated cases, 96 pinned hashes, 48 official input validations PASS', flush=True)


def measured(command, inp, output, error, timeout, env):
    """wait4 returns this individual child rusage, not cumulative children RSS."""
    start = time.monotonic()
    timed_out = False
    with inp.open('rb') as fi, output.open('wb') as fo, error.open('wb') as fe:
        proc = subprocess.Popen(command, stdin=fi, stdout=fo, stderr=fe, env=env)
        while True:
            pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start > timeout:
                timed_out = True
                proc.kill()
                _, status, usage = os.wait4(proc.pid, 0)
                break
            time.sleep(0.005)
        proc.returncode = os.waitstatus_to_exitcode(status)
    return dict(exit_code=proc.returncode, timeout=timed_out,
                elapsed_seconds=round(time.monotonic() - start, 6),
                user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
                resident_bytes=int(usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024)))


def check(mode, timeout, profile, attempt):
    from usage_examples import records
    meta, names, hashes = reference()
    row = next(r for r in records() if r['id'] == USAGE)
    assert row['driver'] == DRIVER
    work = ROOT / 'build/garner-official' / (mode + '-' + attempt)
    work.mkdir(parents=True, exist_ok=False)
    program = work / 'main.cpp'
    program.write_text(row['program'])
    assert sha(program) == row['program_sha256']
    flags = ['-std=c++20', '-O2']
    env = os.environ.copy()
    for key in ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS'):
        env.pop(key, None)
    if mode == 'sanitizer':
        flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        env['ASAN_OPTIONS'] = 'detect_leaks=0:halt_on_error=1'
        if profile == 'bounded':
            env['ASAN_OPTIONS'] += ':quarantine_size_mb=32:thread_local_quarantine_size_kb=128'
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    exe = work / 'main'
    report_path = ROOT / 'verification' / ('garner-official-usage-' + mode + ('-' + attempt if attempt != 'first' else '') + '.json')
    assert not report_path.exists(), 'Do not overwrite earlier attempt; provide a new --attempt'
    report = dict(problem=PROBLEM, scope='Local official generated cases only; not online AC or controlled OJ speed ranking',
                  reference_commit=PIN, reference_problem_path=str(FOLDER.relative_to(UP)),
                  reference_tracked_files_unmodified=True, metadata_sha256=sha(FOLDER / 'info.toml'),
                  checker_source_sha256=sha(FOLDER / 'checker.cpp'), checker_binary_sha256=sha(FOLDER / 'checker'),
                  driver=DRIVER, driver_sha256=sha(ROOT / DRIVER), usage=USAGE,
                  program_sha256=sha(program), bundle_sha256=sha(program),
                  compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0], flags=flags,
                  mode=mode, sanitizer_profile=profile if mode == 'sanitizer' else None,
                  sanitizer_environment={k: env[k] for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS') if k in env},
                  leak_sanitizer='Excluded: detect_leaks=0' if mode == 'sanitizer' else 'Not enabled',
                  per_case_timeout_seconds=timeout, official_normal_time_limit_seconds=meta['timelimit'],
                  timing_scope='Per-process local wall/CPU timings; no OJ hardware equivalence or speed ranking',
                  memory_method='POSIX wait4 per-child ru_maxrss, Linux KiB converted to bytes; no cumulative child peak',
                  attempt=attempt, helper_sha256=sha(__file__), invocation=sys.argv, status='compiling', recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=[])
    write(report_path, report)
    try:
        run([CXX, *flags, str(program), '-o', str(exe)])
        report['executable_sha256'] = sha(exe)
        wrong = work / 'negative-control.out'
        wrong.write_text('not-a-valid-answer\n')
        first = names[0]
        negative = subprocess.run([str(FOLDER / 'checker'), str(FOLDER / 'in' / (first + '.in')), str(wrong),
                                   str(FOLDER / 'out' / (first + '.out'))], capture_output=True, text=True, timeout=30)
        report['negative_control'] = dict(description='Deliberately wrong output rejected by actual official checker',
                                          exit_code=negative.returncode, message=negative.stderr.strip())
        assert negative.returncode in (1, 2), report['negative_control']
        report['status'] = 'running'
        write(report_path, report)
        for name in names:
            inp, ans = FOLDER / 'in' / (name + '.in'), FOLDER / 'out' / (name + '.out')
            actual, error = work / (name + '.out'), work / (name + '.err')
            result = measured([str(exe)], inp, actual, error, timeout, env)
            result.update(case=name, input_sha256=hashes[name + '.in'], answer_sha256=hashes[name + '.out'],
                          output_sha256=sha(actual), stderr=error.read_text(), verdict='not_accepted')
            report['cases'].append(result)
            write(report_path, report)
            assert result['exit_code'] == 0 and not result['timeout'], result
            assert not DIAGNOSTIC.search(result['stderr']), result
            checked = subprocess.run([str(FOLDER / 'checker'), str(inp), str(actual), str(ans)],
                                     capture_output=True, text=True, timeout=30)
            result.update(checker_exit_code=checked.returncode, checker_message=checked.stderr.strip())
            assert checked.returncode == 0, result
            result['verdict'] = 'local_checker_accepted'
            write(report_path, report)
            print(f"{mode} {name}: PASS {result['elapsed_seconds']:.3f}s {result['resident_bytes']/1048576:.1f} MiB", flush=True)
        assert sha(ROOT / DRIVER) == report['driver_sha256'], 'Driver changed while running'
        current = next(r for r in records() if r['id'] == USAGE)
        assert current['program_sha256'] == report['program_sha256'], 'Printed program changed while running'
        reference()
        report.update(status='passed', passed_cases=len(report['cases']),
                      max_local_elapsed_seconds=max(r['elapsed_seconds'] for r in report['cases']),
                      max_resident_bytes=max(r['resident_bytes'] for r in report['cases']),
                      finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    except BaseException as exc:
        report.update(status='failed', failure=repr(exc), finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        raise
    finally:
        write(report_path, report)
    print(f'{mode}: all 48 exact printed official checks PASS; not online AC', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'normal', 'sanitizer'])
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('--profile', choices=['default', 'bounded'], default='default')
    parser.add_argument('--attempt', default='first', help='Unique receipt/work suffix; failed attempts are never overwritten')
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9_-]+', args.attempt)
    assert args.timeout > 0
    if args.mode == 'prepare':
        prepare()
    else:
        check(args.mode, args.timeout, args.profile, args.attempt)
