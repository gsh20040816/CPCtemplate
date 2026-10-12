#!/usr/bin/env python3
"""Reject five plausible wrong implementations with the independent oracle."""
import json
from pathlib import Path
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
build = root / 'build/color-components/mutations'
build.mkdir(parents=True, exist_ok=True)
header = (root / 'src/compact/color_components.hpp').read_text().replace('#include "tree.hpp"', '#include "' + str(root / 'src/compact/tree.hpp') + '"')
probe = (root / 'tests/color_components_probe.cpp').read_text()
mutations = [
    ('omit_opposite_boundary', 'v = h.fa[v];', '// omitted boundary'),
    ('reverse_old_delta', 'change(u, c, -value(u, c));', 'change(u, c, value(u, c));'),
    ('stale_color_set', 'pos[c].erase(h.dfn[u]);', '// missing erase'),
    ('exclude_chain_head', '*it >= h.dfn[v]', '*it > h.dfn[v]'),
    ('query_subtree_only', 'value(top(u), col[u])', 'value(u, col[u])'),
]
report = []
for name, old, new in mutations:
    assert header.count(old) == 1
    path = build / (name + '.hpp')
    path.write_text(header.replace(old, new))
    source = build / (name + '.cpp')
    source.write_text(probe.replace('../src/compact/color_components.hpp', str(path)))
    exe = build / name
    subprocess.run([CXX, '-std=c++17', '-O2', str(source), '-o', str(exe)], check=True)
    run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
    assert run.returncode != 0 and 'ColorComponents oracle mismatch' in run.stderr, (name, run)
    report.append({'mutation': name, 'result': 'oracle mismatch', 'returncode': run.returncode})
    print(name, 'rejected', flush=True)
(root / 'verification/color-components-mutations.json').write_text(json.dumps(report, indent=2) + '\n')
