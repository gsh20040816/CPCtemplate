#!/usr/bin/env python3
"""Run the entire staged suite and retain a source-bound receipt, including failures."""
import datetime
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

from run_provenance import (BASELINE, COMMAND, SCHEMA, HEADER, FOOTER, baseline_archive,
                            baseline_hashes, canonical, clean_diagnostics, digest, execution_environment,
                            snapshot, stage_inputs, stack_observation, valid_stack)


def run(root):
    env, mode, metadata = execution_environment(os.environ)
    source = snapshot(root)
    archive = baseline_archive(root)
    baseline = baseline_hashes(archive)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ-') + mode + '-' + uuid.uuid4().hex[:8]
    output = root / 'verification' / 'runs' / run_id
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='cpc-vector-tests-') as temp:
        stage = Path(temp)
        stage_inputs(root, stage, archive)
        executed = snapshot(stage)
        if (executed != dict(source, **baseline) or snapshot(root) != source):
            raise ValueError('inputs changed during staging; refusing to run')
        start = {'run_id': run_id, 'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'mode': mode, 'command': COMMAND, 'baseline': BASELINE,
                 'baseline_sha256': baseline, 'source_sha256': source,
                 'executed_sha256': executed,
                 'metadata': metadata}
        with (output / 'output.log').open('xb') as log:
            log.write(HEADER + canonical(start) + b'\n')
            log.flush()
            process = subprocess.Popen(COMMAND, cwd=stage, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline, b''):
                log.write(line)
                log.flush()
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
            process.stdout.close()
            returncode = process.wait()
            end = {'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'returncode': returncode, 'source_after_sha256': snapshot(root),
                   'executed_after_sha256': snapshot(stage),
                   'compiler_after_sha256': digest(Path(env['CXX']).read_bytes())}
            log.flush()
            body = (output / 'output.log').read_bytes()
            end['linux_stack_actual'] = stack_observation(body)
            passed = (valid_stack(metadata, end['linux_stack_actual']) and clean_diagnostics(body) and returncode == 0 and end['source_after_sha256'] == source and
                      end['executed_after_sha256'] == executed and
                      end['compiler_after_sha256'] == metadata['compiler']['sha256'])
            log.write(b'\n' + FOOTER + canonical(end) + b'\n')
        receipt = {'schema': SCHEMA, 'status': 'passed' if passed else 'failed', 'start': start, 'end': end,
                   'log': {'path': 'output.log', 'sha256': digest((output / 'output.log').read_bytes())}}
        (output / 'receipt.json').write_bytes(canonical(receipt) + b'\n')
        print(f'Run receipt: {output / "receipt.json"}', flush=True)
        if passed:
            print('Vector library regression with pinned historical baseline PASS', flush=True)
        elif returncode == 0:
            print('FAIL: source/compiler/stack changed or sanitizer diagnostic during execution', file=sys.stderr)
        return 0 if passed else (returncode or 1)


if __name__ == '__main__':
    try:
        raise SystemExit(run(Path(__file__).resolve().parents[1]))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit(f'Verification failed closed: {error}')
