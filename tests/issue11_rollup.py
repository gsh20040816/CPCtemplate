#!/usr/bin/env python3
"""Check issue #11 accounting/provenance; no algorithms, PDFs or OJ are run."""
from collections import Counter
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('issue11_inventory', ROOT / 'tools/issue11_inventory.py')
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)  # Import must not parse arguments or read a PDF.
SOURCE_KEYS = ('section', 'title', 'toc_page', 'physical_page', 'level')
SOURCE_DIGEST = 'a9aea268df0cb73d505427aa0cd1c2e6d8abf1a28c1905b77e5f04fc6bc2bd03'
LOCAL_STATUSES = {
    'existing_implementation_local_verified',
    'existing_formula_implementation_local_verified',
    'implemented_local_verified_online_pending',
    'implemented_application_local_verified_online_pending',
}


def source_digest(data):
    snapshot = {key: data[key] for key in
                ('issue', 'url', 'pdf_sha256', 'pdf_bytes', 'pdf_pages', 'scope_note')}
    snapshot['entries'] = [{key: row[key] for key in SOURCE_KEYS} for row in data['entries']]
    return hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def independent_counts(entries, section=None):
    """Select terminal nodes by tuple ancestry, not the generator's prefix scan."""
    paths = {tuple(row['section'].split('.')): row for row in entries}
    parent_paths = {path[:size] for path in paths for size in range(1, len(path))}
    prefix = tuple(section.split('.')) if section else ()
    leaves = [row for path, row in paths.items() if path not in parent_paths and
              len(path) > len(prefix) and path[:len(prefix)] == prefix]
    statuses = Counter(row['status'] for row in leaves)
    return dict(
        leaf_count=len(leaves),
        leaf_status_counts=dict(sorted(statuses.items())),
        reviewed_leaf_count=sum(row['status'] != 'pending_content_review' for row in leaves),
        locally_verified_leaf_count=sum(row['status'] in LOCAL_STATUSES for row in leaves),
        partial_leaf_sections=[row['section'] for row in leaves if row['status'] == 'reviewed_partial_coverage'],
        pending_content_leaf_sections=[row['section'] for row in leaves if row['status'] == 'pending_content_review'],
        explicit_online_pending_leaf_count=sum(row['status'] in {
            'implemented_local_verified_online_pending',
            'implemented_application_local_verified_online_pending'} for row in leaves),
        all_leaves_content_reviewed=bool(leaves) and all(row['status'] != 'pending_content_review' for row in leaves),
        all_leaves_locally_verified=bool(leaves) and all(row['status'] in LOCAL_STATUSES for row in leaves),
    )


def validate(data, markdown):
    assert source_digest(data) == SOURCE_DIGEST, 'attachment provenance/source rows changed'
    entries = data['entries']
    summary = data['hierarchy_summary']
    assert summary == inventory.hierarchy_summary(entries), 'stored summary is not recomputed'
    for key, value in independent_counts(entries).items():
        assert summary[key] == value, ('independent total disagrees', key)
    for parent in summary['parents']:
        for key, value in independent_counts(entries, parent['section']).items():
            assert parent[key] == value, ('independent parent disagrees', parent['section'], key)
    by_section = {row['section']: row for row in entries}
    assert summary['heading_count'] == 88
    assert summary['parent_heading_count'] == 26 and summary['leaf_count'] == 62
    assert summary['chapter_heading_count'] == 6 and summary['main_topic_heading_count'] == 55
    assert summary['variant_heading_count'] == 27
    assert summary['attachment_complete'] is False
    assert summary['recorded_pending_parent_sections'] == ['3', '4', '5']
    for section in ('3', '4', '5'):
        assert by_section[section]['status'] == 'pending_content_review'
    assert by_section['6.5.2']['status'] == 'reviewed_partial_coverage'
    assert '稳健谓词和数值契约' in by_section['6.5.2']['review']
    assert '通用浮点输入/无界分类' in by_section['6.4']['review']
    assert '任意浮点输入的稳健凸包' in by_section['6.1']['review']
    assert '原题外部地址与线上 AC 待核验' in by_section['4.2.2']['review']
    assert '附件无完整牛客题号' in by_section['4.3.1']['review']
    assert '不声称完成 Seoul 原题' in by_section['6.5.1']['review']
    assert by_section['2.14.1']['status'] == 'implemented_application_local_verified_online_pending'
    assert all(row.get('review', '').strip() for row in entries if row['level'] > 0), 'missing leaf/topic review'
    assert markdown == inventory.render_inventory(data), 'Markdown differs from source and summary'
    for note in ('通用浮点半平面交、无界分类', '竞赛应用及本地接口用法不代替正式模板题覆盖',
                 '本地验证数量不是全功能完成数量，更不是线上 AC 数量', 'FFT-ATTACHMENT.md',
                 'POLYNOMIAL-ATTACHMENT-BASE.md', 'RECURRENCE-ATTACHMENT.md'):
        assert note in markdown, ('scope limitation lost', note)


