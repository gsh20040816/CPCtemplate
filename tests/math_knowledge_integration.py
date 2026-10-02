#!/usr/bin/env python3
"""Check shared knowledge inclusion, routing, and local template references.

Run after tools/book.py and tools/volumes.py. This is a document integration
check, not a PDF visual inspection or an algorithm correctness certificate.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
volume = (ROOT / 'docs/volume-mathematics.tex').read_text()
labels = set(re.findall(r'\\label\{([^}]+)\}', volume))
knowledge_labels = []
for filename in ('knowledge-combinatorics.tex', 'knowledge-probability-games.tex',
                 'knowledge-mobius.tex', 'knowledge-orbits.tex', 'knowledge-lte.tex'):
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
assert len(knowledge_labels) == 16
for rendered in (omnibus, volume):
    assert r'\newpage' + '\n\n' + r'\section{升幂引理}' in rendered, 'LTE page break must precede taxonomy heading'
for label in knowledge_labels:
    assert volume.count(r'\label{' + label + '}') == 1, label
    assert omnibus.count(r'\label{' + label + '}') == 1, label
    assert r'\label{' + label + '}' not in legacy, label
for other in ('strings', 'data-structures', 'graphs', 'geometry', 'misc'):
    text = (ROOT / f'docs/volume-{other}.tex').read_text()
    assert not any(r'\label{' + label + '}' in text for label in knowledge_labels), other
print(f'PASS: {len(knowledge_labels)} knowledge sections classified once in both books; authored text preserved; references resolve')
