"""Independent scope regression: exact exclusions must not become broad deletions."""
from pathlib import Path
import json
import sys
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from template_scope import excluded_driver

policy = json.loads((root / 'docs/basic-template-exclusions.json').read_text())
assert policy['approval'].endswith('/issues/2#issuecomment-5907178580')
assert {(r['judge'], r['problem']) for r in policy['problems']} == {
    ('luogu', 'P1226'), ('luogu', 'P1177'), ('luogu', 'P3374')}
assert len(policy['problems']) == 3
for problem in ('P1226', 'P1177', 'P3374'):
    assert excluded_driver(f'verify/luogu/{problem}.compact.cpp', policy)
    assert not excluded_driver(f'verify/luogu/{problem}0.compact.cpp', policy)
    assert not excluded_driver(f'verify/qoj/{problem}.compact.cpp', policy)
    assert not excluded_driver(f'archive/luogu/{problem}.compact.cpp', policy)
for problem in ('P3367', 'P3377', 'P2617', 'P4721', 'P5245'):
    assert not excluded_driver(f'verify/luogu/{problem}.compact.cpp', policy)
cat = json.loads((root / 'docs/catalog.json').read_text())
by_name = {r[1]: r for r in cat}
assert len(cat) >= 200
for symbol in ('dsu', 'RollbackDSU', 'Fenwick', 'ModInt', 'Mod64', 'NttConvolution', 'FpsPower'):
    assert symbol in by_name
assert '第 k 小' in by_name['Fenwick'][2]
source = (root / 'src/compact/data_structure.hpp').read_text()
for method in ('add(', 'sum(', 'query(', 'kth('):
    assert method in source
inventory = json.loads((root / 'docs/template-problems.json').read_text())
assert inventory['excluded_basic_problems'] == policy
assert {r['symbol'] for r in inventory['algorithms']} == set(by_name)
for row in inventory['algorithms']:
    assert row['title'] == by_name[row['symbol']][2]
    assert all(not excluded_driver(d['driver'], policy) for d in row['candidate_drivers'])
assert any(d['driver'] == 'verify/luogu/P3367.compact.cpp'
           for r in inventory['algorithms'] if r['symbol'] == 'dsu'
           for d in r['candidate_drivers'])
assert len(json.loads((root / 'docs/usage-examples.json').read_text())) >= 198
# Exercise the real generator against synthetic drivers and a source ledger.
# A removed basic driver must not reappear merely because it mentions Fenwick.
with tempfile.TemporaryDirectory() as tmp:
    fixture = Path(tmp)
    for directory in ('tools', 'docs', 'verification', 'verify/luogu', 'verify/api'):
        (fixture / directory).mkdir(parents=True)
    for name in ('template_inventory.py', 'template_scope.py'):
        shutil.copyfile(root / 'tools' / name, fixture / 'tools' / name)
    shutil.copyfile(root / 'docs/basic-template-exclusions.json', fixture / 'docs/basic-template-exclusions.json')
    (fixture / 'docs/catalog.json').write_text(json.dumps([by_name['Fenwick'], by_name['dsu']]))
    (fixture / 'verification/oj.json').write_text('[]')
    ledger = 'source,source_path,page,topic,status\nWIDA,basic-source,,basic,pending\n'
    (fixture / 'docs/coverage.csv').write_text(ledger)
    for problem in ('P1226', 'P1177', 'P3374', 'P33740', 'P2617', 'P3367'):
        (fixture / f'verify/luogu/{problem}.compact.cpp').write_text('Fenwick dsu;')
    (fixture / 'verify/api/demo.compact.cpp').write_text('Fenwick dsu;')
    subprocess.run([sys.executable, str(fixture / 'tools/template_inventory.py')], check=True, capture_output=True)
    result = json.loads((fixture / 'docs/template-problems.json').read_text())
    for row in result['algorithms']:
        assert {Path(d['driver']).name for d in row['candidate_drivers']} == {
            'P33740.compact.cpp', 'P2617.compact.cpp', 'P3367.compact.cpp'}
    assert len(result['unresolved_upstream_topics']) == 1
    assert (fixture / 'docs/coverage.csv').read_text() == ledger
print('Basic template scope: three exact exclusions, advanced dependencies, DSU and history scope preserved PASS')
