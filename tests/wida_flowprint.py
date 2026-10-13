"""Audit the WIDA printout for Dinic, one project-selection cut, and Dijkstra cost flow."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-flow.md').read_bytes()
fix = root / 'tests/fixtures/wida_flowprint'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '3ebc352fec43201867c290e9d13b34dfa82db384'
text = blob.decode().replace('\r\n', '\n')
fences = [part.split('\n', 1)[1] for part in text.split('```')[1::2]]
flow, cut, gomory, mcf = fences
assert 'struct Flow_' in flow and 'Flow<int> flow(n);' in gomory and 'h[i] += dis[i];' in mcf
reset = '''
    void reset() {
        for (int i = 0; i < (int)ver.size(); i += 2) {
            ver[i].w += ver[i ^ 1].w;
            ver[i ^ 1].w = 0;
        }
    }
'''
flow = flow.replace('\n};\nusing Flow = Flow_<int>;', '\n' + reset + '};\nusing Flow = Flow_<int>;')
out = root / 'build/wida-flowprint'
out.mkdir(parents=True, exist_ok=True)
body = (root / 'tests/wida_flowprint.cpp').read_text().split('static long long ek', 1)[1]
wrapped = '#include <bits/stdc++.h>\nusing namespace std;\n' + flow + '\n' + mcf + '\nstatic long long ek' + body
(out / 'wrapped.cpp').write_text(wrapped)
(out / 'gomory.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + flow + '\n' + gomory)
bare = subprocess.run([CXX, '-std=c++20', '-c', str(out / 'gomory.cpp'), '-o', str(out / 'gomory.o')], text=True, capture_output=True)
assert bare.returncode != 0 and 'Flow' in bare.stderr
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
for mode, flags in [('normal', ['-O2']), ('sanitizer', ['-O1', '-g', '-fsanitize=address,undefined'])]:
    exe = out / mode
    subprocess.run([CXX, '-std=c++20', *flags, str(out / 'wrapped.cpp'), '-o', str(exe)], check=True)
    got = subprocess.run([str(exe), 'flow'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert got.stderr == '' and got.stdout == 'flow\n'
    cut_out = subprocess.run([str(exe), 'cut'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert cut_out.stderr == '' and cut_out.stdout == '0 8 2147483647\n'
    mcf_out = subprocess.run([str(exe), 'mcf'], text=True, capture_output=True, env=env, timeout=30, check=True)
    assert mcf_out.stderr == '' and mcf_out.stdout == '2 7 1 -5\n'
    report.append(dict(mode=mode))
    print(mode, 'PASS', flush=True)
ub = out / 'island'
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(out / 'wrapped.cpp'), '-o', str(ub)], check=True)
island = out / 'island.cpp'
island.write_text(wrapped.replace('string mode = argc > 1 ? argv[1] : "flow";', 'string mode = "island";', 1).replace(
'''    if (mode == "flow") {''',
'''    if (mode == "island") {
        MinCostFlow g(3);
        g.add(0, 1, 1, 1);
        g.add(0, 1, 1, 1);
        auto [flow, cost] = g.flow(0, 1);
        cout << flow << ' ' << cost << '\\n';
        return 0;
    }
    if (mode == "flow") {''', 1))
subprocess.run([CXX, '-std=c++20', '-O1', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=undefined', str(island), '-o', str(ub)], check=True)
bad = subprocess.run([str(ub)], text=True, capture_output=True, env=env, timeout=30)
assert bad.returncode != 0 and 'signed integer overflow' in bad.stderr
report.append(dict(gomory='does not compile', island=bad.stderr.strip().splitlines()[-1]))
print('bounds PASS', flush=True)
import json
(root / 'verification/wida-flowprint.json').write_text(json.dumps(dict(
    scope='Dinic matches Edmonds-Karp on the checked graphs, and reset repeats the same value. The project example prints 0 while the best subset profit is 8; 1E18 becomes INT_MAX. Gomory-Hu uses Flow<int> and does not compile against this alias. Reachable cost-flow samples match, and a second augmentation overflows an unreachable potential. No online AC.',
    blob='3ebc352fec43201867c290e9d13b34dfa82db384', runs=report), indent=2) + '\n')
