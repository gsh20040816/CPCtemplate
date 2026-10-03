"""Additive constraints: independent graph oracle and copied program checks."""
import argparse, hashlib, json, os, random, resource, subprocess, sys, tempfile, time
from collections import deque
from pathlib import Path
if not __debug__:
    raise RuntimeError('Run this test without Python optimization')
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
from audit_copy_context import extract_components
from run_provenance import snapshot
MOD = 998244353


def small_case(rng, n, q):
    g = [[] for _ in range(n)]
    lines = [f'{n} {q}']; answers = []
    def difference(u, v):
        values = {v: 0}; queue = deque([v])
        while queue:
            a = queue.popleft()
            for b, w in g[a]:
                if b not in values:
                    values[b] = (values[a] + w) % MOD; queue.append(b)
        return values.get(u)
    for i in range(q):
        u, v = rng.randrange(n), rng.randrange(n)
        old = difference(u, v)
        if i % 4 == 0:
            lines.append(f'1 {u} {v}'); answers.append(-1 if old is None else old)
        else:
            w = rng.randrange(MOD) if old is None else (old + (i % 3 == 0)) % MOD
            lines.append(f'0 {u} {v} {w}')
            ok = old is None or old == w; answers.append(int(ok))
            if ok:
                g[v].append((u, w)); g[u].append((v, (-w) % MOD))
    return '\n'.join(lines) + '\n', '\n'.join(map(str, answers)) + '\n'


