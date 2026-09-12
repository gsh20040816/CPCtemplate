#!/usr/bin/env python3
"""Run existing oracle tests against current vector code and a pinned historical baseline.

Historical headers live only in the temporary test checkout, never in the library.
"""
from pathlib import Path
import os, shutil, subprocess, tempfile, tarfile, io

root = Path(__file__).resolve().parents[1]
baseline = '1a9fa3e91d7dff58915341040be069611370054c'
with tempfile.TemporaryDirectory(prefix='cpc-vector-tests-') as temp:
    stage = Path(temp)
    for name in ('src', 'tests', 'tools', 'verify', 'verification'):
        shutil.copytree(root / name, stage / name)
    archive = subprocess.check_output(['git', 'archive', baseline, 'src/classic'], cwd=root)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(stage, filter='data')
    env = dict(os.environ, CPC_BASELINE_STAGED='1')
    result = subprocess.run(['bash', 'tools/test.sh'], cwd=stage, env=env)
    if result.returncode == 0:
        print("Vector library regression with pinned historical baseline PASS", flush=True)
    raise SystemExit(result.returncode)
