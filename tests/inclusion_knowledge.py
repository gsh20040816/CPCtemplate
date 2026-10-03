#!/usr/bin/env python3
"""Source-bound inclusion/exclusion checks in one selected build profile.

Installed usage:
  python3 tests/inclusion_knowledge.py [--sanitize] [--report PATH]
Draft development requires BOTH --prototype and --source PATH. Such receipts
are explicitly non-publication evidence. Importing this module performs no I/O.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import os
import platform
import random
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

MOD = 998244353
MODULI = (1, 2, 3, 5, 7, 97, 998244353, 4, 6, 8, 9, 12, 1000)
MAX_LL = 2**63-1
LABEL = 'knowledge-inclusion-exact'
CANONICAL_SOURCE = 'docs/knowledge-inclusion.tex'
CANONICAL_RUNNER = 'tests/inclusion_knowledge.py'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pascal(n, modulus=None):
    rows = [[1]]
    for k in range(1, n+1):
        row = [1] + [rows[-1][j-1]+rows[-1][j] for j in range(1, k)] + [1]
        if modulus is not None:
            row = [v % modulus for v in row]
        rows.append(row)
    if modulus is not None:
        rows[0][0] %= modulus
    return rows

PASCAL = pascal(10)
RESIDUE_PASCAL = {p: pascal(10, p) for p in MODULI}


def incidence_check(assignment, m, weights=None):
    """Build actual sets and literally intersect subsets, never infer S from N."""
    u = len(assignment)
    omega = set(range(u))
    a = [{x for x, mask in enumerate(assignment) if mask & (1 << i)} for i in range(m)]
    weights = [1]*u if weights is None else weights
    s = [sum(weights)] + [0]*m
    for j in range(1, m+1):
        for indices in combinations(range(m), j):
            intersection = omega.copy()
            for i in indices:
                intersection.intersection_update(a[i])
            s[j] += sum(weights[x] for x in intersection)
    n = [0]*(m+1)
    for x in omega:
        n[sum(x in ai for ai in a)] += weights[x]
    assert s == [sum(PASCAL[t][j]*n[t] for t in range(j, m+1)) for j in range(m+1)]
    for r in range(-2, m+3):
        exact = sum((-1)**(j-r)*PASCAL[j][r]*s[j] for j in range(r, m+1)) if 0 <= r <= m else 0
        at_least = (s[0] if r <= 0 else
                    sum((-1)**(j-r)*PASCAL[j-1][r-1]*s[j] for j in range(r, m+1)))
        assert exact == (n[r] if 0 <= r <= m else 0)
        assert at_least == sum(n[max(0,r):])
    # Only addition/multiplication/subtraction on modular Pascal coefficients.
    # Includes modulus 1 and composites; no modular inverses/division occur.
    for p in MODULI:
        c = RESIDUE_PASCAL[p]
        smod = [v % p for v in s]
        assert smod == [sum(c[t][j]*(n[t] % p) for t in range(j, m+1)) % p for j in range(m+1)]
        for r in range(m+1):
            exact = sum((-1)**(j-r)*c[j][r]*smod[j] for j in range(r, m+1)) % p
            at_least = smod[0] if r == 0 else sum((-1)**(j-r)*c[j-1][r-1]*smod[j] for j in range(r, m+1)) % p
            assert exact == n[r] % p
            assert at_least == sum(n[r:]) % p
    return s, n


def check_incidence(report):
    counts = Counter()
    started = time.monotonic()
    for m in range(5):
        for u in range(5):
            for assignment in product(range(1 << m), repeat=u):
                incidence_check(assignment, m)
                counts[f'm={m}, universe={u}'] += 1
    # Larger explicitly shaped universes, including empty, repeated, nested,
    # disjoint and unequal equal-cardinality-intersection examples.
    fixtures = {
        'empty_universe_m8': ((), 8),
        'zero_properties': ((0,0,0,0,0,0), 0),
        'all_repeated_equal_universe': ((255,)*5, 8),
        'repeated_sets_with_outside': ((255,255,255,0,0), 8),
        'nested_chain': ((0,1,3,7,15,31,63,127,255), 8),
        'pairwise_disjoint_with_outside': ((0,1,2,4,8,16,32,64,128), 8),
        'equal_cardinality_unequal_pair_intersections': ((3,3,4,4), 3),
        'all_empty_sets': ((0,)*5, 8),
        'one_object_two_properties': ((3,), 2),
    }
    details = {}
    for name, (assignment,m) in fixtures.items():
        s,n = incidence_check(assignment,m)
        details[name] = dict(m=m, assignment=list(assignment), intersection_sums=s, exact_counts=n)
    rng = random.Random(202610021)
    for _ in range(256):
        m = rng.randrange(9)
        u = rng.randrange(11)
        assignment = [rng.randrange(1<<m) for _ in range(u)]
        weights = [rng.randrange(-20,21) for _ in range(u)]
        incidence_check(assignment,m,weights)
    report['incidence'] = dict(passed=True, exhaustive_assignments=sum(counts.values()),
        per_dimension=dict(counts), named_fixtures=details, signed_weighted_random_fixtures=256,
        moduli=list(MODULI), seconds=round(time.monotonic()-started,6),
        oracle='Literal intersections of concrete sets versus direct per-object membership counts; addition-only Pascal coefficients for modular transforms; no modular division')
    print('Incidence PASS:', sum(counts.values()), 'exhaustive assignments,',len(fixtures),'named and 256 signed-weighted fixtures',flush=True)


def occupied_step(dp, m, modulus=None):
    nxt = [0]*len(dp)
    for k,value in enumerate(dp):
        nxt[k] += value*k
        if k+1 < len(dp):
            nxt[k+1] += value*(m-k)
    if modulus is not None:
        nxt = [v % modulus for v in nxt]
    return nxt


def occupied_dp(n, m, limit=None, modulus=None):
    limit = min(n,m) if limit is None else min(m,limit)
    dp = [1] + [0]*limit
    for _ in range(n):
        dp = occupied_step(dp,m,modulus)
    return dp


def multiply(a,b,p):
    size = len(a)
    out = [[0]*size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if a[i][k]:
                for j in range(size):
                    out[i][j] = (out[i][j]+a[i][k]*b[k][j]) % p
    return out


def occupied_matrix(n,m,limit=None,p=MOD):
    """Power the ball-by-ball transition, with no IE sum, factorial or inverse."""
    limit = m if limit is None else min(m,limit)
    size = limit+1
    a = [[0]*size for _ in range(size)]
    for k in range(size):
        a[k][k] = k % p
        if k+1 < size:
            a[k+1][k] = (m-k) % p
    result = [[int(i==j) for j in range(size)] for i in range(size)]
    while n:
        if n & 1:
            result = multiply(result,a,p)
        a = multiply(a,a,p)
        n >>= 1
    return [result[k][0] for k in range(size)]


def ballot_formula(n,m,r):
    if not 0 <= r <= min(n,m):
        return 0
    return math.comb(m,r)*sum((-1)**j*math.comb(r,j)*(r-j)**n for j in range(r+1))


def falling(m,r):
    out = 1
    for k in range(r):
        out = out*(m-k) % MOD
    return out


def build_cases(report):
    cases=[]
    group_counts=Counter()
    def add(n,m,r,want,group):
        assert 0 <= n <= MAX_LL and 0 <= m < MOD and -(2**31) <= r < 2**31
        cases.append(dict(n=n,m=m,r=r,expected=want % MOD,group=group))
        group_counts[group]+=1
    maps_count=0
    enumerated_models=0
    for m in range(7):
        for n in range(8):
            histogram=[0]*(m+1)
            for mapping in product(range(m),repeat=n):
                histogram[len(set(mapping))] += 1
                maps_count += 1
            enumerated_models += 1
            dp=occupied_dp(n,m)
            dp += [0]*(m+1-len(dp))
            assert histogram==dp
            assert sum(histogram)==m**n
            matrix=occupied_matrix(n,m)
            assert matrix==[v % MOD for v in histogram]
            for r in range(-2,m+3):
                want=histogram[r] if 0 <= r <= m else 0
                assert ballot_formula(n,m,r)==want
                # Empty-box S and inversion is checked against mapping histogram.
                if 0 <= r <= m:
                    s=[math.comb(m,j)*(m-j)**n for j in range(m+1)]
                    empty=m-r
                    inverse=sum((-1)**(j-empty)*math.comb(j,empty)*s[j] for j in range(empty,m+1))
                    assert inverse==want
                add(n,m,r,want,'literal_labelled_maps')
    for m in range(31):
        for n in range(41):
            dp=occupied_dp(n,m)
            assert sum(dp)==m**n
            for r in range(-2,m+3):
                want=dp[r] if 0 <= r < len(dp) else 0
                assert ballot_formula(n,m,r)==want
                add(n,m,r,want,'integer_occupied_dp')
    huge_n=(2**31-1,2**31,MOD-1,MOD,MOD+1,2*MOD,2**62,MAX_LL-1,MAX_LL)
    for m in range(9):
        for n in huge_n:
            dp=occupied_matrix(n,m)
            assert sum(dp)%MOD==pow(m,n,MOD)
            for r in (-2**31, *range(-2,m+3), 2**31-1):
                add(n,m,r,dp[r] if 0 <= r <= m else 0,'huge_n_transition_matrix')
    # Practical table sizes: DP only tracks reachable occupied states.
    for m in (99999,100000):
        for n in (0,1,2,3,8,31,100):
            dp=occupied_dp(n,m,modulus=MOD)
            assert sum(dp)%MOD==pow(m,n,MOD)
            for r in sorted({-2**31,-1,0,1,2,3,n//2,n,n+1,m-1,m,2**31-1}):
                add(n,m,r,dp[r] if 0 <= r < len(dp) else 0,'practical_large_m_dp')
        for n in (MOD,MAX_LL):
            dp=occupied_matrix(n,m,limit=8)
            for r in range(9):
                add(n,m,r,dp[r],'practical_large_m_huge_n_matrix')
        # Bijective/all-but-one occupied and exactly one doubleton block cases.
        fact=falling(m,m)
        add(m,m,m,fact,'practical_large_r_closed_count')
        add(m,m,m-1,math.comb(m,2)*falling(m,m-1),'practical_large_r_closed_count')
        add(m+1,m,m,math.comb(m+1,2)*fact,'practical_large_r_closed_count')
    # Invalid INT endpoints in the tiny and empty contracts.
    for n in (0,1,MAX_LL):
        for m in (0,1,2,100000):
            for r in (-2**31,-1,2**31-1):
                add(n,m,r,0,'invalid_r_int_endpoints')
    report['ball_oracles']=dict(passed=True,literal_mapping_models=enumerated_models,
        labelled_maps_enumerated=maps_count, cases=len(cases),groups=dict(group_counts),
        huge_n=list(huge_n),largest_n=MAX_LL,largest_m=100000,
        oracle='Literal maps and integer occupied-count DP; independent modular transition-matrix exponentiation for huge n; bijection and one-doubleton closed counts for huge r; no modular inverse')
    print('Ball oracle PASS:',maps_count,'maps;',len(cases),'snippet cases',flush=True)
    return cases


def repository_root(script):
    """Find the nearest actual project root, independent of cwd/install depth."""
    markers = ('src/compact/number_theory.hpp', 'tests/compiler_config.py',
               'docs/catalog.json', 'docs/knowledge-taxonomy.json', 'tools/test.sh')
    for candidate in script.resolve().parents:
        if all((candidate/name).is_file() for name in markers):
            return candidate
    raise RuntimeError(f'Cannot locate CPCtemplate root above {script}')


def parse_options(argv=None):
    # Assertions provide the exhaustive oracle checks. Never silently strip them.
    if not __debug__ or 'PYTHONOPTIMIZE' in os.environ:
        raise RuntimeError('Run without Python -O/-OO and unset PYTHONOPTIMIZE; assertions are required')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true',
                        help='Run only ASan+UBSan; SANITIZE=1/CPC_SANITIZE=1 also select this profile')
    parser.add_argument('--report', type=Path, help='Also write the complete receipt at this path')
    parser.add_argument('--prototype', action='store_true', help='Explicit non-publication draft run')
    parser.add_argument('--source', type=Path, help='Draft TeX path, required with --prototype only')
    args = parser.parse_args(argv)
    if args.prototype != (args.source is not None):
        parser.error('--prototype and --source must be used together')
    args.mode = ('asan_ubsan' if args.sanitize or any(os.environ.get(k) == '1'
                 for k in ('SANITIZE', 'CPC_SANITIZE')) else 'ordinary')
    return args


def dependencies(path, seen=None):
    """Snapshot the current quoted-include closure before using any source bytes.

    Each actual compiler-generated dependency set is separately compared below;
    a new untracked compiler dependency fails instead of silently expanding proof.
    """
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return seen
    if not path.is_file():
        raise RuntimeError(f'Missing project dependency: {path}')
    seen.add(path)
    for name in re.findall(r'^\s*#\s*include\s+"([^"]+)"', path.read_text(), re.M):
        dependencies(path.parent/name, seen)
    return seen


def snapshot(paths, root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(paths)}


def load_compiler_config(path):
    """Execute the repository compiler selector without writing tests/__pycache__."""
    spec = importlib.util.spec_from_file_location('_inclusion_compiler_config', path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot load tests/compiler_config.py')
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module.CXX


def resolve_executable(name):
    candidate = shutil.which(str(name)) or str(name)
    path = Path(candidate).resolve()
    if not path.is_file():
        raise RuntimeError(f'Compiler executable not found: {name}')
    return path


def compiler_identity(driver, frontend):
    return dict(driver=str(driver), driver_sha256=digest(driver),
                frontend=str(frontend), frontend_sha256=digest(frontend))


def integration_snapshot(root, source, prototype):
    catalog = json.loads((root/'docs/catalog.json').read_text())
    components = {}
    for symbol in ('ModInt', 'Binomial'):
        rows = [row for row in catalog if len(row) >= 2 and row[1] == symbol]
        assert len(rows) == 1 and rows[0][0] == 'number_theory', (symbol, rows)
        components[symbol] = rows[0]
    taxonomy = json.loads((root/'docs/knowledge-taxonomy.json').read_text())
    navigation = json.loads((root/'docs/oi-taxonomy.json').read_text())
    mappings = [row for row in taxonomy['entries'] if row['label'] == LABEL]
    record = dict(catalog_entries=components, observed_taxonomy_entries=mappings,
                  enforced_installed_mapping=not prototype,
                  installed_integration_claim=False)
    if prototype:
        record['note'] = 'Existing taxonomy/catalog bytes are bound, but no future mapping is fabricated or claimed validated'
        return record
    assert source == root/CANONICAL_SOURCE
    assert len(mappings) == 1 and mappings[0]['source'] == CANONICAL_SOURCE
    assert CANONICAL_SOURCE in taxonomy['scope']['source_files']
    assert taxonomy['scope']['new_algorithm_coverage'] is False
    assert taxonomy['scope']['new_oj_verification'] is False
    known = {row['path'] for row in navigation['navigation']}
    assert mappings[0]['path'] in known
    assert all(path in known for path in mappings[0]['additional'])
    assert taxonomy['reference_commit'] == navigation['reference_commit']
    assert taxonomy['reference_source_sha256'] == navigation['source_sha256']
    record['installed_integration_claim'] = True
    record['note'] = 'Checks this installed source mapping and component catalog entries, not whole-book generation/layout or the full taxonomy suite'
    return record


def prepare_programs(root, source, out):
    tex = source.read_bytes()
    listings = re.findall(rb'\\begin\{lstlisting\}\n(.*?)\\end\{lstlisting\}', tex, re.S)
    assert len(listings) == 1, 'Expected one exact printed lstlisting'
    snippet = listings[0]
    assert tex.count(('\\label{'+LABEL+'}').encode()) == 1
    header = root/'src/compact/number_theory.hpp'
    header_bytes = header.read_bytes()
    regions = []
    info = []
    for symbol in ('ModInt', 'Binomial'):
        # Anchor the actual templated top-level declaration and its top-level
        # closing brace; never infer from historical numeric line positions.
        pattern = rb'^template\s*<\s*int\s+mod\s*>\s*struct\s+' + symbol.encode() + rb'\b[^\n]*\n\{\n.*?^\};(?:\n|$)'
        matches = list(re.finditer(pattern, header_bytes, re.M | re.S))
        assert len(matches) == 1, f'Expected exactly one anchored {symbol} region'
        match = matches[0]
        region = match.group()
        assert re.findall(rb'^(?:template[^\n]*\s+)?struct\s+(\w+)', region, re.M) == [symbol.encode()]
        regions.append(region)
        info.append(dict(symbol=symbol, source='src/compact/number_theory.hpp',
                         start_byte=match.start(), end_byte=match.end(), sha256=sha(region)))
    wrapper = (b'\nint main() {\nlong long n; int m, r;\n'
               b'while (std::cin >> n >> m >> r) {\n'+snippet+
               b'\nstd::cout << answer.v << "\\n";\n}\n}\n')
    programs = {
        'minimal_components': b'#include <cassert>\n#include <vector>\n#include <iostream>\n#include <optional>\n#include <utility>\nusing namespace std;\n'+b'\n'.join(regions)+wrapper,
        'full_header': b'#include "number_theory.hpp"\n'+wrapper,
    }
    paths = {}
    for context, program in programs.items():
        path = out/(context+'.cpp')
        path.write_bytes(program)
        paths[context] = path
    return paths, dict(snippet_sha256=sha(snippet), copied_regions=info,
                       snippet_extraction='Sole lstlisting copied byte-for-byte; wrapper only reads n,m,r and prints answer.v',
                       context_sha256={name: digest(path) for name,path in paths.items()})


def actual_dependencies(depfile, root):
    text = depfile.read_text().replace('\\\n', '')
    _, separator, rest = text.partition(':')
    assert separator, 'Missing compiler dependency rule'
    result = set()
    for name in shlex.split(rest):
        path = Path(name)
        path = path.resolve() if path.is_absolute() else (root/path).resolve()
        assert path.is_file(), path
        result.add(path)
    return result


def write_report(report, out, requested):
    text = json.dumps(report, indent=2)+'\n'
    (out/'report.json').write_text(text)
    if requested and requested != out/'report.json':
        requested.parent.mkdir(parents=True, exist_ok=True)
        requested.write_text(text)


def run(args):
    self_path = Path(__file__).resolve()
    root = repository_root(self_path)
    source = args.source.resolve() if args.prototype else root/CANONICAL_SOURCE
    if not source.is_file():
        raise RuntimeError(f'Required TeX source does not exist: {source}; no implicit draft fallback')
    if not source.is_relative_to(root):
        raise RuntimeError('The explicitly selected TeX source must be inside this repository')
    if not args.prototype and self_path != root/CANONICAL_RUNNER:
        raise RuntimeError('Publication-mode checks require the installed tests/inclusion_knowledge.py; use explicit --prototype --source for draft work')
    requested = args.report.resolve() if args.report else None
    build_parent = root/'build'
    if args.prototype:
        # Draft development never writes into a currently frozen source/report tree.
        build_parent = root/'build/inclusion-next'
        if requested and not requested.is_relative_to(root/'build'):
            raise RuntimeError('Prototype --report must stay under build/; frozen/publication report paths are not permitted')
    config = root/'tests/compiler_config.py'
    project_deps = dependencies(root/'src/compact/number_theory.hpp')
    sources = {self_path, source, config, *project_deps,
               root/'docs/catalog.json', root/'docs/knowledge-taxonomy.json',
               root/'docs/oi-taxonomy.json', root/'tests/knowledge_taxonomy.py',
               root/'tests/math_knowledge_integration.py', root/'tools/test.sh'}
    if requested in sources:
        raise RuntimeError('--report cannot overwrite a bound source')
    before = snapshot(sources,root)  # Before reading source for derivation/config execution.
    driver = resolve_executable(load_compiler_config(config))
    frontend_name = subprocess.check_output([str(driver), '-print-prog-name=cc1plus'], text=True).strip()
    frontend = resolve_executable(frontend_name)
    compiler_before = compiler_identity(driver,frontend)
    if requested in {driver,frontend}:
        raise RuntimeError('--report cannot overwrite a compiler')
    build_parent.mkdir(parents=True,exist_ok=True)
    prefix = ('test_prototype_' if args.prototype else 'inclusion-knowledge-')+args.mode+'-'
    out = Path(tempfile.mkdtemp(prefix=prefix,dir=build_parent)).resolve()
    started = time.monotonic()
    env = dict(os.environ)
    env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    env.pop('LSAN_OPTIONS',None)
    flags = ['-std=c++20','-Wall','-Wextra','-Werror']+(['-O2'] if args.mode == 'ordinary' else
             ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])
    report = dict(schema_version=1, passed=False, mode=args.mode,
        prototype=args.prototype, publication_eligible=not args.prototype,
        evidence_kind='non-publication prototype' if args.prototype else 'installed source-bound local checks',
        started_at=datetime.now(timezone.utc).isoformat(), build_directory=str(out.relative_to(root)),
        actual_runner=str(self_path.relative_to(root)), actual_tex=str(source.relative_to(root)),
        source_sha256_before=before, compiler_before=compiler_before,
        compiler_version=subprocess.check_output([str(driver),'--version'],text=True),
        toolchain_scope='Resolved compiler driver and cc1plus frontend only; not the complete toolchain or system headers',
        platform=platform.platform(), python_version=sys.version, flags=flags,
        pie='Compiler default; no PIE overrides', quarantine='ASan default; no quarantine overrides',
        sanitizer_options={k:env[k] for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')}, runs=[],
        scope='Local mathematical and exact-interface checks only; no full regression, OJ/CI, LSan, layout, or modulus-scale factorial-table claim')
    failure = None
    generated = {}
    try:
        report['integration'] = integration_snapshot(root,source,args.prototype)
        programs, evidence = prepare_programs(root,source,out)
        report.update(evidence)
        check_incidence(report)
        cases = build_cases(report)
        assert len(cases) == 26983, 'Unexpected coverage change; review before changing the bound count'
        fixture = ''.join(f"{c['n']} {c['m']} {c['r']}\n" for c in cases)
        expected = ''.join(f"{c['expected']}\n" for c in cases)
        (out/'cases.jsonl').write_text(''.join(json.dumps(c,sort_keys=True)+'\n' for c in cases))
        (out/'input.txt').write_text(fixture)
        (out/'expected.txt').write_text(expected)
        generated = {path: digest(path) for path in [*programs.values(),out/'cases.jsonl',out/'input.txt',out/'expected.txt']}
        report['generated_sha256_before'] = {str(p.relative_to(root)):value for p,value in generated.items()}
        report['fixture_sha256'] = digest(out/'cases.jsonl')
        report['input_sha256'] = sha(fixture.encode())
        report['expected_sha256'] = sha(expected.encode())
        for context, cpp in programs.items():
            assert snapshot(sources,root) == before, 'Bound source changed before compilation'
            assert compiler_identity(driver,frontend) == compiler_before, 'Compiler changed before compilation'
            binary = out/context
            depfile = out/(context+'.d')
            command = [str(driver),*flags,'-I',str(root/'src/compact'),'-MMD','-MF',str(depfile),str(cpp),'-o',str(binary)]
            entry = dict(context=context,mode=args.mode,cases=len(cases),compile_command=command)
            report['runs'].append(entry)
            compiled = subprocess.run(command,capture_output=True,text=True,cwd=root,env=env,timeout=180)
            entry['compile'] = dict(exit_code=compiled.returncode,stdout=compiled.stdout,stderr=compiled.stderr)
            assert compiled.returncode == 0, f'{context} compilation failed: {compiled.stderr}'
            deps = actual_dependencies(depfile,root)
            expected_deps = {cpp} | (project_deps if context == 'full_header' else set())
            assert deps == expected_deps, ('Actual compiler dependency closure differs',deps^expected_deps)
            entry['actual_dependency_sha256'] = snapshot(deps,root)
            entry['dependency_file_sha256'] = digest(depfile)
            entry['source_sha256'] = digest(cpp)
            entry['binary_sha256_before'] = digest(binary)
            # ELF inspection is informative and platform-conditional; never change
            # the toolchain's default PIE policy to make a diagnostic pass.
            readelf = shutil.which('readelf')
            if sys.platform.startswith('linux') and readelf:
                elf = subprocess.check_output([readelf,'-h',str(binary)],text=True)
                entry['elf_type'] = elf.split('Type:')[1].splitlines()[0].strip()
            run_started = time.monotonic()
            ran = subprocess.run([str(binary)],input=fixture,capture_output=True,text=True,cwd=root,env=env,timeout=180)
            entry.update(exit_code=ran.returncode,stderr=ran.stderr,actual_sha256=sha(ran.stdout.encode()),seconds=round(time.monotonic()-run_started,6))
            if ran.stdout != expected:
                actual = ran.stdout.splitlines()
                for index,case in enumerate(cases):
                    if index >= len(actual) or actual[index] != str(case['expected']):
                        entry['first_mismatch'] = dict(index=index,case=case,actual=actual[index] if index<len(actual) else 'MISSING')
                        break
                entry['actual_line_count'] = len(actual)
            entry['binary_sha256_after'] = digest(binary)
            entry['passed'] = (ran.returncode == 0 and ran.stderr == '' and ran.stdout == expected
                               and entry['binary_sha256_before'] == entry['binary_sha256_after'])
            assert snapshot(sources,root) == before, 'Bound source changed during build/run'
            assert all(digest(path) == value for path,value in generated.items()), 'Generated source/fixture changed during build/run'
            assert entry['passed'], f'{args.mode} {context} output, process, or binary-integrity failure: {entry}'
            print(args.mode,context,len(cases),'PASS',flush=True)
        report['passed'] = True
    except BaseException as error:
        failure = error
        report['failure'] = f'{type(error).__name__}: {error}'
    finally:
        try:
            report['source_sha256_after'] = snapshot(sources,root)
            report['compiler_after'] = compiler_identity(driver,frontend)
            report['sources_unchanged'] = report['source_sha256_after'] == before
            report['compiler_unchanged'] = report['compiler_after'] == compiler_before
            report['generated_sha256_after'] = {str(p.relative_to(root)):digest(p) for p in generated}
            report['generated_unchanged'] = all(digest(p) == value for p,value in generated.items())
            if not all(report[k] for k in ('sources_unchanged','compiler_unchanged','generated_unchanged')):
                raise RuntimeError('Bound source/compiler/generated input changed during verification')
        except BaseException as error:
            report['passed'] = False
            report['integrity_failure'] = f'{type(error).__name__}: {error}'
            if failure is None:
                failure = error
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        report['seconds'] = round(time.monotonic()-started,6)
        write_report(report,out,requested)
        print('Report:',requested or out/'report.json',flush=True)
    if failure is not None:
        raise failure
    print(f"{report['evidence_kind']}: {args.mode} PASS; 2 contexts, {2*len(cases)} checked answers",flush=True)
    return report


def main(argv=None):
    return run(parse_options(argv))


if __name__ == '__main__':
    main()
