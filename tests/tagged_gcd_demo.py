#!/usr/bin/env python3
"""Independent custom tagged-GCD API checks: direct, expanded, printed, and core."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'tests/fixtures/tagged-gcd-demo'
DRIVER = ROOT / 'docs/usage-drivers/tagged-gcd-demo.cpp'
CORE_TEST = ROOT / 'tests/tagged_gcd_demo_core.cpp'
HEADER = ROOT / 'src/compact/gcd_sequence.hpp'
EXAMPLE = 'example-224'
PRINTED = ROOT / f'docs/usage/{EXAMPLE}.cpp'

MAX = 2**64 - 1


def sha(data):
    return hashlib.sha256(data).hexdigest()


def literal(name, start, ops):
    a, out, peak = start[:], [], len(start)
    assert 0 <= len(a) <= 200000 and len(ops) <= 100000
    assert all(0 <= v <= MAX and t in (0, 1) for v, t in a)
    for op, *args in ops:
        if op == 'I':
            k, v, t = args
            assert 0 <= k <= len(a) and 0 <= v <= MAX and t in (0, 1)
            a.insert(k, (v, t))
        elif op in ('S', 'T'):
            k = args[0]
            assert 1 <= k <= len(a)
            v, t = a[k-1]
            if op == 'S':
                v = args[1]
                assert 0 <= v <= MAX
            else:
                t ^= 1
            a[k-1] = v, t
        else:
            l, r = args[:2]
            assert 1 <= l <= r <= len(a)
            if op == 'E':
                del a[l-1:r]
            else:
                assert op == 'Q' and args[2] in (0, 1)
                selected = [v for v, t in a[l-1:r] if t == args[2]]
                out.append(str(math.gcd(*selected)) if selected else 'NONE')
        peak = max(peak, len(a))
        assert peak <= 300000
    return serialize(name, start, ops, out, peak)


def serialize(name, start, ops, out, peak):
    data = f'{len(start)} {len(ops)}\n' + ''.join(f'{v} {t}\n' for v, t in start)
    data += ''.join(' '.join(map(str, op)) + '\n' for op in ops)
    return dict(name=name, input=data, expected=''.join(x+'\n' for x in out),
                n=len(start), operations=len(ops), queries=len(out), peak=peak)


def cases():
    sample = (HERE/'sample.in').read_text().splitlines()
    n, q = map(int, sample[0].split())
    start = [tuple(map(int, s.split())) for s in sample[1:n+1]]
    ops = [(s[0], *map(int, s.split()[1:])) for s in sample[n+1:]]
    assert len(ops) == q
    case = literal('custom-sample', start, ops)
    assert case['expected'] == (HERE/'sample.out').read_text()
    yield case
    yield literal('empty-no-operations', [], [])
    yield literal('empty-head-tail-delete-all-reinsert', [], [
        ('I',0,0,0),('Q',1,1,0),('Q',1,1,1),('S',1,MAX),('Q',1,1,0),
        ('T',1),('Q',1,1,0),('Q',1,1,1),('I',0,12,0),('I',2,18,0),
        ('Q',1,3,0),('E',1,2),('Q',1,1,0),('E',1,1),('I',0,MAX,1),('Q',1,1,1)])
    for n in (1, 2, 7, 16):
        for tag in (0, 1):
            a = [(v, tag) for v in ([0, MAX, 6, 18]*n)[:n]]
            ops = []
            for phase in range(5):
                if phase == 1: ops += [('S', k, 0) for k in range(1,n+1)]
                if phase == 2: ops += [('T', k) for k in range(1,n+1)]
                if phase == 3: ops += [('S', k, MAX) for k in range(1,n+1)]
                if phase == 4: ops += [('T', k) for k in range(1,n+1,2)]
                ops += [('Q',l,r,t) for l in range(1,n+1) for r in range(l,n+1) for t in (0,1)]
            yield literal(f'all-ranges-n{n}-tag{tag}', a, ops)
    rng = random.Random(20261002)
    for trial in range(120):
        start = [(rng.choice([0,1,12,18,MAX]),rng.randrange(2)) for _ in range(rng.randrange(40))]
        size, ops = len(start), []
        for _ in range(800):
            op = rng.choice('IESTQQ') if size else 'I'
            v = rng.choice([0,1,MAX,rng.getrandbits(64)])
            if op == 'I':
                ops.append((op,rng.randrange(size+1),v,rng.randrange(2))); size += 1
            elif op == 'E':
                l = rng.randint(1,size); r = rng.randint(l,size)
                ops.append((op,l,r)); size -= r-l+1
            elif op == 'S': ops.append((op,rng.randint(1,size),v))
            elif op == 'T': ops.append((op,rng.randint(1,size)))
            else:
                l = rng.randint(1,size); r = rng.randint(l,size)
                ops.append((op,l,r,rng.randrange(2)))
        yield literal(f'random-{trial:03}',start,ops)
    # Cheap exact scalar identities, no O(n*q) vector scans at selected maximum n/q.
    n = 200000
    start, ops, out = [(0,0)]*n, [], []
    for i in range(50000):
        pos = 1+(i*7919)%n
        ops.append(('S',pos,MAX))
        if i % 3 == 0:
            ops.append(('Q',1,n,0)); out.append(str(MAX))
        elif i % 3 == 1:
            ops.append(('Q',1,n,1)); out.append('NONE')
        else:
            ops.append(('Q',pos,pos,0)); out.append(str(MAX))
    yield serialize('maximum-n-q-observable',start,ops,out,n)
    ops = [('I',n+i,MAX,1) for i in range(99998)] + [('Q',1,299998,0),('Q',1,299998,1)]
    yield serialize('near-maximum-peak-observable',start,ops,['0',str(MAX)],299998)
    ops = [('I',n+i,MAX,1) for i in range(100000)]
    yield serialize('exact-maximum-peak-no-output-smoke',start,ops,[],300000)


def local_headers(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT), path
    if path in seen:
        return seen
    seen.add(path)
    for inc in re.findall(r'^\s*#include "([^"\n]+)"\s*$', path.read_text(), re.M):
        local_headers(path.parent / inc, seen)
    return seen


def selected_metadata():
    registration = [r for r in json.loads((ROOT/'docs/usage-examples.json').read_text()) if r['id'] == EXAMPLE]
    catalog = [r for r in json.loads((ROOT/'docs/catalog.json').read_text()) if r[1] == 'GcdSequenceTreap']
    assert len(registration) == len(catalog) == 1
    return dict(registration=registration[0], catalog=catalog[0])


def snapshot(compiler):
    files = local_headers(DRIVER) | local_headers(CORE_TEST)
    files.update((Path(__file__).resolve(), PRINTED, ROOT/'tests/compiler_config.py', ROOT/'tools/usage_examples.py'))
    files.update(p for p in HERE.iterdir() if p.is_file())
    # GCC launches cc1plus separately; hash the frontend as well as the driver.
    frontend_name = subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()
    frontend = Path(shutil.which(frontend_name) or frontend_name).resolve()
    assert frontend.is_file(), f'Cannot resolve compiler frontend: {frontend_name}'
    metadata = selected_metadata()
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted(files)},
                selected_metadata=metadata, selected_metadata_sha256=sha(json.dumps(metadata,sort_keys=True).encode()),
                compiler_executable=str(compiler),compiler_sha256=sha(compiler.read_bytes()),
                frontend_executable=str(frontend),frontend_sha256=sha(frontend.read_bytes()))


def programs():
    sys.path.insert(0,str(ROOT/'tools'))
    from usage_examples import records
    matches = [r for r in records() if r['id'] == EXAMPLE]
    assert len(matches) == 1
    row = matches[0]
    assert row['kind'] == 'api' and row['symbol'] == 'GcdSequenceTreap'
    assert row['driver'] == str(DRIVER.relative_to(ROOT)) and row['requires'] == ['GcdSequenceTreap']
    assert not row.get('also_covers')
    driver = DRIVER.read_text()
    start = re.search(r'(?m)^int main\(\)',driver)
    assert start and driver[start.start():] == row['snippet']
    printed = PRINTED.read_text()
    assert printed == row['snippet'], 'Generated printed snippet is stale'
    assert sha(row['program'].encode()) == row['program_sha256']
    # This standalone component is the declared context of the actual printed main.
    header = HEADER.read_text()
    assert re.findall(r'(?m)^struct (\w+)',header) == ['GcdSequenceTreap']
    context = '\n'.join(line for line in header.splitlines() if line.strip() != '#pragma once')+'\n'
    pasted = '#include <bits/stdc++.h>\nusing namespace std;\n'+context+printed
    return dict(complete_driver=driver,registered_program=row['program'],printed_copy=pasted,
                separate_core=CORE_TEST.read_text()), dict(
                    program_sha256=row['program_sha256'], printed_snippet_sha256=sha(printed.encode()),
                    printed_context=dict(symbol='GcdSequenceTreap',path=str(HEADER.relative_to(ROOT)),
                                         source_sha256=sha(header.encode()),context_sha256=sha(context.encode())))


def main():
    if not __debug__:
        raise SystemExit('Run without python -O: validation assertions must remain enabled')
    sys.path.insert(0,str(ROOT/'tests'))
    from compiler_config import CXX
    ap = argparse.ArgumentParser(description=__doc__)
    default = 'sanitizer' if any(os.getenv(k)=='1' for k in ('SANITIZE','CPC_SANITIZE')) else 'normal'
    ap.add_argument('--mode',choices=('normal','sanitizer','both'),default=default)
    ap.add_argument('--report',type=Path,help='JSON report path under build/ or verification/')
    args = ap.parse_args()
    report_path = args.report.resolve() if args.report else None
    if report_path and not any(report_path.is_relative_to(ROOT/p) for p in ('build','verification')):
        ap.error('--report must remain under repository build/ or verification/')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    assert compiler.is_file(), 'No compiler found'
    build = ROOT/'build'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='tagged-gcd-demo-',dir=build))
    if report_path is None: report_path = work/'report.json'
    report_path.parent.mkdir(parents=True,exist_ok=True)
    before = None
    report = dict(passed=False,mode=args.mode,id=EXAMPLE,kind='api',component='GcdSequenceTreap',
                  scope='Custom API protocol; finite local checks, no official constraints, online AC, adversarial balance or full-suite claim',
                  created=datetime.now(timezone.utc).isoformat(), modes=[], executions=[],
                  compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
                  pie='compiler default',quarantine='ASan default',
                  oracle='Python list/math.gcd; cheap exact scalar identities at selected maximum envelope; separate direct API structural assertions')
    def save():
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Artifacts:',work,flush=True)
    try:
        before = snapshot(compiler)
        report['before'] = before
        sources, provenance = programs()
        report.update(provenance)
        checks = list(cases())
        contract = json.loads((HERE/'contract.json').read_text())
        counts = contract['counts']
        assert contract['kind'] == 'api' and contract['symbol'] == 'GcdSequenceTreap'
        assert len(checks) == counts['driver_cases_per_form'] == 134
        assert sum(c['operations'] for c in checks) == counts['operations_per_form'] == 399572
        assert sum(c['queries'] for c in checks) == counts['queries_per_form'] == 83267
        assert contract['custom_sample'] == dict(input=(HERE/'sample.in').read_text(),output=(HERE/'sample.out').read_text())
        assert contract['domain']['n'] == [0,200000] and contract['domain']['q'] == [0,100000]
        assert contract['domain']['peak_live_max'] == 300000
        fixtures = work/'cases.jsonl'
        fixtures.write_text(''.join(json.dumps(c,sort_keys=True)+'\n' for c in checks))
        report.update(cases_file=str(fixtures.relative_to(ROOT)),cases_sha256=sha(fixtures.read_bytes()),
                      case_count_per_form=len(checks),operations_per_form=sum(c['operations'] for c in checks),
                      queries_per_form=sum(c['queries'] for c in checks),domain=contract['domain'],counts=counts)
        modes = ('normal','sanitizer') if args.mode == 'both' else (args.mode,)
        for mode in modes:
            report['modes'].append(mode)
            flags = ['-std=c++20','-Wall','-Wextra'] + (['-O2'] if mode=='normal' else
                     ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'])
            env = os.environ.copy()
            for key in ('ASAN_OPTIONS','LSAN_OPTIONS','UBSAN_OPTIONS'): env.pop(key,None)
            if mode=='sanitizer': env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            for form, program in sources.items():
                source = DRIVER if form=='complete_driver' else CORE_TEST if form=='separate_core' else work/f'{mode}-{form}.cpp'
                if form not in ('complete_driver','separate_core'): source.write_text(program)
                exe = work/f'{mode}-{form}'
                command = [str(compiler),*flags,str(source),'-o',str(exe)]
                entry = dict(mode=mode,form=form,compile_command=command,completed_cases=0,cases=[],
                             source=str(source.relative_to(ROOT)),source_sha256=sha(source.read_bytes()),
                             sanitizer_options={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')})
                report['executions'].append(entry); save()
                cp = subprocess.run(command,capture_output=True,text=True,timeout=120,env=env,cwd=ROOT)
                entry['compile'] = dict(returncode=cp.returncode,stdout=cp.stdout,stderr=cp.stderr)
                assert cp.returncode == 0, cp.stderr
                entry['binary_sha256'] = sha(exe.read_bytes())
                selected = checks if form!='separate_core' else [dict(name='core-build-recycle-peak',input='',expected='PASS builds=7 recycling_rounds=128 queries=523\n')]
                output_hash = hashlib.sha256()
                for i,c in enumerate(selected):
                    stem = work/f'{mode}-{form}-{i:03}'
                    try:
                        result = subprocess.run([str(exe)],input=c['input'],text=True,capture_output=True,timeout=180,env=env,cwd=ROOT)
                    except subprocess.TimeoutExpired as error:
                        for suffix, value in [('.stdout',error.stdout or b''),('.stderr',error.stderr or b'')]:
                            stem.with_suffix(suffix).write_bytes(value if isinstance(value,bytes) else value.encode())
                        stem.with_suffix('.in').write_text(c['input'])
                        stem.with_suffix('.expected').write_text(c['expected'])
                        entry['cases'].append(dict(name=c['name'],passed=False,timeout=True,artifact_prefix=str(stem.relative_to(ROOT))))
                        raise
                    stem.with_suffix('.stdout').write_text(result.stdout)
                    stem.with_suffix('.stderr').write_text(result.stderr)
                    ok = result.returncode==0 and result.stdout==c['expected'] and not result.stderr
                    entry['cases'].append(dict(name=c['name'],passed=ok,returncode=result.returncode,
                                               input_sha256=sha(c['input'].encode()),expected_sha256=sha(c['expected'].encode()),
                                               stdout_file=str(stem.with_suffix('.stdout').relative_to(ROOT)),stderr_file=str(stem.with_suffix('.stderr').relative_to(ROOT)),
                                               stdout_sha256=sha(result.stdout.encode()),stderr_sha256=sha(result.stderr.encode())))
                    if not ok:
                        stem.with_suffix('.in').write_text(c['input']); stem.with_suffix('.expected').write_text(c['expected'])
                        raise AssertionError(f'{mode} {form} {c["name"]}: {result.stderr[:1000]}')
                    output_hash.update((json.dumps(result.stdout)+'\n').encode())
                    entry['completed_cases'] += 1
                entry['stdout_sha256'] = output_hash.hexdigest()
                assert sha(exe.read_bytes()) == entry['binary_sha256']
                assert sha(source.read_bytes()) == entry['source_sha256']
                print(mode,form,entry['completed_cases'],'PASS',flush=True); save()
            assert len({e['stdout_sha256'] for e in report['executions'] if e['mode']==mode and e['form']!='separate_core'}) == 1
        assert sha(fixtures.read_bytes()) == report['cases_sha256']
        assert snapshot(compiler) == before, 'Inputs, selected metadata, or compiler changed during run'
        report['passed'] = True
    except BaseException as e:
        report['error'] = repr(e)
        raise
    finally:
        try:
            report['after'] = snapshot(compiler)
            report['source_unchanged'] = before is not None and report['after'] == before
        except BaseException as e:
            report.update(after_error=repr(e),source_unchanged=False)
        if not report['source_unchanged']: report['passed'] = False
        save()
        print('Report:',report_path,flush=True)


if __name__ == '__main__':
    main()
