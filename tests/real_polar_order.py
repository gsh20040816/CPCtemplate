#!/usr/bin/env python3
"""Exact represented-floating polar API checks, including real copied usage."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import random
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/real-polar-demo'
DRIVER = ROOT / 'docs/usage-drivers/real-polar-demo.cpp'
HEADER = ROOT / 'src/compact/real_polar.hpp'
PLANE = ROOT / 'src/compact/real_plane.hpp'
CORE = ROOT / 'tests/real_polar_order.cpp'
EXAMPLE = 'example-228'
SEED = 20261002


def sha(data):
    return hashlib.sha256(data).hexdigest()


def angle_key(point):
    """Four exact rational slopes; no half-plane/cross implementation reuse."""
    x, y = point
    if x == y == 0:
        return (-1, F(0), F(0))
    if x > 0 and y >= 0:
        quadrant, slope = 0, y / x
    elif y > 0 and x <= 0:
        quadrant, slope = 1, -x / y
    elif x < 0 and y <= 0:
        quadrant, slope = 2, y / x
    else:
        quadrant, slope = 3, x / -y
    return quadrant, slope, x*x + y*y


def expected_ids(points):
    keys = {p: angle_key(p) for p in set(points)}
    return sorted(range(1, len(points) + 1), key=lambda i: (keys[points[i-1]], i))


def validate_output(stdout, expected):
    words = stdout.split()
    assert len(words) == len(expected), 'Output ID count differs'
    assert all(re.fullmatch(rb'[0-9]+', word) for word in words), 'Non-ID output'
    actual = list(map(int, words))
    assert actual == expected, 'Wrong exact polar/radial/original-ID order'


def dyadic_decimal(m, k):
    # Decimal(int) avoids Python's large-integer string conversion limit.
    with localcontext() as ctx:
        ctx.prec = abs(k) + max(80, m.bit_length() + 2)
        return format(Decimal(m) * (Decimal(2) ** k), 'f')


def dyadic_value(m, k):
    return F(m * 2**k) if k >= 0 else F(m, 2**(-k))


def make_case(name, tokens, points=None):
    assert 0 <= len(tokens) <= 200000
    data = (str(len(tokens)) + '\n' + ''.join(x+' '+y+'\n' for x, y in tokens)).encode()
    if points is None:
        points = [tuple(F(v) for v in p) for p in tokens]
    assert len(points) == len(tokens)
    return dict(name=name, data=data, expected=expected_ids(points), n=len(tokens),
                oracle='exact-input-dyadic-four-quadrant-slopes')


def cases(meta):
    text = (FIXTURES/'sample.in').read_text().split()
    tokens = list(zip(text[1::2], text[2::2]))
    assert len(tokens) == int(text[0])
    sample = make_case('custom-sample', tokens)
    validate_output((FIXTURES/'sample.out').read_bytes(), sample['expected'])
    yield sample
    yield make_case('empty', [])
    yield make_case('singleton-origin', [('0', '-0')])
    yield make_case('all-signed-zeros', [('0','0'), ('-0','0'), ('0','-0'), ('-0','-0')])
    grid = [(str(x/4), str(y/4)) for x in range(-8,9) for y in range(-8,9)]
    rng = random.Random(SEED)
    rng.shuffle(grid)
    yield make_case('quarter-grid-all-quadrants-axes-rays', grid)
    p = meta['digits']
    m = 2**p-1
    # All inputs are normal and exact; products/determinants need not be representable.
    for k, name in [(0,'unit'), ((meta['max_exponent']+1)//2+4,'huge'),
                    (meta['min_exponent']//2-p-20,'tiny')]:
        points = []
        tokens = []
        for sx in (-1,1):
            for sy in (-1,1):
                for x,y in [(m,m-1),(m-1,m-2),(m,m),(m-1,m-1)]:
                    tokens.append((dyadic_decimal(sx*x,k),dyadic_decimal(sy*y,k)))
                    points.append((dyadic_value(sx*x,k),dyadic_value(sy*y,k)))
        yield make_case('exact-near-parallel-'+name, tokens, points)
    for i in range(40):
        values = [(rng.randint(-2**20,2**20),rng.randint(-80,80)) for _ in range(2*rng.randint(1,80))]
        tokens = [(dyadic_decimal(*values[j]),dyadic_decimal(*values[j+1])) for j in range(0,len(values),2)]
        points = [(dyadic_value(*values[j]),dyadic_value(*values[j+1])) for j in range(0,len(values),2)]
        if i % 3 == 0:
            tokens += tokens[:4]
            points += points[:4]
        yield make_case('seeded-exact-dyadic-'+str(i), tokens, points)
    # Cache a small exact palette's ranks, while checking every returned ID.
    palette = [('0','0'),('-0','+0'),('1','0'),('2','0'),('1','1'),('2','2'),
               ('0','1'),('0','2'),('-1','1'),('-1','0'),('-2','0'),('-1','-1'),
               ('0','-1'),('0','-2'),('1','-1'),('2','-2'),('0.5','0.25')]
    large = [palette[i % len(palette)] for i in range(200000)]
    rng.shuffle(large)
    yield make_case('maximum-n-shuffled-repeated-rays-and-identities', large)
    # Distinct directions also exercise n log n comparison work, not only duplicates.
    distinct = [('1048576',str(i)) for i in range(-100000,100000)]
    rng.shuffle(distinct)
    yield make_case('maximum-n-shuffled-distinct-directions', distinct)


def rounding_cases():
    near = '1.0000000000000000000000000000000000000001'
    yield 'decimal-rounding-collision', [('1',near),(near,'1'),('1','1'),('0','-0'),('-0','+0')]
    yield 'decimal-rounding-general', [('0.1','0.3'),('0.2','0.6'),('0.3','0.9'),
        ('1e300','1e-300'),('1e-300','1e300'),('-1e300','1e-300'),
        ('0.100000000000000000001','0.300000000000000000001'),
        ('-0.1','-0.3'),('0','0'),('+0.0','-0.0')]


def parse_hex(token):
    # Exact integer arithmetic on printf's hexadecimal representation of stored R.
    match = re.fullmatch(r'([+-]?)0x([0-9a-f]+)(?:\.([0-9a-f]*))?p([+-]?\d+)',token.lower())
    assert match, token
    sign, whole, frac, exponent = match.groups()
    frac = frac or ''
    m = int(whole+frac,16) * (-1 if sign == '-' else 1)
    return dyadic_value(m,int(exponent)-4*len(frac))


def definition(path, name):
    text = path.read_text()
    begin = text.index('struct '+name+'\n')
    opening = text.index('{',begin)
    end, depth = opening+1, 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    assert text[end] == ';'
    return text[begin:end+1]+'\n'


def local_headers(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT), path
    if path in seen:
        return seen
    seen.add(path)
    for inc in re.findall(r'^\s*#include "([^"\n]+)"\s*$',path.read_text(),re.M):
        # The unchanged-body precision probe is generated and bound separately.
        if inc == 'real-polar-type-probes.hpp':
            continue
        local_headers(path.parent/inc,seen)
    return seen


def selected_metadata(prototype):
    rows = json.loads((ROOT/'docs/usage-examples.json').read_text())
    catalog = json.loads((ROOT/'docs/catalog.json').read_text())
    row = [r for r in rows if r['id'] == EXAMPLE]
    entries = [r for r in catalog if r[1] in ('RealPlane','RealPolarLess')]
    if not prototype:
        assert len(row) == 1 and {r[1] for r in entries} == {'RealPlane','RealPolarLess'}
    return dict(registration=row,catalog=entries)


def snapshot(compiler, prototype):
    files = local_headers(DRIVER) | local_headers(CORE)
    files.update([Path(__file__).resolve(),ROOT/'tools/usage_examples.py',ROOT/'tests/compiler_config.py'])
    files.update(p for p in FIXTURES.rglob('*') if p.is_file())
    printed = ROOT/'docs/usage'/f'{EXAMPLE}.cpp'
    if not prototype:
        files.add(printed)
    front = subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()
    frontend = Path(shutil.which(front) or front).resolve()
    assert frontend.is_file(), front
    metadata = selected_metadata(prototype)
    return dict(sources={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(files)},
                selected_metadata=metadata,metadata_sha256=sha(json.dumps(metadata,sort_keys=True).encode()),
                compiler_binaries={str(p):sha(p.read_bytes()) for p in (compiler,frontend)})


def no_core_dump():
    _, hard = resource.getrlimit(resource.RLIMIT_CORE)
    resource.setrlimit(resource.RLIMIT_CORE,(0,hard))


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE') not in (None,'','0'):
        raise SystemExit('Run without Python optimization: validation assertions must remain enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--prototype',action='store_true',help='Explicitly non-publication pre-registration development run')
    ap.add_argument('--report',type=Path)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(ROOT/'tools'),str(ROOT/'tests')]
    from compiler_config import CXX
    from usage_examples import records, expand
    san = args.sanitize or any(os.getenv(k)=='1' for k in ('SANITIZE','CPC_SANITIZE'))
    mode = 'sanitizer' if san else 'normal'
    base = ROOT/'build/real-polar-order'
    base.mkdir(parents=True,exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=mode+'-',dir=base))
    report_path = args.report.resolve() if args.report else work/'report.json'
    if not any(report_path.is_relative_to(ROOT/p) for p in ('build','verification')):
        ap.error('--report must remain under repository build/ or verification/')
    report_path.parent.mkdir(parents=True,exist_ok=True)
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    assert compiler.is_file(), 'No compiler found'
    env = os.environ.copy()
    for key in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS'):
        env.pop(key,None)
    if san:
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    flags = ['-std=c++20','-Wall','-Wextra','-frounding-math'] + (['-O1','-g',
        '-fsanitize=address,undefined,float-cast-overflow','-fno-sanitize-recover=all',
        '-fno-omit-frame-pointer'] if san else ['-O2'])
    report = dict(status='running',development_only=args.prototype,mode=mode,id=EXAMPLE,kind='api',seed=SEED,
        scope='Local bounded represented-binary polar API evidence; no online AC, official judge, arbitrary precision, exact source decimals, other RealPlane predicates, alternate-platform certification or full-suite claim. Prototype runs are development only.',
        oracle='Core: independently generated signed cpp_int dyadics, aligned exact products and squared-length ties. Driver: four quadrant rational slopes plus exact norm and original ID. Rounded decimal cases recover parsed R with hexadecimal printf independently of frexp.',
        started_at=datetime.now(timezone.utc).isoformat(),compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
        flags=flags,environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','CXX','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH')},
        forms={},executions=[])
    before = None
    def save():
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    def execute(label, exe, data=b'', args=(), expected_rc=0, timeout=180, dump=False):
        stem = work/f'run-{len(report["executions"]):04}-{label}'
        result = subprocess.run([str(exe),*args],input=data,capture_output=True,env=env,cwd=ROOT,
                                timeout=timeout,preexec_fn=no_core_dump if dump else None)
        stem.with_suffix('.stdout').write_bytes(result.stdout)
        stem.with_suffix('.stderr').write_bytes(result.stderr)
        entry = dict(label=label,command=[str(exe),*args],returncode=result.returncode,
                     input_sha256=sha(data),stdout_sha256=sha(result.stdout),stderr_sha256=sha(result.stderr),
                     stdout_file=str(stem.with_suffix('.stdout').relative_to(ROOT)),
                     stderr_file=str(stem.with_suffix('.stderr').relative_to(ROOT)))
        report['executions'].append(entry)
        if result.returncode != expected_rc or (expected_rc == 0 and result.stderr):
            stem.with_suffix('.in').write_bytes(data)
            raise AssertionError((label,result.returncode,result.stderr[:1500]))
        return result
    def compile_form(label, source, extra=()):
        cpp = source if isinstance(source,Path) else work/(label+'.cpp')
        if not isinstance(source,Path):
            cpp.write_text(source)
        exe = work/label
        command = [str(compiler),*flags,*extra,str(cpp),'-o',str(exe)]
        result = subprocess.run(command,capture_output=True,env=env,cwd=ROOT,timeout=180)
        report['forms'][label] = dict(compile_command=command,source=str(cpp.relative_to(ROOT)),
            source_sha256=sha(cpp.read_bytes()),compile_returncode=result.returncode,
            compile_stdout=result.stdout.decode(errors='replace'),compile_stderr=result.stderr.decode(errors='replace'))
        assert result.returncode == 0, result.stderr.decode(errors='replace')
        report['forms'][label]['binary_sha256'] = sha(exe.read_bytes())
        return exe
    print('Artifacts:',work,flush=True)
    try:
        before = snapshot(compiler,args.prototype)
        report['before'] = before
        save()
        imported = execute('python-import-only',Path(sys.executable),args=['-B','-c',
            'import runpy; runpy.run_path('+repr(str(Path(__file__).resolve()))+', run_name="import_only_probe")'])
        assert not imported.stdout and not imported.stderr
        optimized = execute('python-optimization-rejected',Path(sys.executable),
            args=['-B','-O',str(Path(__file__).resolve()),'--prototype'],expected_rc=1)
        assert not optimized.stdout and b'validation assertions must remain enabled' in optimized.stderr
        report['runtime_guards'] = dict(import_safe=True,optimized_python_rejected=True,
            python_executable=sys.executable,python_version=sys.version)
        contract = json.loads((FIXTURES/'contract.json').read_text())
        source_record = json.loads((FIXTURES/'source.json').read_text())
        assert contract['kind'] == 'api' and contract['symbol'] == 'RealPolarLess'
        assert contract['example'] == EXAMPLE and contract['domain']['n'] == [0,200000]
        assert contract['custom_sample'] == dict(input=(FIXTURES/'sample.in').read_text(),output=(FIXTURES/'sample.out').read_text())
        assert source_record['pdf_sha256'] == 'b5ce46f7cf542be2d9846d8f01898c8ccd7f4619521036b0b7895206895745f3'
        assert source_record['source_scalar'] == 'double' and source_record['physical_code_page'] == 200
        body = definition(HEADER,'RealPolarLess')
        probe_text = ''.join('namespace test_'+name+'\n{\nstruct RealPlane { using R = '+name+'; struct Point { R x,y; }; };\n'+body+'}\n' for name in ('float','double'))
        (work/'real-polar-type-probes.hpp').write_text(probe_text)
        report['precision_probes'] = dict(class_body_sha256=sha(body.encode()),generated_header_sha256=sha(probe_text.encode()),
            scope='Actual header at native long-double precision; unchanged class body with float/double type suppliers, not another platform or ABI')
        # Build dependencies are standard installed Boost headers or caller include paths.
        core = compile_form('core',CORE,['-DREAL_POLAR_TYPE_PROBES','-I'+str(work)])
        meta = json.loads(execute('type-metadata',core,args=['--metadata']).stdout)
        assert meta['radix'] == 2 and 1 <= meta['digits'] <= 64
        report['actual_type'] = meta
        core_run = execute('all-rounding-core',core,timeout=600)
        results = [json.loads(line) for line in core_run.stdout.splitlines()]
        assert len(results) == 12 and all(r['passed'] for r in results)
        labels = {'actual-long-double','unchanged-body-float','unchanged-body-double'}
        assert {r['label'] for r in results} == labels
        assert all(sum(r['label'] == label for r in results) == 4 for label in labels)
        assert all(len({r['rounding_mode'] for r in results if r['label']==label}) == 4 for label in labels)
        assert {r['digits'] for r in results if r['label']=='actual-long-double'} == {meta['digits']}
        assert {r['digits'] for r in results if r['label']=='unchanged-body-double'} == {53}
        assert {r['digits'] for r in results if r['label']=='unchanged-body-float'} == {24}
        report['core_results'] = results
        for value in ('nan','inf'):
            for coordinate in range(4):
                failed = execute('assertion-'+value+'-'+str(coordinate),core,
                    args=['--invalid',value,str(coordinate)],expected_rc=-signal.SIGABRT,dump=True)
                assert b'assert' in failed.stderr.lower(), 'Failure did not identify an assertion'
        driver = DRIVER.read_text()
        begin = re.search(r'(?m)^int main\(\)',driver)
        assert begin
        snippet = driver[begin.start():]
        programs = {'direct':DRIVER}
        if args.prototype:
            programs['prototype-expanded'] = expand(driver,DRIVER.parent,set())
        else:
            matches = [r for r in records() if r['id'] == EXAMPLE]
            assert len(matches) == 1
            row = matches[0]
            assert row['symbol'] == 'RealPolarLess' and row['kind'] == 'api'
            assert row['driver'] == str(DRIVER.relative_to(ROOT))
            assert row['requires'] == ['RealPlane','RealPolarLess'] and not row.get('also_covers')
            assert snippet == row['snippet'] == (ROOT/row['snippet_file']).read_text()
            assert sha(row['program'].encode()) == row['program_sha256']
            report['registered_program_sha256'] = row['program_sha256']
            programs['registered-expanded'] = row['program']
        context = definition(PLANE,'RealPlane') + body
        programs['actual-minimal-copied-context'] = '#include <bits/stdc++.h>\nusing namespace std;\n'+context+snippet
        report.update(copied_context_sha256=sha(context.encode()),snippet_sha256=sha(snippet.encode()))
        checks = list(cases(meta))
        for name,tokens in rounding_cases():
            data = (str(len(tokens))+'\n'+''.join(x+' '+y+'\n' for x,y in tokens)).encode()
            decoded = execute(name+'-decode',core,data,args=['--decode'])
            values = decoded.stdout.decode().split()
            assert len(values) == 2*len(tokens)
            points = [(parse_hex(values[i]),parse_hex(values[i+1])) for i in range(0,len(values),2)]
            case = make_case(name,tokens,points)
            case['oracle'] = 'actual-parsed-values-from-independent-hexadecimal-output'
            if name == 'decimal-rounding-collision':
                assert points[0] == points[1] == points[2] == (F(1),F(1))
                assert case['expected'] == [4,5,1,2,3]
            checks.append(case)
        for bad in (b'',b'2 1',b'1 1 3',b'0 2 3',b'1 2 x'):
            try:
                validate_output(bad,[1,2,3])
            except AssertionError:
                pass
            else:
                raise AssertionError('Output checker accepted negative control')
        report['checker_negative_controls'] = 5
        # Supply every pair so missing input cannot mask a removed upper-count guard.
        too_many_points = b'200001\n' + b'0 0\n' * 200001
        invalid = [('missing-count',b''),('malformed-count',b'bad\n'),('negative-count',b'-1\n'),
            ('too-many-points',too_many_points),('count-overflow',b'99999999999999999999999999999\n'),
            ('missing-pair',b'1\n'),('missing-coordinate',b'1\n0\n'),('missing-later-pair',b'2\n0 0\n'),
            ('bad-coordinate',b'1\nno 0\n'),('bad-last-coordinate',b'1\n0 no\n'),
            ('nan-coordinate',b'1\nnan 0\n'),('inf-coordinate',b'1\n0 inf\n'),
            ('negative-inf-coordinate',b'1\n-inf 0\n'),('overflow-coordinate',b'1\n1e999999 0\n')]
        report['valid_cases_per_form'] = len(checks)
        report['invalid_cases_per_form'] = len(invalid)
        report['maximum_n'] = max(c['n'] for c in checks)
        report['case_manifest'] = [dict(name=c['name'],n=c['n'],oracle=c['oracle'],input_sha256=sha(c['data']),
            expected_ids_sha256=sha((' '.join(map(str,c['expected']))+'\n').encode())) for c in checks]
        # A test-sensitivity mutation only, never a production execution or valid-domain claim.
        mutation_base = expand(driver,DRIVER.parent,set())
        guard = ' || n > 200000'
        assert mutation_base.count(guard) == 1
        mutation = mutation_base.replace(guard,'',1)
        mutant = compile_form('upper-count-guard-mutation',mutation)
        report['forms']['upper-count-guard-mutation']['scope'] = 'Checker guard sensitivity control only; production source is unchanged'
        accepted = execute('mutation-only-upper-count-removed',mutant,too_many_points,timeout=300)
        validate_output(accepted.stdout,list(range(1,200002)))
        report['upper_count_guard_control'] = dict(
            classification='Negative-test sensitivity control, not production execution or an expanded valid domain',
            supplied_count=200001,supplied_finite_pairs=200001,
            original_source_sha256=sha(mutation_base.encode()),mutated_source_sha256=sha(mutation.encode()),
            only_source_change='Remove the single || n > 200000 guard',
            input_sha256=sha(too_many_points),mutant_accepts=True,expected_production_exit=1)
        save()
        for form,program in programs.items():
            exe = compile_form(form,program)
            report['forms'][form]['valid_passed'] = 0
            for case in checks:
                result = execute(form+'-'+case['name'],exe,case['data'],timeout=300)
                validate_output(result.stdout,case['expected'])
                report['forms'][form]['valid_passed'] += 1
            for name,data in invalid:
                result = execute(form+'-invalid-'+name,exe,data,expected_rc=1)
                assert not result.stdout and not result.stderr, (form,name,result.stdout,result.stderr)
            report['forms'][form]['invalid_passed'] = len(invalid)
            diagnostics = [('accepted-numeric-prefix',b'1\n0 0junk\n'),
                           ('ignored-extra-trailing-tokens',b'1\n0 0\n42 13\n')]
            for name,data in diagnostics:
                result = execute(form+'-outside-protocol-'+name,exe,data)
                validate_output(result.stdout,[1])
            report['forms'][form]['outside_protocol_diagnostics'] = [name for name,_ in diagnostics]
            assert sha(exe.read_bytes()) == report['forms'][form]['binary_sha256']
            print(mode,form,len(checks),'valid and',len(invalid),'invalid cases PASS',flush=True)
            save()
        assert sha(mutant.read_bytes()) == report['forms']['upper-count-guard-mutation']['binary_sha256']
        assert sha((work/'real-polar-type-probes.hpp').read_bytes()) == report['precision_probes']['generated_header_sha256']
        assert snapshot(compiler,args.prototype) == before, 'Sources, metadata or compiler changed during run'
        report['status'] = 'passed'
    except BaseException:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        raise
    finally:
        try:
            report['after'] = snapshot(compiler,args.prototype)
            report['inputs_unchanged'] = report['after'] == before
        except BaseException:
            report['after_error'] = traceback.format_exc()
            report['inputs_unchanged'] = False
        if not report['inputs_unchanged']:
            report['status'] = 'failed'
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        save()
        print('Report:',report_path,flush=True)


if __name__ == '__main__':
    main()
