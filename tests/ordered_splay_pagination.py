"""Keep OrderedSplay's source-linked book chunks at complete-method boundaries."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = (root / 'src/compact/splay.hpp').read_text()
lines = source.splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith('struct OrderedSplay'))
# Ignore ordinary C++ strings, character literals, and comments before counting.
lex = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', re.S)
depth = 0
at = [0] * (len(lines) + 1)
for i, line in enumerate(lines):
    # This header contains no multiline comments or raw strings; fail closed if added.
    assert '/*' not in line and 'R"' not in line
    for token in lex.finditer(line):
        if token[0] == '{':
            depth += 1
        elif token[0] == '}':
            depth -= 1
    at[i + 1] = depth
end = next(i for i in range(start + 2, len(lines)) if lines[i] == '};') + 1
text = (root / 'docs/generated.tex').read_text()
chunks = [(int(a) - 1, int(b)) for a, b in re.findall(
    r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,[^\]]*)?\]\{\.\./src/compact/splay\.hpp\}', text)]
assert len(chunks) > 1, 'Long type lost its method-aware chunks'
assert chunks[0][0] == start and chunks[-1][1] == end
assert all(a[1] == b[0] for a, b in zip(chunks, chunks[1:])), 'Missing or duplicated source lines'
for lo, hi in chunks:
    assert lo < hi
    if lo != start:
        assert at[lo] == 1, 'Split inside a method or nested object'
        assert re.match(r'    (?:void|int|long long|ll|optional<ll>) \w+\(', lines[lo]), 'Split inside a declaration'
    if hi != end:
        assert at[hi] == 1
print('OrderedSplay book chunks cover the source once and split only between complete methods PASS')
