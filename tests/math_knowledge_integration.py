#!/usr/bin/env python3
"""Check shared knowledge inclusion, routing, and local template references.

Run after tools/book.py and tools/volumes.py. This is a document integration
check, not a PDF visual inspection or an algorithm correctness certificate.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / 'docs/main.tex').read_text()
math = (ROOT / 'docs/mathematics.tex').read_text()
assert main.count(r'\input{mathematics.tex}') == 1
volume = (ROOT / 'docs/volume-mathematics.tex').read_text()
labels = set(re.findall(r'\\label\{([^}]+)\}', volume))
knowledge_labels = []
for filename in ('knowledge-combinatorics.tex', 'knowledge-probability-games.tex'):
    assert math.count(r'\input{' + filename + '}') == 1, filename
    content = (ROOT / 'docs' / filename).read_text()
    # Routing may insert whitespace between sections and discard leading comments.
    for section in re.split(r'(?=\\section\{)', content)[1:]:
        assert section.strip() in volume, (filename, 'authored section changed during routing')
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
assert len(knowledge_labels) == len(set(knowledge_labels)) == 8
for label in knowledge_labels:
    assert volume.count(r'\label{' + label + '}') == 1, label
for other in ('strings', 'data-structures', 'graphs', 'geometry', 'misc'):
    text = (ROOT / f'docs/volume-{other}.tex').read_text()
    assert not any(r'\label{' + label + '}' in text for label in knowledge_labels), other
print('PASS: eight knowledge sections shared once; math-only routing; section/page references resolve')
