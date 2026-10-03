#!/usr/bin/env python3
"""Check the bounded two-section migration; no new algorithm or OJ claim."""
from pathlib import Path
import hashlib
import json
import os
import re


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None, '', '0'):
        raise SystemExit('Validation requires Python assertions')
    root = Path(__file__).resolve().parents[1]
    fixtures = root / 'tests/fixtures/floor-knowledge-migration'
    data = json.loads((fixtures / 'manifest.json').read_text())
    original = (fixtures / 'original.tex').read_text()
    assert hashlib.sha256(original.encode()).hexdigest() == data['original_sections_sha256']
    assert data['base_commit'] == '4df4e2b5c1edbd146168b9cae6767ef05d67e2d6'
    assert len(data['changes']) == 7
    expected = original
    for change in data['changes']:
        assert expected.count(change['old']) == 1
        expected = expected.replace(change['old'], change['new'])
    actual = (root / 'docs/knowledge-floor-sums.tex').read_text()
    assert actual == expected
    assert hashlib.sha256(actual.encode()).hexdigest() == data['candidate_sha256']
    labels = re.findall(r'\\label\{(knowledge-[^}]+)\}', actual)
    assert labels == ['knowledge-floor-sum', 'knowledge-floor-moments']
    math = (root / 'docs/mathematics.tex').read_text()
    assert math.count(r'\input{knowledge-floor-sums.tex}') == 1
    for title in re.findall(r'\\section\{([^}]+)\}', original):
        assert r'\section{' + title + '}' not in math
    mapping = json.loads((root / 'docs/knowledge-taxonomy.json').read_text())
    rows = [row for row in mapping['entries'] if row['label'] in labels]
    assert [row['label'] for row in rows] == labels
    assert all(row['source'] == 'docs/knowledge-floor-sums.tex' and
               row['path'] == 'math/number-theory/euclidean.md' for row in rows)
    for target in ('compact-floor_sum', 'compact-floor_moments', 'usage-example-157'):
        assert r'\ref{' + target + '}' in actual
        assert r'\pageref{' + target + '}' in actual
    for name in ('generated.tex', 'volume-mathematics.tex'):
        rendered = (root / 'docs' / name).read_text()
        sequence = re.findall(r'\\label\{(knowledge-[^}]+)\}', rendered)
        index = sequence.index(labels[0])
        assert sequence[index:index + 2] == labels
        assert all(sequence.count(label) == 1 for label in labels)
    legacy = (root / 'docs/mathematics-legacy.tex').read_text()
    assert len(re.findall(r'^\\section\{', legacy, re.M)) == 70
    assert not any(label in legacy for label in labels)
    audit = (root / 'docs/KNOWLEDGE-TAXONOMY.md').read_text()
    count = mapping['scope']['classified_section_count']
    assert f'**{count} 个带标签节**' in audit
    assert f'{count} 个知识标签' in audit
    print('Floor knowledge migration: two sections preserved except seven explicit amendments; '
          'unique adjacent routing, links, 70 legacy sections and prose counts PASS')


if __name__ == '__main__':
    main()
