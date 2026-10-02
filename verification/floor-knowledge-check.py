#!/usr/bin/env python3
"""Reproducible TARGETED floor-sum check, deliberately not a full-suite receipt."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import runpy
import shlex
import shutil
import subprocess
import sys
import time
import traceback
import uuid

SCHEMA = 'cpc-targeted-floor-knowledge-v1'
PINNED_BASELINE = '1a9fa3e91d7dff58915341040be069611370054c'
CPP_TESTS = ('number_components', 'floor_sum', 'floor_moments', 'floor_moments_large')
APP_TEST = 'tests/floor_moments_application.py'
STACK_KIB = 524288


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def audit_python(script):
    # Observe actual subprocess commands in the unchanged application test.
    def hook(event, args):
        if event == 'subprocess.Popen':
            executable, argv, cwd, env = args
            print('TARGETED_SUBPROCESS ' + json.dumps({
                'executable': os.fsdecode(executable),
                'argv': [os.fsdecode(x) for x in argv],
                'cwd': str(Path(cwd or os.getcwd()).resolve()),
                'environment_source': 'inherited' if env is None else 'explicit',
            }, sort_keys=True), flush=True)
    sys.addaudithook(hook)
    path = Path(script).resolve()
    sys.argv = [str(path)]
    sys.path.insert(0, str(path.parent))
    runpy.run_path(str(path), run_name='__main__')


def limit_stack():
    soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
    target = STACK_KIB * 1024
    if hard != resource.RLIM_INFINITY:
        target = min(target, hard)
    resource.setrlimit(resource.RLIMIT_STACK, (target, hard))
    actual_soft, actual_hard = resource.getrlimit(resource.RLIMIT_STACK)
    def kib(value):
        return 'unlimited' if value == resource.RLIM_INFINITY else value // 1024
    os.write(1, ('TARGETED_STACK ' + json.dumps({
        'requested_kib': STACK_KIB, 'inherited_soft_kib': kib(soft),
        'actual_soft_kib': kib(actual_soft), 'hard_kib': kib(actual_hard),
        'hard_limit_unchanged': actual_hard == hard,
    }, sort_keys=True) + '\n').encode())


def boost_snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def run(mode, root, boost):
    sys.path.insert(0, str(root / 'tools'))
    import run_provenance as rp
    assert rp.BASELINE == PINNED_BASELINE
    compiler = Path(shutil.which('g++') or '/missing-g++').resolve(strict=True)
    frontend = Path(subprocess.check_output([str(compiler), '-print-prog-name=cc1plus'], text=True).strip()).resolve(strict=True)
    version = subprocess.check_output([str(compiler), '-dumpfullversion'], text=True).strip()
    assert version == '14.2.0', f'Expected GNU 14.2.0, got {version}'
    helper = Path(__file__).resolve()
    helper_before = sha(helper)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ-') + mode + '-' + uuid.uuid4().hex[:8]
    directory = root / 'build' / ('floor-knowledge-check-' + run_id)
    directory.mkdir(parents=True, exist_ok=False)
    stage = directory / 'stage'
    stage.mkdir()
    log_path = directory / 'output.txt'
    report_path = root / 'verification' / ('floor-knowledge-' + mode + '.json')
    env = {
        'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
        'HOME': os.environ.get('HOME', '/tmp'),
        'LC_ALL': 'C.UTF-8',
        'CXX': str(compiler),
        'CPLUS_INCLUDE_PATH': str(boost),
        'SANITIZE': '1' if mode == 'sanitizer' else '0',
        'CPC_SANITIZE': '1' if mode == 'sanitizer' else '0',
        'CPC_BASELINE_STAGED': '1',
        'CPC_TEST_STACK_KIB': str(STACK_KIB),
        'PYTHONDONTWRITEBYTECODE': '1',
        'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1',
        'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1',
    }
    flags = ['-std=c++20', '-Wall', '-Wextra']
    flags += ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    recipe = ['python3', 'build/floor-knowledge-check.py', '--mode', mode, '--root', str(root), '--boost-include', str(boost)]
    source = rp.snapshot(root)
    archive = rp.baseline_archive(root)
    baseline = rp.baseline_hashes(archive)
    archive_path = directory / 'baseline.tar'
    archive_path.write_bytes(archive)
    boost_before = boost_snapshot(boost)
    report = {
        'schema': SCHEMA, 'status': 'running', 'scope': 'TARGETED subset only',
        'claims_excluded': ['full-suite pass', 'CI pass', 'online judge AC', 'PDF/layout/taxonomy validation', 'LeakSanitizer coverage', 'complete toolchain attestation'],
        'mode': mode, 'run_id': run_id, 'started_at_utc': utc(),
        'git_head_at_start': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'tests_selected': [f'tests/{name}.cpp' for name in CPP_TESTS] + [APP_TEST],
        'helper': {'path': str(helper.relative_to(root)), 'sha256_before': helper_before,
                   'command': recipe, 'shell_command': shlex.join(recipe)},
        'staging': {'api': 'tools.run_provenance.stage_inputs', 'api_file_sha256': sha(root/'tools/run_provenance.py'),
                    'baseline_commit': PINNED_BASELINE, 'baseline_archive_sha256': rp.digest(archive),
                    'baseline_archive_path': str(archive_path.relative_to(root)),
                    'baseline_sha256': baseline, 'original_input_folders': list(rp.SOURCE_DIRS),
                    'original_sha256_before': source,
                    'directory': str(stage.relative_to(root)),
                    'historical_verification_copy_note': 'stage_inputs copies verification as context; no verification file is selected or executed by these targeted tests'},
        'toolchain': {'driver_path': str(compiler), 'driver_sha256_before': sha(compiler),
                      'frontend_path': str(frontend), 'frontend_sha256_before': sha(frontend),
                      'version': subprocess.check_output([str(compiler), '--version'], text=True).strip(),
                      'target': subprocess.check_output([str(compiler), '-dumpmachine'], text=True).strip(),
                      'scope': 'GNU driver and cc1plus fingerprints only; not whole toolchain'},
        'boost': {'include_path': str(boost), 'file_count': len(boost_before),
                  'manifest_sha256_before': rp.digest(canonical(boost_before))},
        'environment': env, 'cxx_flags': flags,
        'application_cxx_flags': ['-std=c++20'] + (['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']),
        'platform': platform.platform(), 'python_version': platform.python_version(),
        'pie': 'compiler default; no override', 'asan_quarantine': 'ASan default; no override',
        'leak_detection': 'disabled',
        'stack_policy': {'per_child_soft_kib': STACK_KIB, 'capped_at_inherited_hard': True, 'changes_hard_limit': False},
        'commands': [], 'test_results': [], 'failures': [],
    }
    (directory/'boost-files.json').write_bytes(canonical(boost_before)+b'\n')
    report['boost']['manifest_path'] = str((directory/'boost-files.json').relative_to(root))
    expected = dict(source, **baseline)
    rp.stage_inputs(root, stage, archive)
    staged = rp.snapshot(stage)
    report['staging']['staged_sha256_before'] = staged
    stage_ok = staged == expected and rp.snapshot(root) == source
    report['staging']['matches_original_plus_pinned_baseline'] = stage_ok
    if not stage_ok:
        report['failures'].append('Inputs changed during staging or do not match original plus pinned baseline')
    (stage/'build').mkdir()
    staged_helper = stage/'build/floor-knowledge-check.py'
    shutil.copy2(helper, staged_helper)
    report['helper']['staged_copy_sha256_before'] = sha(staged_helper)
    report['helper']['staged_copy_matches_original'] = sha(staged_helper) == helper_before
    report['generated_artifacts'] = {}
    with log_path.open('xb') as log:
        def emit(label, value):
            log.write((label+' '+json.dumps(value, sort_keys=True)+'\n').encode()); log.flush()
        emit('TARGETED_BEGIN', {'schema': SCHEMA, 'scope': report['scope'], 'run_id': run_id, 'mode': mode,
                               'original_manifest_sha256': rp.digest(canonical(source)),
                               'staged_manifest_sha256': rp.digest(canonical(staged)), 'baseline': PINNED_BASELINE,
                               'helper_sha256': helper_before, 'environment': env})
        def invoke(label, argv, timeout):
            index = len(report['commands']) + 1
            path = directory/f'{index:02d}-{label}.txt'
            item = {'label': label, 'argv': argv, 'shell_command': shlex.join(argv),
                    'cwd': str(stage), 'started_at_utc': utc(), 'timeout_seconds': timeout,
                    'log_path': str(path.relative_to(root))}
            emit('TARGETED_COMMAND', item)
            begin = time.monotonic()
            with path.open('xb') as command_log:
                process = subprocess.Popen(argv, cwd=stage, env=env, stdout=command_log,
                                           stderr=subprocess.STDOUT, preexec_fn=limit_stack)
                try:
                    code = process.wait(timeout=timeout)
                    item['timed_out'] = False
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
                    code = 124; item['timed_out'] = True
            data = path.read_bytes()
            log.write(data); log.flush()
            observation_lines = [line.split(b' ', 1)[1] for line in data.splitlines() if line.startswith(b'TARGETED_STACK ')]
            observations = [json.loads(line) for line in observation_lines]
            item.update(returncode=code, elapsed_seconds=round(time.monotonic()-begin, 6),
                        finished_at_utc=utc(), log_sha256=rp.digest(data), output=data.decode(errors='replace'),
                        sanitizer_diagnostics_clean=rp.clean_diagnostics(data), stack_observations=observations)
            item['passed'] = code == 0 and item['sanitizer_diagnostics_clean'] and len(observations) == 1 and observations[0]['hard_limit_unchanged'] and observations[0]['actual_soft_kib'] == (STACK_KIB if observations[0]['hard_kib']=='unlimited' else min(STACK_KIB, observations[0]['hard_kib']))
            if not item['passed']:
                report['failures'].append(label)
            report['commands'].append(item)
            emit('TARGETED_COMMAND_END', {k:item[k] for k in ('label','returncode','passed','elapsed_seconds','log_sha256')})
            print(f"{mode}: {label}: {'PASS' if item['passed'] else 'FAIL'} ({item['elapsed_seconds']:.2f}s)", flush=True)
            return item['passed']
        if stage_ok:
            for name in CPP_TESTS:
                exe = 'build/'+name
                compiled = invoke(name+'-compile', [str(compiler), *flags, 'tests/'+name+'.cpp', '-o', exe], 240)
                ran = invoke(name+'-run', ['./'+exe], 300) if compiled else False
                report['test_results'].append({'test':'tests/'+name+'.cpp', 'compiled':compiled, 'passed':compiled and ran})
                if compiled:
                    report['generated_artifacts'][exe] = sha(stage/exe)
            app_argv = [sys.executable, 'build/floor-knowledge-check.py', '--audit-python', APP_TEST]
            app_ok = invoke('floor_moments_application', app_argv, 300)
            report['test_results'].append({'test':APP_TEST, 'passed':app_ok})
            for filename in ('P5170.compact.cpp', 'P5170.compact'):
                path = stage/'build'/filename
                if path.is_file():
                    report['generated_artifacts']['build/'+filename] = sha(path)
        after_source = rp.snapshot(root)
        after_stage = rp.snapshot(stage)
        boost_after = boost_snapshot(boost)
        report['staging']['original_sha256_after'] = after_source
        report['staging']['staged_sha256_after'] = after_stage
        report['staging']['original_inputs_unchanged'] = after_source == source
        report['staging']['staged_inputs_unchanged'] = after_stage == staged
        report['toolchain']['driver_sha256_after'] = sha(compiler)
        report['toolchain']['frontend_sha256_after'] = sha(frontend)
        report['toolchain']['driver_unchanged'] = sha(compiler) == report['toolchain']['driver_sha256_before']
        report['toolchain']['frontend_unchanged'] = sha(frontend) == report['toolchain']['frontend_sha256_before']
        report['boost']['manifest_sha256_after'] = rp.digest(canonical(boost_after))
        report['boost']['unchanged'] = boost_before == boost_after
        report['helper']['sha256_after'] = sha(helper)
        report['helper']['staged_copy_sha256_after'] = sha(staged_helper)
        report['helper']['unchanged'] = sha(helper) == helper_before == sha(staged_helper)
        invariants = {
            'original_inputs_unchanged': after_source == source,
            'staged_inputs_unchanged': after_stage == staged,
            'compiler_driver_unchanged': report['toolchain']['driver_unchanged'],
            'compiler_frontend_unchanged': report['toolchain']['frontend_unchanged'],
            'boost_unchanged': boost_before == boost_after,
            'helper_unchanged': report['helper']['unchanged'],
            'all_five_selected_tests_passed': len(report['test_results']) == 5 and all(x['passed'] for x in report['test_results']),
        }
        report['invariants'] = invariants
        report['failures'].extend(k for k,v in invariants.items() if not v)
        report['status'] = 'passed' if not report['failures'] else 'failed'
        report['finished_at_utc'] = utc()
        emit('TARGETED_END', {'schema': SCHEMA, 'run_id': run_id, 'status': report['status'],
                             'invariants': invariants, 'finished_at_utc': report['finished_at_utc']})
    report['log'] = {'path': str(log_path.relative_to(root)), 'sha256': sha(log_path)}
    report['reproduction'] = {
        'shell_recipe': 'cd '+shlex.quote(str(root))+' && '+shlex.join(recipe),
        'prerequisites': ['unchanged source/input files listed in staging.original_sha256_before',
                         'pinned baseline available in git object database',
                         'retained build/floor-knowledge-check.py at recorded SHA256',
                         'GNU 14.2 driver/frontend and Boost include tree at recorded fingerprints'],
        'notes': 'Run either mode independently; stages and command logs are retained. The schema is distinct from cpc-test-run-v1 and is not consumable as a full-suite receipt.'}
    preserved = directory/'report.json'
    preserved.write_text(json.dumps(report, indent=2)+'\n')
    if report_path.exists():
        prior = directory/'prior-final-report.json'
        shutil.copy2(report_path, prior)
    shutil.copy2(preserved, report_path)
    print(f"{mode}: {report['status'].upper()} TARGETED subset receipt: {report_path}", flush=True)
    return 0 if report['status']=='passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('normal','sanitizer'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--boost-include', type=Path)
    parser.add_argument('--audit-python')
    args = parser.parse_args()
    if args.audit_python:
        audit_python(args.audit_python)
    else:
        if args.mode is None:
            parser.error('--mode required')
        root = args.root.resolve()
        boost = (args.boost_include or root/'build/deps/boost-1.83/usr/include').resolve(strict=True)
        raise SystemExit(run(args.mode, root, boost))