class Issue11RollupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'docs/issue11-inventory.json').read_text())
        cls.markdown = (ROOT / 'docs/ISSUE-11.md').read_text()

    def reject(self, mutate, rerender=False):
        data = copy.deepcopy(self.data)
        mutate(data)
        markdown = inventory.render_inventory(data) if rerender else self.markdown
        with self.assertRaises(AssertionError):
            validate(data, markdown)

    def test_source_summary_and_markdown_agree(self):
        validate(self.data, self.markdown)

    def test_no_parent_double_counting_or_online_inference(self):
        summary = self.data['hierarchy_summary']
        self.assertEqual(summary['locally_verified_leaf_count'], 61)
        self.assertEqual(summary['reviewed_leaf_count'], 62)
        self.assertEqual(summary['partial_leaf_sections'], ['6.5.2'])
        self.assertEqual(summary['pending_content_leaf_sections'], [])
        self.assertEqual(summary['explicit_online_pending_leaf_count'], 38)
        self.assertFalse(summary['attachment_complete'])
        self.assertEqual(summary['leaf_status_counts']['implemented_application_local_verified_online_pending'], 1)
        # Both source application rows remain; only the terminal heading enters the leaf total.
        self.assertEqual(sum(row['status'] == 'implemented_application_local_verified_online_pending'
                             for row in self.data['entries']), 2)

    def test_stale_chapter_status_is_not_a_pending_leaf(self):
        parents = {row['section']: row for row in self.data['hierarchy_summary']['parents']}
        for section, count in [('3', 10), ('4', 8), ('5', 13)]:
            with self.subTest(section=section):
                self.assertEqual(parents[section]['leaf_count'], count)
                self.assertEqual(parents[section]['reviewed_leaf_count'], count)
                self.assertEqual(parents[section]['locally_verified_leaf_count'], count)
                self.assertEqual(parents[section]['pending_content_leaf_sections'], [])
        self.assertEqual(parents['6.5']['leaf_count'], 3)
        self.assertEqual(parents['6.5']['locally_verified_leaf_count'], 2)
        self.assertFalse(parents['6.5']['all_leaves_locally_verified'])
        self.assertFalse(parents['6']['all_leaves_locally_verified'])

    def test_provenance_source_rows_and_order_are_pinned(self):
        for key, value in [('pdf_sha256', '0' * 64), ('pdf_pages', 200), ('pdf_bytes', 1),
                           ('issue', 'https://example.invalid'), ('url', 'https://example.invalid'),
                           ('scope_note', 'all done')]:
            with self.subTest(key=key):
                self.reject(lambda data: data.__setitem__(key, value))
        for key, value in [('title', 'changed'), ('toc_page', 1), ('physical_page', 1),
                           ('section', '99'), ('level', 2)]:
            with self.subTest(key=key):
                self.reject(lambda data: data['entries'][0].__setitem__(key, value))
        self.reject(lambda data: data['entries'].reverse())
        self.reject(lambda data: data['entries'].pop())

    def test_inflated_or_stale_summary_is_rejected(self):
        for key, value in [('attachment_complete', True), ('all_leaves_locally_verified', True),
                           ('leaf_count', 88), ('locally_verified_leaf_count', 62),
                           ('partial_leaf_sections', []), ('explicit_online_pending_leaf_count', 0)]:
            with self.subTest(key=key):
                self.reject(lambda data: data['hierarchy_summary'].__setitem__(key, value), True)
        for section in ('6', '6.5'):
            self.reject(lambda data: next(row for row in data['hierarchy_summary']['parents']
                        if row['section'] == section).__setitem__('all_leaves_locally_verified', True), True)
        self.reject(lambda data: data['hierarchy_summary']['parents'].pop())

    def test_false_verified_parent_and_unknown_complete_status_are_rejected(self):
        for section in ('6', '6.5'):
            for status in ('existing_implementation_local_verified', 'complete'):
                entries = copy.deepcopy(self.data['entries'])
                next(row for row in entries if row['section'] == section)['status'] = status
                with self.subTest(section=section, status=status), self.assertRaises(AssertionError):
                    inventory.hierarchy_summary(entries)

    def test_real_gap_cannot_be_erased_by_recomputation(self):
        data = copy.deepcopy(self.data)
        next(row for row in data['entries'] if row['section'] == '6.5.2')['status'] = 'existing_implementation_local_verified'
        data['hierarchy_summary'] = inventory.hierarchy_summary(data['entries'])
        with self.assertRaises(AssertionError):
            validate(data, inventory.render_inventory(data))
        for section in ('6.5.2', '6.4', '6.1', '4.2.2', '4.3.1', '6.5.1'):
            self.reject(lambda data: next(row for row in data['entries'] if row['section'] == section)
                        .__setitem__('review', 'fully implemented and verified'), True)

    def test_partial_and_pending_children_propagate_without_prefix_collisions(self):
        for status in ('reviewed_partial_coverage', 'pending_content_review'):
            rows = [dict(section=section, level=section.count('.'), status=value) for section, value in [
                ('1', 'reviewed_partial_coverage'), ('1.1', 'reviewed_partial_coverage'),
                ('1.1.1', status), ('1.10', 'existing_implementation_local_verified'),
                ('1.10.1', 'existing_implementation_local_verified')]]
            summary = inventory.hierarchy_summary(rows)
            parents = {row['section']: row for row in summary['parents']}
            self.assertEqual(summary['leaf_count'], 2)
            self.assertFalse(summary['all_leaves_locally_verified'])
            self.assertEqual(parents['1.1']['locally_verified_leaf_count'], 0)
            self.assertEqual(parents['1.10']['locally_verified_leaf_count'], 1)
            self.assertEqual(parents['1']['direct_child_sections'], ['1.1', '1.10'])
            self.assertEqual(summary['reviewed_leaf_count'], 1 if status == 'pending_content_review' else 2)
            for parent in ('1', '1.1'):
                altered = copy.deepcopy(rows)
                next(row for row in altered if row['section'] == parent)['status'] = 'existing_implementation_local_verified'
                with self.assertRaises(AssertionError):
                    inventory.hierarchy_summary(altered)

    def test_pending_intermediate_parent_is_not_silently_promoted(self):
        rows = [dict(section=section, level=section.count('.'), status=status) for section, status in [
            ('1', 'existing_implementation_local_verified'), ('1.1', 'pending_content_review'),
            ('1.1.1', 'existing_implementation_local_verified')]]
        with self.assertRaises(AssertionError):
            inventory.hierarchy_summary(rows)

    def test_duplicate_missing_parent_level_and_status_errors_are_rejected(self):
        for mutate in (lambda rows: rows.append(copy.deepcopy(rows[0])),
                       lambda rows: rows.pop(0),
                       lambda rows: rows[0].__setitem__('level', 1),
                       lambda rows: rows[0].__setitem__('status', 'done')):
            rows = copy.deepcopy(self.data['entries'])
            mutate(rows)
            with self.assertRaises(AssertionError):
                inventory.hierarchy_summary(rows)

    def test_refresh_cli_is_no_pdf_and_idempotent(self):
        with tempfile.TemporaryDirectory(prefix='issue11-rollup-') as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            path = root / 'docs/issue11-inventory.json'
            path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + '\n')
            with mock.patch.object(inventory, 'ROOT', root), \
                    mock.patch.object(inventory, 'inventory_from_pdf', side_effect=AssertionError('PDF accessed')), \
                    mock.patch.object(inventory.subprocess, 'check_output', side_effect=AssertionError('process started')), \
                    mock.patch('sys.stdout', new=io.StringIO()):
                inventory.main(['--refresh-summary'])
                first = path.read_bytes(), (root / 'docs/ISSUE-11.md').read_bytes()
                inventory.main(['--refresh-summary'])
                self.assertEqual(first, (path.read_bytes(), (root / 'docs/ISSUE-11.md').read_bytes()))
            rebuilt = json.loads(path.read_text())
            self.assertEqual(rebuilt['entries'], self.data['entries'])
            validate(rebuilt, (root / 'docs/ISSUE-11.md').read_text())

    def test_pdf_cli_replaces_stale_summary_without_dropping_rows(self):
        with tempfile.TemporaryDirectory(prefix='issue11-rollup-') as directory:
            root = Path(directory)
            (root / 'docs').mkdir()
            prior = copy.deepcopy(self.data)
            prior['hierarchy_summary'] = {'attachment_complete': True, 'leaf_count': 88}
            path = root / 'docs/issue11-inventory.json'
            path.write_text(json.dumps(prior, ensure_ascii=False))
            with mock.patch.object(inventory, 'ROOT', root), \
                    mock.patch.object(inventory, 'inventory_from_pdf', return_value=prior) as extract, \
                    mock.patch('sys.stdout', new=io.StringIO()):
                inventory.main(['original-attachment.pdf'])
                extract.assert_called_once()
                self.assertEqual(extract.call_args.args[0], Path('original-attachment.pdf'))
            rebuilt = json.loads(path.read_text())
            self.assertEqual(rebuilt['entries'], self.data['entries'])
            validate(rebuilt, (root / 'docs/ISSUE-11.md').read_text())

    def test_pdf_entrypoint_retains_all_original_metadata_and_recomputes(self):
        # Mock extraction only: no real PDF is read, written, fetched or rendered.
        prior = copy.deepcopy(self.data)
        prior['future_metadata'] = {'keep': True}
        prior['entries'][0]['future_review_field'] = 'keep'
        body = b'fixture bytes, not a PDF'
        prior['pdf_sha256'] = hashlib.sha256(body).hexdigest()
        prior['pdf_bytes'] = len(body)
        pages = [''] * prior['pdf_pages']
        pages[0] = '\n'.join(f"{row['section']} {row['title']} {row['toc_page']}" for row in prior['entries'])
        for row in prior['entries']:
            pages[row['physical_page'] - 1] += f"{row['section']} {row['title']}\n"
        pdf = mock.Mock()
        pdf.read_bytes.return_value = body
        pdf.stat.return_value.st_size = len(body)
        with mock.patch.object(inventory.subprocess, 'check_output', return_value='\f'.join(pages) + '\f'):
            rebuilt = inventory.inventory_from_pdf(pdf, prior)
        self.assertEqual(rebuilt, prior)
        self.assertEqual(inventory.hierarchy_summary(rebuilt['entries']), prior['hierarchy_summary'])
        prior['entries'][0]['physical_page'] += 1
        with mock.patch.object(inventory.subprocess, 'check_output', return_value='\f'.join(pages) + '\f'):
            with self.assertRaisesRegex(AssertionError, 'source rows changed'):
                inventory.inventory_from_pdf(pdf, prior)
        pdf.read_bytes.return_value = b'changed attachment'
        with mock.patch.object(inventory.subprocess, 'check_output') as extraction:
            with self.assertRaisesRegex(AssertionError, 'Attachment changed'):
                inventory.inventory_from_pdf(pdf, prior)
            extraction.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
