#!/usr/bin/env python3
"""Check explicit knowledge mappings against sources and pinned navigation.

This is a data/scope check. It does not claim PDF visual validation, algorithm
correctness, new template coverage, or new online judge verification.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    'docs/knowledge-combinatorics.tex',
    'docs/knowledge-probability-games.tex',
    'docs/knowledge-mobius.tex',
    'docs/knowledge-orbits.tex',
    'docs/knowledge-lte.tex',
    'docs/knowledge-lagrange.tex',
    'docs/knowledge-state-recurrence.tex',
    'docs/knowledge-inclusion.tex',
    'docs/knowledge-floor-sums.tex',
    'docs/knowledge-matrix-tree.tex',
)
SECTION = re.compile(r'(?m)(?=^\\section\{)')
LABEL = re.compile(r'\\label\{(knowledge-[^}]+)\}')


def pinned_navigation(text):
    """Read the local navigation independently of the knowledge generator."""
    nav = text.split('\nnav:\n', 1)[1].split('\n# Theme', 1)[0]
    stack, leaves = [], []
    for line in nav.splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'( +)- (.*?):\s*(.*?)\s*', line)
        assert match, ('unrecognized pinned navigation line', line)
        indent, title, path = len(match[1]), match[2], match[3]
        while stack and stack[-1][0] >= indent:
            stack.pop()
        assert not stack or indent == stack[-1][0] + 2, line
        hierarchy = [row[1] for row in stack] + [title]
        if path:
            assert path.endswith('.md'), path
            leaves.append(dict(path=path, hierarchy=hierarchy, order=len(leaves)))
        else:
            stack.append((indent, title))
    assert len({row['path'] for row in leaves}) == len(leaves)
    return leaves


def source_sections(sources):
    sections = {}
    for source, text in sources.items():
        fragments = SECTION.split(text)[1:]
        assert fragments, (source, 'no sections')
        for fragment in fragments:
            labels = LABEL.findall(fragment)
            assert len(labels) == 1, (source, 'one knowledge label per section', labels)
            label = labels[0]
            assert label not in sections, ('duplicate source label', label)
            # Each section's identity is explicit at its header, not guessed
            # from its title or incidental references in the body.
            assert LABEL.search(fragment.split('\n', 1)[0]), (source, label)
            sections[label] = source
    assert len(sections) == 23, ('bounded knowledge section count', len(sections))
    return sections


def validate(data, taxonomy, sources):
    assert data['schema_version'] == 1
    assert data['reference_commit'] == taxonomy['reference_commit']
    assert data['reference_source_sha256'] == taxonomy['source_sha256']
    scope = data['scope']
    assert len(scope['source_files']) == len(set(scope['source_files']))
    assert set(scope['source_files']) == set(SOURCE_FILES) == set(sources)
    assert scope['classified_section_count'] == 23
    assert scope['legacy_source'] == 'docs/mathematics.tex'
    assert scope['legacy_sections_classified'] is False
    assert scope['classification_only'] is True
    assert scope['new_algorithm_coverage'] is False
    assert scope['new_oj_verification'] is False
    assert scope['note'].strip()
    by_path = {row['path']: row for row in taxonomy['navigation']}
    sections = source_sections(sources)
    entries = data['entries']
    assert len(entries) == len(sections)
    labels = [entry['label'] for entry in entries]
    assert len(labels) == len(set(labels)), 'duplicate mapping label'
    assert set(labels) == set(sections), 'missing or unknown knowledge label'
    for entry in entries:
        label, source, path = entry['label'], entry['source'], entry['path']
        assert source in sources, (label, 'unknown or noncanonical source', source)
        assert sections[label] == source, (label, 'label belongs to a different source')
        assert path in by_path, (label, 'unknown primary leaf', path)
        hierarchy = by_path[path]['hierarchy']
        graph_labels = {'knowledge-matrix-tree-weighted', 'knowledge-matrix-tree-mod'}
        if label in graph_labels:
            assert path == 'graph/matrix-tree.md' and hierarchy == ['图论', '矩阵树定理'], (label, hierarchy)
        else:
            assert len(hierarchy) == 3 and hierarchy[0] == '数学', (label, hierarchy)
        assert isinstance(entry.get('page_break_before', False), bool)
        assert entry['relation'] in ('direct', 'application', 'composite')
        assert entry['note'].strip(), (label, 'classification rationale missing')
        additional = entry['additional']
        assert len(additional) == len(set(additional)), (label, 'duplicate additional leaf')
        assert path not in additional, (label, 'primary repeated as additional')
        assert all(page in by_path for page in additional), (label, 'unknown additional leaf')
        # Hierarchy/order must be derived from the fixed navigation by path.
        assert not {'hierarchy', 'order', 'title'} & entry.keys(), label
    return sections


class KnowledgeTaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'docs/knowledge-taxonomy.json').read_text())
        cls.taxonomy = json.loads((ROOT / 'docs/oi-taxonomy.json').read_text())
        cls.sources = {source: (ROOT / source).read_text() for source in SOURCE_FILES}

    def reject(self, mutate):
        data = copy.deepcopy(self.data)
        mutate(data)
        with self.assertRaises(AssertionError):
            validate(data, self.taxonomy, self.sources)

    def test_fixed_source_and_generated_navigation_agree(self):
        source = ROOT / 'docs/references/oi-wiki-mkdocs.yml'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         self.data['reference_source_sha256'])
        self.assertEqual(pinned_navigation(source.read_text()), self.taxonomy['navigation'])

    def test_all_registered_sections_have_one_known_primary_leaf(self):
        self.assertEqual(len(validate(self.data, self.taxonomy, self.sources)), 23)
        observed = {path.relative_to(ROOT).as_posix()
                    for path in (ROOT / 'docs').glob('knowledge-*.tex')}
        self.assertEqual(observed, set(SOURCE_FILES), 'new source needs explicit classification')
        legacy = (ROOT / 'docs/mathematics.tex').read_text()
        for source in SOURCE_FILES:
            self.assertEqual(legacy.count(r'\input{' + Path(source).name + '}'), 1)
        self.assertTrue(SECTION.search(legacy), 'legacy unclassified sections still exist')
        self.assertFalse(LABEL.search(legacy), 'legacy source is outside this bounded map')

    def test_graph_exception_is_bound_to_matrix_tree_labels(self):
        self.reject(lambda data: data['entries'][0].update(path='graph/matrix-tree.md'))
        self.reject(lambda data: data['entries'][-1].update(path='math/number-theory/euclidean.md'))

    def test_duplicate_and_missing_labels_are_rejected(self):
        self.reject(lambda data: data['entries'].append(copy.deepcopy(data['entries'][0])))
        self.reject(lambda data: data['entries'].pop())
        self.reject(lambda data: data['entries'].__setitem__(1, copy.deepcopy(data['entries'][0])))
        self.reject(lambda data: data['entries'][0].__setitem__('label', 'knowledge-unknown'))

    def test_invalid_mismatched_and_legacy_sources_are_rejected(self):
        for source in ('docs/missing.tex', 'docs/mathematics.tex', '../docs/knowledge-combinatorics.tex',
                       'docs/../docs/knowledge-combinatorics.tex', 'docs/knowledge-mobius.tex'):
            with self.subTest(source=source):
                self.reject(lambda data: data['entries'][0].__setitem__('source', source))
        self.reject(lambda data: data['scope']['source_files'].append(SOURCE_FILES[0]))
        self.reject(lambda data: data['entries'][-1].__setitem__('page_break_before', 'true'))

    def test_invalid_and_duplicate_paths_are_rejected(self):
        for path in ('math/does-not-exist.md', 'math/number-theory/', 'index.md'):
            with self.subTest(path=path):
                self.reject(lambda data: data['entries'][0].__setitem__('path', path))
        for additional in (['math/missing.md'], ['math/poly/ogf.md'] * 2,
                           [self.data['entries'][0]['path']]):
            with self.subTest(additional=additional):
                self.reject(lambda data: data['entries'][0].__setitem__('additional', additional))

    def test_title_edits_do_not_drive_classification(self):
        renamed = {source: re.sub(r'(?m)^\\section\{[^}]+\}',
                                 lambda match: r'\section{不参与路由的显示标题}', text)
                   for source, text in self.sources.items()}
        self.assertEqual(validate(self.data, self.taxonomy, renamed),
                         validate(self.data, self.taxonomy, self.sources))

    def test_duplicate_source_labels_are_rejected(self):
        sources = self.sources.copy()
        sources[SOURCE_FILES[0]] += '\n' + sources[SOURCE_FILES[0]]
        with self.assertRaises(AssertionError):
            validate(self.data, self.taxonomy, sources)

    def test_scope_cannot_claim_full_legacy_or_new_coverage(self):
        for field in ('legacy_sections_classified', 'new_algorithm_coverage', 'new_oj_verification'):
            with self.subTest(field=field):
                self.reject(lambda data: data['scope'].__setitem__(field, True))
        self.reject(lambda data: data['scope'].__setitem__('classification_only', False))

    def test_snapshot_identity_mismatch_is_rejected(self):
        self.reject(lambda data: data.__setitem__('reference_source_sha256', '0' * 64))
        self.reject(lambda data: data.__setitem__('reference_commit', '0' * 40))

    def test_audit_documents_every_entry_and_the_legacy_limit(self):
        audit = (ROOT / 'docs/KNOWLEDGE-TAXONOMY.md').read_text()
        for entry in self.data['entries']:
            for field in ('label', 'source', 'path'):
                self.assertIn('`' + entry[field] + '`', audit)
        self.assertIn('`mathematics.tex` 的其余历史知识节尚未逐项分类', audit)
        self.assertIn('不新增算法、模板覆盖或 OJ 验证记录', audit)


if __name__ == '__main__':
    unittest.main(verbosity=2)
