#!/usr/bin/env python3
"""Bounded provenance fixtures. Does not run or claim a full algorithm suite pass."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import manifest
import run_provenance as provenance
import test_baseline


def archive_fixture():
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w') as tar:
        data = b'// historical fixture\n'
        info = tarfile.TarInfo('src/classic/fixture.hpp')
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in (*provenance.SOURCE_DIRS, 'verification'):
            (self.root / directory).mkdir()
        (self.root / 'src/current.hpp').write_text('// fixture source\n')
        (self.root / 'docs/required.json').write_text('{"fixture": true}\n')
        (self.root / 'tools/test.sh').write_text('set -eu\ntest -f docs/required.json\necho "bounded fixture PASS"\n')
        (self.root / 'verification/manifest.json').write_text('{"historical": true}\n')
        self.archive = archive_fixture()
        self.baseline = provenance.baseline_hashes(self.archive)
        self.env, _, self.metadata = provenance.execution_environment(dict(os.environ, SANITIZE='0'))

    def run_fixture(self, mode='normal'):
        env = dict(self.env, SANITIZE='1' if mode == 'sanitizer' else '0')
        with patch.dict(os.environ, env, clear=True), patch.object(test_baseline, 'baseline_archive', return_value=self.archive):
            status = test_baseline.run(self.root)
        receipts = sorted((self.root / 'verification/runs').glob('*/receipt.json'))
        return status, receipts[-1]

    def validate(self, path, mode='normal'):
        return provenance.validate_receipt(self.root, path, mode, provenance.snapshot(self.root), self.baseline)

    def tamper(self, path, action):
        receipt = json.loads(path.read_text())
        action(receipt)
        path.write_text(json.dumps(receipt))
        with self.assertRaises((ValueError, KeyError, TypeError)):
            self.validate(path)

    def test_real_runner_copies_docs_and_emits_valid_receipt(self):
        status, path = self.run_fixture()
        self.assertEqual(status, 0)
        receipt = self.validate(path)
        self.assertEqual(receipt['start']['metadata']['compiler'], self.metadata['compiler'])
        self.assertEqual(receipt['start']['metadata']['platform'], self.metadata['platform'])
        self.assertNotIn('HOME', receipt['start']['metadata']['environment'])
        self.assertEqual((self.root / 'verification/manifest.json').read_text(), '{"historical": true}\n')

    def test_valid_pair_aggregates_actual_metadata(self):
        _, normal = self.run_fixture()
        _, sanitizer = self.run_fixture('sanitizer')
        with patch.object(manifest, 'baseline_archive', return_value=self.archive):
            result = manifest.build_manifest(self.root, normal, sanitizer)
        self.assertEqual(set(result['runs']), {'normal', 'sanitizer'})
        self.assertEqual(result['runs']['normal']['start']['metadata']['compiler'], self.metadata['compiler'])

    def test_old_log_and_old_manifest_rejected(self):
        old = self.root / 'verification/local-tests.txt'
        old.write_text('All historical tests PASS\n')
        with self.assertRaises((ValueError, KeyError)):
            self.validate(old)
        with self.assertRaises(ValueError):
            self.validate(self.root / 'verification/manifest.json')

    def test_source_edit_add_delete_rejected(self):
        _, path = self.run_fixture()
        source = self.root / 'src/current.hpp'
        original = source.read_bytes()
        source.write_text('// changed\n')
        with self.assertRaises(ValueError): self.validate(path)
        source.write_bytes(original)
        added = self.root / 'tests/new.py'
        added.write_text('pass\n')
        with self.assertRaises(ValueError): self.validate(path)
        added.unlink()
        source.unlink()
        with self.assertRaises(ValueError): self.validate(path)

    def test_log_edit_rejected_even_if_receipt_hash_is_updated(self):
        _, path = self.run_fixture()
        log = path.parent / 'output.log'
        log.write_bytes(log.read_bytes() + b'edited\n')
        self.tamper(path, lambda r: r['log'].update(sha256=provenance.digest(log.read_bytes())))

    def test_log_body_edit_rejected(self):
        _, path = self.run_fixture()
        log = path.parent / 'output.log'
        log.write_bytes(log.read_bytes().replace(b'bounded fixture PASS', b'altered fixture PASS'))
        with self.assertRaises(ValueError): self.validate(path)

    def test_mode_or_metadata_edit_rejected(self):
        _, path = self.run_fixture()
        original = path.read_bytes()
        self.tamper(path, lambda r: r['start'].update(mode='sanitizer'))
        path.write_bytes(original)
        self.tamper(path, lambda r: r['start']['metadata'].update(platform='invented platform'))
        path.write_bytes(original)
        self.tamper(path, lambda r: r['start']['metadata']['environment'].update(SANITIZE='1'))

    def test_failed_run_rejected_including_relabelled_receipt(self):
        (self.root / 'tools/test.sh').write_text('echo "partial PASS"\nexit 7\n')
        status, path = self.run_fixture()
        self.assertEqual(status, 7)
        self.tamper(path, lambda r: r.update(status='passed'))
        self.tamper(path, lambda r: r['end'].update(returncode=0))

    def test_silent_sanitizer_failure_rejected(self):
        (self.root / 'tools/test.sh').write_text('echo "x.cpp: runtime error: deliberate fixture"\nexit 0\n')
        status, path = self.run_fixture('sanitizer')
        self.assertNotEqual(status, 0)
        with self.assertRaises(ValueError): self.validate(path, 'sanitizer')

    def test_staged_source_change_rejected(self):
        (self.root / 'tools/test.sh').write_text('echo changed >> src/current.hpp\n')
        status, path = self.run_fixture()
        self.assertNotEqual(status, 0)
        self.tamper(path, lambda r: r.update(status='passed'))

    def test_parent_source_change_during_execution_rejected(self):
        target = self.root / 'src/current.hpp'
        (self.root / 'tools/test.sh').write_text(f'echo changed >> "{target}"\n')
        status, path = self.run_fixture()
        self.assertNotEqual(status, 0)
        with self.assertRaises(ValueError): self.validate(path)

    def test_compiler_after_and_command_changes_rejected(self):
        _, path = self.run_fixture()
        original = path.read_bytes()
        self.tamper(path, lambda r: r['end'].update(compiler_after_sha256='0' * 64))
        path.write_bytes(original)
        self.tamper(path, lambda r: r['start'].update(command=['true']))

    def test_cli_requires_receipts_and_preserves_existing_files(self):
        result = subprocess.run([sys.executable, str(ROOT / 'tools/manifest.py')], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for target in (self.root / 'verification/manifest.json', self.root / 'verification/runs/existing.json'):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('preserved')
            args = ['manifest.py', '--normal', 'unused', '--sanitizer', 'unused', '--output', str(target)]
            with patch.object(manifest, '__file__', str(self.root / 'tools/manifest.py')), patch.object(manifest, 'build_manifest', return_value={}), patch.object(sys, 'argv', args):
                with self.assertRaises(SystemExit) as error: manifest.main()
                self.assertNotEqual(error.exception.code, 0)
            self.assertEqual(target.read_text(), 'preserved')

    def test_source_change_during_staging_rejected(self):
        real_stage = provenance.stage_inputs
        def changing_stage(root, stage, archive):
            real_stage(root, stage, archive)
            (root / 'src/current.hpp').write_text('changed\n')
        with patch.object(test_baseline, 'stage_inputs', side_effect=changing_stage):
            with self.assertRaises(ValueError): self.run_fixture()

    def test_no_recursive_receipt_copy_and_no_symlink_input(self):
        (self.root / 'verification/runs').mkdir()
        (self.root / 'verification/runs/old.log').write_text('old')
        with tempfile.TemporaryDirectory() as temp:
            stage = Path(temp)
            provenance.stage_inputs(self.root, stage, self.archive)
            self.assertFalse((stage / 'verification/runs').exists())
            self.assertTrue((stage / 'docs/required.json').is_file())
        (self.root / 'src/link.hpp').symlink_to(self.root / 'src/current.hpp')
        with self.assertRaises(ValueError): provenance.snapshot(self.root)

    def test_optimized_python_refused(self):
        with self.assertRaises(ValueError):
            provenance.execution_environment(dict(os.environ, PYTHONOPTIMIZE='1'))

    def test_real_basic_scope_preflight_in_stage(self):
        # Real source/docs preflight only; never invokes tools/test.sh or a C++ suite.
        with tempfile.TemporaryDirectory() as temp:
            stage = Path(temp)
            provenance.stage_inputs(ROOT, stage, provenance.baseline_archive(ROOT))
            result = subprocess.run([sys.executable, 'tests/basic_template_scope.py'], cwd=stage, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('scope preserved PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
