#!/usr/bin/env python3
"""Check shared knowledge inclusion, routing, and local template references.

Run after tools/book.py and tools/volumes.py. This is a document integration
check, not a PDF visual inspection or an algorithm correctness certificate.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not __debug__:
    raise RuntimeError('Document integration checks require Python assertions')
registration = json.loads((ROOT / 'docs/knowledge-taxonomy.json').read_text())
main = (ROOT / 'docs/main.tex').read_text()
math = (ROOT / 'docs/mathematics.tex').read_text()
assert main.count(r'\input{mathematics-legacy.tex}') == 1
sys.path.insert(0, str(ROOT / 'tools'))
from knowledge_layout import classified_fragments, legacy_knowledge
from taxonomy_layout import LEVELS
mapped = {row['symbol']: row for row in classified_fragments()}
omnibus = (ROOT / 'docs/generated.tex').read_text()
legacy = (ROOT / 'docs/mathematics-legacy.tex').read_text()
assert legacy == legacy_knowledge()
volumes = {key: (ROOT / f'docs/volume-{key}.tex').read_text() for key in
           ('strings', 'mathematics', 'data-structures', 'graphs', 'geometry', 'misc')}
owner = {'数学': 'mathematics', '图论': 'graphs'}
volume = volumes['mathematics']
knowledge_labels = []
for source in registration['scope']['source_files']:
    filename = Path(source).name
    file_rows = [row for row in mapped.values() if row['symbol'] in re.findall(r'\\label\{(knowledge-[^}]+)\}', (ROOT / source).read_text())]
    owners = {owner[row['taxonomy']['hierarchy'][0]] for row in file_rows}
    assert len(owners) == 1, filename
    volume = volumes[next(iter(owners))]
    labels = set(re.findall(r'\\label\{([^}]+)\}', volume))
    assert math.count(r'\input{' + filename + '}') == 1, filename
    content = (ROOT / 'docs' / filename).read_text()
    # Only heading levels change; all authored mathematical text is preserved.
    for section in re.split(r'(?=\\section\{)', content)[1:]:
        label = re.findall(r'\\label\{(knowledge-[^}]+)\}', section)[0]
        row = mapped[label]
        depth = len(row['taxonomy']['hierarchy']) - 1
        levels = LEVELS + ['paragraph', 'subparagraph']
        adjusted = re.sub(r'\\((?:sub)*)section\{',
                          lambda m: '\\' + levels[depth + len(m[1]) // 3] + '{', section)
        assert adjusted.strip() in volume, (filename, 'authored section changed during routing')
        assert adjusted.strip() in omnibus, (filename, 'omnibus content drift')
    local_labels = re.findall(r'\\label\{(knowledge-[^}]+)\}', content)
    assert local_labels, filename
    knowledge_labels.extend(local_labels)
    refs = set(re.findall(r'\\(?:page)?ref\{([^}]+)\}', content))
    assert refs <= labels, (filename, 'unresolved references', refs - labels)
    for target in refs:
        if target.startswith('compact-'):
            assert r'\ref{' + target + '}' in content, (target, 'missing section')
            assert r'\pageref{' + target + '}' in content, (target, 'missing page')
    assert r'\chapter{' not in content, filename
assert len(knowledge_labels) == len(set(knowledge_labels))
assert set(knowledge_labels) == {row['label'] for row in registration['entries']}
assert len(knowledge_labels) == registration['scope']['classified_section_count']
for rendered in (omnibus, volumes['mathematics']):
    assert r'\newpage' + '\n\n' + r'\section{升幂引理}' in rendered, 'LTE page break must precede taxonomy heading'
    assert r'\newpage' + '\n\n' + r'\section{Lagrange 反演}' in rendered, 'Lagrange page break must precede taxonomy heading'
    assert r'\newpage' + '\n\n' + r'\section{特征多项式}' in rendered, 'State recurrence page break must precede taxonomy heading'
for label in knowledge_labels:
    expected = owner[mapped[label]['taxonomy']['hierarchy'][0]]
    for key, text in volumes.items():
        assert text.count(r'\label{' + label + '}') == (1 if key == expected else 0), (label, key)
    assert omnibus.count(r'\label{' + label + '}') == 1, label
    assert r'\label{' + label + '}' not in legacy, label
print(f'PASS: {len(knowledge_labels)} knowledge sections once in omnibus and owning volume; authored text and references preserved')