def large_case(kind):
    n = q = 200000; lines = [f'{n} {q}']; answers = []
    # A deterministic partial forest leaves enough queries after many unions.
    end = 100000
    for u in range(1, end):
        v = u - 1 if kind == 'chain' else (u - 1) // 2
        w = (17 * (u - v)) % MOD
        lines.append(f'0 {u} {v} {w}'); answers.append(1)
    for i in range(q - end + 1):
        u, v = (i * 173 + 11) % end, (i * 317 + 97) % end
        w = 17 * (u - v) % MOD
        k = i % 5
        if k == 0:
            lines.append(f'1 {u} {n - 1}'); answers.append(-1)
        elif k == 1:
            lines.append(f'1 {u} {v}'); answers.append(w)
        elif k == 2:
            lines.append(f'0 {u} {v} {w}'); answers.append(1)
        elif k == 3:
            lines.append(f'0 {u} {v} {(w + 1) % MOD}'); answers.append(0)
        else:
            lines.append(f'1 {n - 1} {n - 1}'); answers.append(0)
    assert len(lines) == q + 1 and len(answers) == q
    return '\n'.join(lines) + '\n', '\n'.join(map(str, answers)) + '\n'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sanitizer', action='store_true'); args = ap.parse_args()
    san = args.sanitizer or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'; before = snapshot(ROOT)
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    (ROOT / 'build').mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='potential-dsu-' + mode + '-', dir=ROOT / 'build'))
    compiler = Path(subprocess.check_output(['which', CXX], text=True).strip()).resolve()
    frontend = Path(subprocess.check_output([CXX, '-print-prog-name=cc1plus'], text=True).strip()).resolve()
    ch, fh = sha(compiler), sha(frontend)
    flags = ['-std=c++20'] + (['-O1', '-g', '-fsanitize=address,undefined'] if san else ['-O2'])
    stack = resource.getrlimit(resource.RLIMIT_STACK)
    def limits():
        _, hard = resource.getrlimit(resource.RLIMIT_CORE)
        resource.setrlimit(resource.RLIMIT_CORE, (0, hard))
    commands = []
    def run(cmd, data=None, expected=0):
        start = time.monotonic()
        p = subprocess.run(cmd, input=data, text=True, capture_output=True, cwd=ROOT,
                           preexec_fn=limits, timeout=300)
        files = {}; index = len(commands)
        for name, value in [('stdin', data), ('stdout', p.stdout), ('stderr', p.stderr)]:
            if value is not None:
                f = out / f'{index}.{name}'; f.write_text(value)
                files[name] = str(f.relative_to(ROOT)); files[name + '_sha256'] = sha(f)
        commands.append(dict(command=list(map(str, cmd)), returncode=p.returncode,
                             seconds=time.monotonic() - start, **files))
        assert p.returncode == expected, (cmd, p.returncode, p.stderr[:1200])
        if data is not None and expected == 0: assert not p.stderr, p.stderr
        return p.stdout
    prelude = ''.join('#include <' + h + '>\n' for h in
                      ['cassert','climits','cstdint','iostream','numeric','optional',
                       'queue','random','tuple','utility','vector']) + 'using namespace std;\n'
    components = {x['symbol']: x['code'] for x in
                  extract_components(json.loads((ROOT / 'docs/catalog.json').read_text()))}
    body = (ROOT / 'tests/potential_dsu.cpp').read_text().split('long long states', 1)[1]
    minimal = prelude + components['PotentialDSU'] + '\n' + components['mint'] + '\nlong long states' + body
    core_results = {}
    def artifact(src, exe):
        return dict(source=str(src.relative_to(ROOT)), source_sha256=sha(src),
                    binary=str(exe.relative_to(ROOT)), binary_sha256=sha(exe))
    for name, text in [('header', (ROOT / 'tests/potential_dsu.cpp').read_text().replace('../src/', str(ROOT / 'src') + '/')),
                       ('copied', minimal)]:
        src = out / f'core-{name}.cpp'; src.write_text(text); exe = src.with_suffix('')
        run([CXX, *flags, '-pedantic-errors', str(src), '-o', str(exe)])
        stdout = run([str(exe)], ''); assert '200000-node cases PASS' in stdout
        core_results[name] = dict(**artifact(src, exe), stdout=stdout.strip())
    variants = {
        'wrong-root-offset': ('d[u] - d[v] - w', 'd[v] - d[u] + w'),
        'missing-swap-negation': ('t = T(0) - t;', 't = t;'),
        'missing-parent-offset': ('d[u] = d[u] + d[p];', 'd[u] = d[u];'),
        'accept-contradictions': ('return d[u] - d[v] == w;', 'return true;'),
        'unknown-as-zero': ('return nullopt;', 'return T(0);')}
    mutants = {}
    for name, (a, b) in variants.items():
        assert a in components['PotentialDSU']
        text = minimal.replace(components['PotentialDSU'], components['PotentialDSU'].replace(a, b))
        src = out / f'mutant-{name}.cpp'; src.write_text(text); exe = src.with_suffix('')
        run([CXX, *flags, str(src), '-o', str(exe)]); run([str(exe)], '', expected=-6)
        stderr = (ROOT / commands[-1]['stderr']).read_text()
        assert 'Assertion' in stderr and 'failed' in stderr
        mutants[name] = artifact(src, exe)
    rng = random.Random(232)
    cases = [('official-domain-small', *small_case(rng, 1 + i % 31, 100)) for i in range(100)]
    cases.append(('official-domain-hand-certificate',
                  '3 9\n1 0 1\n0 0 1 3\n1 0 1\n1 1 0\n0 0 1 4\n0 0 1 3\n0 1 2 5\n1 0 2\n0 2 2 1\n',
                  '-1\n1\n3\n998244350\n0\n1\n1\n8\n0\n'))
    for kind in ['chain', 'binary']: cases.append(('official-domain-max-' + kind, *large_case(kind)))
    row = next(r for r in records() if r['id'] == 'example-232')
    forms = {'direct': (ROOT / row['driver']).read_text().replace('../../src/', str(ROOT / 'src') + '/'),
             'expanded': row['program'],
             'copied': prelude + '\n'.join(components[s] for s in row['requires']) + '\n' + row['snippet']}
    reports = {}
    for name, text in forms.items():
        src = out / f'program-{name}.cpp'; src.write_text(text); exe = src.with_suffix('')
        run([CXX, *flags, str(src), '-o', str(exe)])
        for category, data, want in cases:
            output = run([str(exe)], data)
            assert output.split() == want.split(), (name, category, output[:200], want[:200])
            f = out / f'{len(commands) - 1}.expected'; f.write_text(want)
            commands[-1].update(category=category, expected=str(f.relative_to(ROOT)), expected_sha256=sha(f))
        reports[name] = dict(**artifact(src, exe), cases=len(cases), official_domain_inputs=len(cases))
    assert snapshot(ROOT) == before and ch == sha(compiler) and fh == sha(frontend)
    report = dict(mode=mode, passed=True, source_before_sha256=before, source_after_sha256=snapshot(ROOT),
                  compiler=str(compiler), compiler_sha256=ch, frontend=str(frontend), frontend_sha256=fh,
                  compiler_version=subprocess.check_output([CXX, '--version'], text=True).strip(),
                  environment={k: os.environ.get(k) for k in ['CXX','ASAN_OPTIONS','UBSAN_OPTIONS','CPC_SANITIZE','SANITIZE']},
                  flags=flags, inherited_stack=stack, core=core_results, negative_mutations=mutants,
                  programs=reports, commands=commands,
                  scope='Exact additive integer and modular constraints, two core forms, five rejected mutations; 103 complete official-domain inputs per direct/expanded/copied program, including two n=q=200000 cases. Stack unchanged. Local validation, not online AC, full-suite or LeakSanitizer certification.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Potential DSU {mode}: two core forms, five rejected mutations, {len(cases)} inputs x three program forms PASS; report {out.relative_to(ROOT)}/report.json', flush=True)

if __name__ == '__main__': main()
