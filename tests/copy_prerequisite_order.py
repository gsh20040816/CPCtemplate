"""Every flat usage copy list must contain its prerequisites before its users."""
from pathlib import Path
import copy
import json
import sys

root = Path(__file__).resolve().parents[1]
deps = json.loads((root / 'docs/template-dependencies.json').read_text())
rows = json.loads((root / 'docs/usage-examples.json').read_text())
sys.path.insert(0, str(root / 'tools'))
from template_dependencies import reference
link = reference('bridge_component_forest')
assert r'bridge\_\allowbreak{}component\_\allowbreak{}forest' in link
assert r'\hyperref[compact-bridge_component_forest]' in link
assert r'\pageref{compact-bridge_component_forest}' in link

def validate(row):
    required = row['requires']
    index = {name: i for i, name in enumerate(required)}
    assert len(index) == len(required), (row['id'], 'duplicate component')
    for name in required:
        assert name in deps, (row['id'], 'unknown component', name)
        for need in deps[name]:
            assert need in index, (row['id'], name, 'missing', need)
            assert index[need] < index[name], (row['id'], name, 'must follow', need)

for row in rows:
    validate(row)
for ident, mutate in [
    ('example-3', lambda r: r['requires'].remove('SCC')),
    ('example-176', lambda r: r['requires'].reverse()),
    ('example-216', lambda r: r['requires'].append('ModInt')),
]:
    broken = copy.deepcopy(next(r for r in rows if r['id'] == ident))
    mutate(broken)
    try:
        validate(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError(('Invalid copy list accepted', ident))
print(f'Copy prerequisites: all {len(rows)} lists closed, ordered and unique; negative controls PASS')
