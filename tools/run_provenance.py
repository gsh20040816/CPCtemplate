#!/usr/bin/env python3
"""Shared, local-integrity checks for staged test receipts (not an attestation service)."""
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile

BASELINE = '1a9fa3e91d7dff58915341040be069611370054c'
SOURCE_DIRS = ('src', 'tests', 'tools', 'verify', 'docs')
SCHEMA = 'cpc-test-run-v1'
COMMAND = ['bash', 'tools/test.sh']
HEADER = b'CPC_RUN_BEGIN '
FOOTER = b'CPC_RUN_END '
ENV_KEYS = ('CXX', 'SANITIZE', 'CPC_SANITIZE', 'CPC_BASELINE_STAGED',
            'ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS', 'PATH', 'PYTHONPATH',
            'CPATH', 'CPLUS_INCLUDE_PATH', 'LIBRARY_PATH', 'LD_LIBRARY_PATH',
            'DYLD_LIBRARY_PATH', 'CXXFLAGS', 'CPPFLAGS', 'LDFLAGS')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def clean_diagnostics(data):
    return re.search(rb'ERROR: (?:AddressSanitizer|LeakSanitizer)|runtime error:|SUMMARY: (?:AddressSanitizer|UndefinedBehaviorSanitizer)|AddressSanitizer:DEADLYSIGNAL', data) is None


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def snapshot(root, folders=SOURCE_DIRS):
    result = {}
    for folder in folders:
        base = root / folder
        if not base.is_dir() or base.is_symlink():
            raise ValueError(f'missing or symlinked input directory: {base}')
        for path in sorted(base.rglob('*')):
            rel = path.relative_to(root)
            if '__pycache__' in rel.parts or path.suffix == '.pyc':
                continue
            if folder == 'verification' and rel.parts[1:2] == ('runs',):
                continue
            if path.is_symlink():
                raise ValueError(f'symlinked input is unsupported: {rel}')
            if path.is_file():
                result[rel.as_posix()] = digest(path.read_bytes())
    return result


def baseline_archive(root):
    return subprocess.check_output(['git', 'archive', BASELINE, 'src/classic'], cwd=root)


def baseline_hashes(archive):
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        return {m.name: digest(tar.extractfile(m).read()) for m in tar if m.isfile()}


def stage_inputs(root, stage, archive):
    # Never recursively copy previous run receipts into the next run.
    for folder in (*SOURCE_DIRS, 'verification'):
        def ignore(directory, names):
            omitted = [n for n in names if n == '__pycache__' or n.endswith('.pyc')]
            if Path(directory) == root / 'verification' and 'runs' in names:
                omitted.append('runs')
            return omitted
        shutil.copytree(root / folder, stage / folder, ignore=ignore)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(stage, filter='data')


def execution_environment(environ):
    env = dict(environ)
    mode = env.get('SANITIZE', '0')
    if mode not in ('0', '1'):
        raise ValueError('SANITIZE must be 0 or 1')
    compiler = env.get('CXX') or ('g++-16' if shutil.which('g++-16') else 'g++')
    resolved = shutil.which(compiler, path=env.get('PATH'))
    if not resolved:
        raise ValueError(f'compiler not found: {compiler}')
    env.update(CXX=str(Path(resolved).resolve()), SANITIZE=mode,
               CPC_SANITIZE=mode, CPC_BASELINE_STAGED='1')
    # Test scripts must not silently lose Python assertions.
    if env.get('PYTHONOPTIMIZE') not in (None, '', '0'):
        raise ValueError('PYTHONOPTIMIZE disables test assertions')
    metadata = {
        'platform': platform.platform(), 'system': platform.system(),
        'machine': platform.machine(), 'python': platform.python_version(),
        'compiler': {'path': env['CXX'], 'sha256': digest(Path(env['CXX']).read_bytes()),
                     'version': subprocess.check_output([env['CXX'], '--version'], env=env, text=True).strip(),
                     'target': subprocess.check_output([env['CXX'], '-dumpmachine'], env=env, text=True).strip()},
        'environment': {key: env.get(key) for key in ENV_KEYS},
    }
    return env, 'sanitizer' if mode == '1' else 'normal', metadata


def validate_receipt(root, path, mode, source, baseline):
    receipt = json.loads(path.read_text())
    if receipt.get('schema') != SCHEMA or receipt.get('status') != 'passed':
        raise ValueError(f'{path}: not a successful bound receipt')
    start = receipt['start']
    end = receipt['end']
    expected = dict(source, **baseline)
    if (start['mode'] != mode or start['command'] != COMMAND or
            start['baseline'] != BASELINE or start['baseline_sha256'] != baseline or
            start['source_sha256'] != source or
            start['executed_sha256'] != expected):
        raise ValueError(f'{path}: stale source, baseline, inputs, command or mode')
    metadata = start['metadata']
    environment = metadata['environment']
    flag = '1' if mode == 'sanitizer' else '0'
    if (environment['SANITIZE'] != flag or environment['CPC_SANITIZE'] != flag or
            environment['CPC_BASELINE_STAGED'] != '1' or
            environment['CXX'] != metadata['compiler']['path']):
        raise ValueError(f'{path}: inconsistent execution environment')
    for key in ('platform', 'system', 'machine', 'python'):
        if not isinstance(metadata.get(key), str) or not metadata[key]:
            raise ValueError(f'{path}: missing actual {key}')
    for key in ('path', 'sha256', 'version', 'target'):
        if not isinstance(metadata['compiler'].get(key), str) or not metadata['compiler'][key]:
            raise ValueError(f'{path}: missing actual compiler {key}')
    if (type(end['returncode']) is not int or end['returncode'] != 0 or
            end['source_after_sha256'] != source or end['executed_after_sha256'] != expected or
            end['compiler_after_sha256'] != metadata['compiler']['sha256']):
        raise ValueError(f'{path}: failed or changed run')
    # Fixed sibling filename prevents accidental association with another log.
    if receipt['log']['path'] != 'output.log':
        raise ValueError(f'{path}: invalid log name')
    log = (path.parent / 'output.log').read_bytes()
    if not clean_diagnostics(log):
        raise ValueError(f'{path}: sanitizer diagnostic in log')
    if receipt['log']['sha256'] != digest(log):
        raise ValueError(f'{path}: changed log')
    if not log.startswith(HEADER + canonical(start) + b'\n') or not log.endswith(b'\n' + FOOTER + canonical(end) + b'\n'):
        raise ValueError(f'{path}: log/run binding mismatch')
    return receipt
