#!/usr/bin/env python3
"""Check ACL review metadata, not algorithm correctness or current OJ status."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT / 'docs/acl-coverage.json').read_text())
review = (ROOT / 'docs/ACL-REVIEW.md').read_text()
modules = {item['module']: item for item in audit['modules']}
assert len(modules) == len(audit['modules']) == 12
assert sorted(modules) == audit['public_modules']

# Fixed upstream fingerprints and the original local snapshot are historical
# evidence. Updating current paths must not silently replace that evidence.
provenance = {
    'reference_commit': audit['reference_commit'],
    'reference_license': audit['reference_license'],
    'public_modules': audit['public_modules'],
    'internal_modules': audit['internal_modules'],
    'reference_sha256': {name: item['reference_sha256'] for name, item in modules.items()},
    'local_snapshot_commit': audit['local_snapshot_commit'],
    'local_source_sha256': audit['local_source_sha256'],
}
digest = hashlib.sha256(json.dumps(provenance, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
assert digest == '45c8b5bca9e78e4cd72eda754b2712e3475206eff1ea648dce9747bbc0406570'
assert 'Historical' in audit['local_snapshot_scope']
assert 'no algorithm run' in audit['metadata_review']['scope']

table = [line for line in review.splitlines() if line.startswith('| [')]
assert len(table) == len(modules)
for item, line in zip(audit['modules'], table):
    name = item['module']
    reference = f"{audit['reference_repository']}/blob/{audit['reference_commit']}/atcoder/{name}.hpp"
    assert item['reference'] == reference, name
    assert re.fullmatch('[0-9a-f]{64}', item['reference_sha256']), name
    assert len(item['local']) == len(set(item['local'])), name
    links = '、'.join(f'[{Path(path).name}](../{path})' for path in item['local'])
    expected = f"| [{name}]({reference}) | {item['category']} | {item['status']} | {links} |"
    assert line == expected, (name, 'table differs from machine record')
    for path in item['local']:
        assert path.startswith('src/compact/') and path.endswith('.hpp'), path
        assert (ROOT / path).is_file(), path
    assert item['notes'].strip()
    assert isinstance(item['gaps'], list)
    assert f'### {name}\n' in review, name

# These are implementation-location checks. Finding a declaration is not a
# correctness test or permission to inherit another component's AC evidence.
expected_paths = {
    'lazysegtree': ['src/compact/lazy_segtree.hpp'],
    'math': ['src/compact/mod64.hpp', 'src/compact/extended_gcd.hpp',
             'src/compact/mod_inverse.hpp', 'src/compact/crt_merge.hpp',
             'src/compact/floor_sum.hpp'],
    'modint': ['src/compact/number_theory.hpp', 'src/compact/dynamic_modint.hpp'],
    'convolution': ['src/compact/ntt_convolution.hpp', 'src/compact/convolution_i64.hpp'],
}
for name, paths in expected_paths.items():
    assert modules[name]['local'] == paths, name
declarations = {
    'lazy_segtree.hpp': r'struct\s+lazy_segtree\b',
    'mod64.hpp': r'struct\s+Mod64\b',
    'extended_gcd.hpp': r'__int128_t\s+extended_gcd\(',
    'mod_inverse.hpp': r'long long\s+mod_inverse\(',
    'crt_merge.hpp': r'bool\s+crt_merge\(',
    'floor_sum.hpp': r'__int128_t\s+floor_sum\(',
    'number_theory.hpp': r'struct\s+ModInt\b',
    'dynamic_modint.hpp': r'struct\s+mint\b',
    'ntt_convolution.hpp': r'struct\s+NttConvolution\b',
    'convolution_i64.hpp': r'\bconvolution_i64\(',
}
for name, pattern in declarations.items():
    assert re.search(pattern, (ROOT / 'src/compact' / name).read_text()), name

assert audit['composition_probe_result'] == 'fixed_local_regression_recorded'
assert (ROOT / audit['composition_probe']).is_file()
historical = audit['historical_composition_probe']
assert historical['result'] == 'compile_failure_observed'
assert historical['log'] == 'verification/acl-fenwick-modint-probe.txt'
assert (ROOT / historical['log']).is_file()
for path in audit['composition_probe_evidence']:
    assert (ROOT / path).is_file(), path
for name, terms in {
    'lazysegtree': ['线上'],
    'math': ['2^32', '2^64'],
    'modint': ['在线'],
    'convolution': ['线上', '排名'],
    'maxflow': ['在线', 'edges()'],
    'mincostflow': ['线上'],
    'string': ['SA-IS'],
}.items():
    gaps = ' '.join(modules[name]['gaps'])
    assert all(term in gaps for term in terms), (name, 'unresolved scope lost')
assert '函数复合驱动在线待提交' not in modules['segtree']['notes']
assert '当前没有按容量' not in modules['maxflow']['notes']
assert '本地验证通过' in modules['lazysegtree']['status']
assert '静态与动态实现已有' in modules['modint']['status']


# Static unit inversion is an implemented API extension, not new online evidence.
static = audit['static_inverse_extension']
assert static['contract'] == 'static_units_1_to_INT_MAX'
assert static['new_online_verification'] is False
assert (ROOT / static['test']).is_file()
assert (ROOT / static['documentation']).is_file()
assert 'try_inv' in modules['modint']['notes']
assert '仍未扩展' not in ' '.join(modules['modint']['gaps'])

print('PASS: 12 ACL module rows, current paths/statuses, fixed provenance and remaining gaps agree; metadata-only check')
