"""Reporting states and reference URLs, not algorithm or OJ verification."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('template_report_generator', ROOT/'tools/template_report.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class ReportTests(unittest.TestCase):
    def test_ac_record_does_not_depend_on_driver_registration(self):
        self.assertEqual(module.ac_status({'ac':'https://example.org/result'}, ROOT),
                         '[记录](https://example.org/result)')

    def test_missing_and_planned_are_not_completed(self):
        for state in ['missing','planned_extension']:
            self.assertEqual(module.ac_status({'implementation':state}, ROOT), '待实现')

    def test_existing_driver_is_not_online_ac(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'driver.cpp').write_text('int main() {}\n')
            self.assertEqual(module.ac_status({'driver':'driver.cpp'}, root), '待在线 AC')
            self.assertEqual(module.ac_status({'driver':'absent.cpp'}, root), '驱动登记待核验；AC 待核验')
            self.assertEqual(module.ac_status({}, root), '驱动登记待核验；AC 待核验')

    def test_both_statement_source_shapes_use_urls(self):
        expected = '[来源 1](https://example.org/task)，[来源 2](https://example.org/limits)'
        self.assertEqual(module.source_links(['https://example.org/task','https://example.org/limits']), expected)
        self.assertEqual(module.source_links({'task.md':{'url':'https://example.org/task','sha256':'unused'},
                                              'info.toml':{'url':'https://example.org/limits'}}), expected)
        with self.assertRaises(ValueError): module.source_links(['task.md'])

    def test_library_checker_driver_index_is_current(self):
        inventory = json.loads((ROOT/'docs/library-checker-inventory.json').read_text())
        indexed = {driver for row in inventory['problems'] for driver in row['candidate_drivers']}
        current = {str(path.relative_to(ROOT)) for path in
                   (ROOT/'verify/library_checker').rglob('*.compact.cpp')}
        self.assertEqual(indexed, current)

    def test_current_generation_and_evidence_limits(self):
        reviews = json.loads((ROOT/'docs/template-problem-reviews.json').read_text())
        actual = (ROOT/'docs/TEMPLATE-PROBLEMS.md').read_text()
        self.assertEqual(module.render(reviews), actual)
        self.assertEqual(module.render(reviews), module.render(reviews))
        for symbol, driver, usage in [('GeneralSAM','verify/luogu/P6139.compact.cpp','example-132'),
                                     ('unit_flow_edges','verify/qoj/10424.compact.cpp','example-133')]:
            rows = [r for r in reviews if r['symbol']==symbol]
            self.assertEqual(len(rows),1); row = rows[0]
            self.assertEqual((row['driver'],row['usage']), (driver,usage))
            self.assertIsNone(row['ac']); self.assertIsNone(row['ranking']['rank'])
            self.assertEqual(module.ac_status(row,ROOT), '待在线 AC')
            for p in row['local_reports']: self.assertTrue((ROOT/p).is_file())
        with (ROOT/'docs/coverage.csv').open() as stream: coverage = list(csv.DictReader(stream))
        for symbol in ['GeneralSAM','unit_flow_edges']:
            row = next(r for r in coverage if r['source']=='issue11' and r['compact']==symbol)
            self.assertEqual(row['status'],'partial')
            self.assertIn('online AC/ranking unverified',row['verification'])
        for name in ['general-sam-application','knowns-application']:
            report = json.loads((ROOT/f'verification/{name}.json').read_text())
            for p,digest in report['files'].items():
                if not p.startswith(('src/', 'verify/')): continue
                if name == 'general-sam-application':
                    # The historical report remains immutable; construction was extended later.
                    for mode in ['normal', 'sanitizer']:
                        current = json.loads((ROOT/f'verification/sam-build-{mode}.json').read_text())
                        self.assertTrue(current['passed'])
                        self.assertEqual(current['source_before_sha256'], current['source_after_sha256'])
                        self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),
                                         current['source_after_sha256'][p])
                else:
                    self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest)
        known = next(r for r in reviews if r['symbol']=='unit_flow_edges')
        self.assertIn('not a standalone template',known['classification'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
