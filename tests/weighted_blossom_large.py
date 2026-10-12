"""Large primal/dual certificates and nested blossom path coverage."""
from compiler_config import CXX
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
build = root / 'build/weighted-blossom'
build.mkdir(exist_ok=True)
header = (root / 'src/compact/weighted_blossom.hpp').read_text()
cxx = CXX
forms = {}
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = build / ('large-' + mode)
    subprocess.run([cxx, '-std=c++20', *flags, str(root / 'tests/weighted_blossom_large.cpp'), '-o', str(exe)], check=True)
    run = subprocess.run([str(exe)], check=True, capture_output=True, text=True, timeout=180)
    assert not run.stderr, run.stderr
    assert run.stdout.strip() == '16 large primal/dual certificate checks PASS'
    forms[mode] = run.stdout.strip()
    print(mode, run.stdout.strip(), flush=True)

instrumented = header.replace('#pragma once', '#pragma once\ninline long long shrink_count = 0, nested_count = 0, expand_count = 0;', 1)
instrumented = instrumented.replace('    void shrink(int u, int root, int v)\n    {', '    void shrink(int u, int root, int v)\n    {\n        shrink_count++;')
instrumented = instrumented.replace('        set_base(b, b);', '        for (int x : flower[b])\n            if (x > n) nested_count++;\n        set_base(b, b);')
instrumented = instrumented.replace('    void expand(int b)\n    {', '    void expand(int b)\n    {\n        expand_count++;')
(build / 'instrumented.hpp').write_text(instrumented)
source = (root / 'tests/weighted_blossom.cpp').read_text()
source = source.replace('#include "../src/compact/weighted_blossom.hpp"', '#include "instrumented.hpp"')
source = source.replace('    return 0;\n}', '    cout << shrink_count << " shrinks " << nested_count << " nested children " << expand_count << " expansions\\n";\n    return 0;\n}')
assert 'instrumented.hpp' in source
(build / 'instrumented.cpp').write_text(source)
exe = build / 'instrumented'
subprocess.run([cxx, '-std=c++20', '-O2', str(build / 'instrumented.cpp'), '-o', str(exe)], check=True)
run = subprocess.run([str(exe)], check=True, capture_output=True, text=True, timeout=180)
assert not run.stderr, run.stderr
counts = re.search(r'(\d+) shrinks (\d+) nested children (\d+) expansions', run.stdout)
assert counts and all(int(x) > 0 for x in counts.groups())
print(run.stdout, end='')
report = dict(status='pass', source_sha256=hashlib.sha256(header.encode()).hexdigest(),
              large=dict(n=400, graphs=8, modes=2, checks_per_build=16, forms=forms,
                         oracle='Independent primal witness, matching LP dual feasibility and equality'),
              instrumentation=dict(checks=28546, shrinks=int(counts[1]), nested_children=int(counts[2]), expansions=int(counts[3])),
              scope='Local checks, not an online rank or unconditional implementation proof')
(root / 'verification/weighted-blossom-large.json').write_text(json.dumps(report, indent=2) + '\n')
