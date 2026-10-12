#!/usr/bin/env python3
"""Reject six plausible wrong implementations with the independent oracle."""
import json
from pathlib import Path
import subprocess
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
build = root / 'build/color-max/mutations'
build.mkdir(parents=True, exist_ok=True)
header = (root / 'src/compact/color_max.hpp').read_text().replace('#include "tree.hpp"', '#include "' + str(root / 'src/compact/tree.hpp') + '"')
probe = (root / 'tests/color_max_probe.cpp').read_text()
mutations = [
    ('erase_all_equal', 'light[p][old].erase(it);', 'light[p][old].erase(before);'),
    ('wrong_old_color', 'int old = col[t];', 'int old = col[u];'),
    ('stale_contribution', 'light[p][col[t]].insert(down(t));', 'light[p][col[t]].insert(before);'),
    ('ignore_color_barrier', 'r = min(r, *it - 1);', 'r = r;'),
    ('ignore_chain_end', 'int r = tail[h.top[u]];', 'int r = h.n;'),
    ('query_subtree_only', 'down(top(u))', 'down(u)'),
]
report = []
for name, old, new in mutations:
    assert header.count(old) == 1
    path = build / (name + '.hpp')
    path.write_text(header.replace(old, new))
    source = build / (name + '.cpp')
    source.write_text(probe.replace('../src/compact/color_max.hpp', str(path)))
    exe = build / name
    subprocess.run([CXX, '-std=c++17', '-O2', str(source), '-o', str(exe)], check=True)
    run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=30)
    assert run.returncode != 0 and ('ColorMax oracle mismatch' in run.stderr or ('Assertion' in run.stderr and 'failed' in run.stderr)), (name, run)
    report.append({'mutation': name, 'result': 'oracle mismatch' if 'oracle mismatch' in run.stderr else 'internal invariant rejection', 'returncode': run.returncode})
    print(name, 'rejected', flush=True)
(root / 'verification/color-max-mutations.json').write_text(json.dumps(report, indent=2) + '\n')
