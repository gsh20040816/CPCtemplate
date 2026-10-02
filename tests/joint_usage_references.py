"""Joint coverage needs a direct call and closed references in every category book."""
from pathlib import Path
import copy
import json
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from usage_examples import explicitly_calls, records

assert explicitly_calls('ModInt', 'auto x = ModInt<10007>(a).pow(n);')
assert explicitly_calls('euler_phi', 'auto x = euler_phi(n);')
assert explicitly_calls('Box', 'auto x = Box<int>::make(n);')
for text in ['using Z = ModInt<10007>;', 'Binomial<10007> c(k);',
             '// ModInt<10007>(a)\nreturn 0;', '/* ModInt<10007>(a) */',
             'puts("ModInt<10007>(a)");']:
    assert not explicitly_calls('ModInt', text)

usages = json.loads((root / 'docs/usage-examples.json').read_text())
volumes = json.loads((root / 'docs/volumes.json').read_text())

def validate(volume):
    symbols = set(volume['entries']) | set(volume['dependencies'])
    for usage in usages:
        if symbols & set(usage.get('also_covers', [])):
            assert usage['symbol'] in symbols, (volume['id'], usage['id'])

for volume in volumes:
    validate(volume)
# Prove that dropping the cross-class owner is rejected, not silently ignored.
for name in ['data-structures', 'graphs']:
    volume = next(v for v in volumes if v['id'] == name)
    assert 'ModInt' in volume['dependencies'] and 'Binomial' in volume['dependencies']
    broken = copy.deepcopy(volume)
    broken['dependencies'].remove('Binomial')
    try:
        validate(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError('Dangling joint-use owner was accepted')
all_primary = [s for v in volumes for s in v['entries']]
assert len(all_primary) == len(set(all_primary))
assert set(all_primary) == {r[1] for r in json.loads((root / 'docs/catalog.json').read_text())}
assert len(records()) == len(usages)
print('Joint uses: direct-call checks, owner closure, negative controls and unique primary categories PASS')
