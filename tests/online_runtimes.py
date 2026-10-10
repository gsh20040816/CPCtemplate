from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from online_runtimes import build


class RuntimeEvidenceTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'verification/submitted').mkdir(parents=True)
        (root / 'docs').mkdir()
        archive = root / 'verification/submitted/a.cpp'
        archive.write_text('int main() {}\n')
        row = dict(problem='fixture', record='https://judge.example/record/1',
                   submitted_source='verification/submitted/a.cpp',
                   submitted_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                   verdict='Accepted', time_ms=999)
        (root / 'verification/oj.json').write_text(json.dumps([row]))
        (root / 'docs/template-problem-reviews.json').write_text(json.dumps([{'ac': row['record']}]))
        return row

    def test_legacy_time_does_not_become_max_or_total(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            r = build(root)['entries'][0]
            self.assertIsNone(r['maximum_case_ms'])
            self.assertIsNone(r['reported_total_ms'])
            self.assertIsNone(r['ratio'])
            self.assertEqual(r['observations'][0]['timing']['time_ms'], 999)

    def test_deduplicate_url_preserve_independent_scopes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.fixture(root)
            row.pop('time_ms')
            row['test_times_ms'] = [7, 3, 4]
            row['total_time_ms'] = 14
            (root / 'verification/batch-online.json').write_text(json.dumps([row]))
            data = build(root)
            self.assertEqual(data['counts']['accepted'], 1)
            r = data['entries'][0]
            self.assertEqual((r['maximum_case_ms'], r['sum_of_case_ms'], r['reported_total_ms']), (7, 14, 14))
            self.assertEqual(len(r['observations']), 2)

    def test_flat_receipt_preserves_rounded_display(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.fixture(root)
            row.pop('time_ms')
            row.update(displayed_total_time='13.72s', max_case_time_display='2.01s')
            (root / 'verification/batch-online.json').write_text(json.dumps(row))
            result = build(root)['entries'][0]
            self.assertEqual(len(result['observations']), 2)
            timing = result['observations'][1]['timing']
            self.assertEqual(timing['max_case_time_display'], '2.01s')
            self.assertIsNone(result['maximum_case_ms'])
            self.assertIsNone(result['reported_total_ms'])

    def test_corrupt_archive_is_not_verified(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            (root / 'verification/submitted/a.cpp').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Archive hash mismatch'):
                build(root)

    def test_conflicting_explicit_maximum_requires_review(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.fixture(root)
            (root / 'verification/batch-online.json').write_text(json.dumps([
                dict(row, max_case_time_ms=7), dict(row, test_times_ms=[8, 3])]))
            with self.assertRaisesRegex(ValueError, 'Conflicting maximum_case_ms'):
                build(root)

    def test_same_observation_maximum_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.fixture(root)
            row.update(max_case_time_ms=7, test_times_ms=[8, 3])
            (root / 'verification/oj.json').write_text(json.dumps([row]))
            with self.assertRaisesRegex(ValueError, 'within observation'):
                build(root)

    def test_missing_reviewed_ac_fails_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root)
            (root / 'docs/template-problem-reviews.json').write_text('[{"ac":"https://judge.example/record/2"}]')
            with self.assertRaisesRegex(ValueError, 'missing archived runtime'):
                build(root)

    def test_pending_and_rejected_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            row = self.fixture(root)
            row.pop('time_ms')
            rows = [dict(row, record='https://judge.example/record/2', verdict='Waiting'),
                    dict(row, record=None, verdict='submission_rejected')]
            (root / 'verification/batch-online.json').write_text(json.dumps(rows))
            data = build(root)
            self.assertEqual(data['counts']['accepted'], 1)
            self.assertEqual(data['counts']['with_record'], 2)
            for r in data['entries']:
                if 'Accepted' not in r['statuses']:
                    self.assertIsNone(r['maximum_case_ms'])
                    self.assertIsNone(r['sum_of_case_ms'])


if __name__ == '__main__':
    unittest.main()
