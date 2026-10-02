#!/usr/bin/env python3
"""CF732F properties, independent orientation optimum, and actual minimal copy runtime."""
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT/'verify/codeforces/732F.compact.cpp'
FIXTURES = ROOT/'tests/fixtures/edge-compression-732f'
SEED = 732
NORMAL_STACK = 256 << 20
SANITIZER_STACK = 1 << 30


def sha(data):
    return hashlib.sha256(data).hexdigest()


def set_child_soft_stack(size):
    _, hard = resource.getrlimit(resource.RLIMIT_STACK)
    resource.setrlimit(resource.RLIMIT_STACK, (size if hard == resource.RLIM_INFINITY else min(size, hard), hard))
    # Disable only child soft core-dump limit; leave its hard limit unchanged.
    _, hard_core = resource.getrlimit(resource.RLIMIT_CORE)
    resource.setrlimit(resource.RLIMIT_CORE, (0, hard_core))


def measure_child():
    # Fresh small helper avoids charging Python test-generator memory inherited at fork.
    exe, inp, out, receipt, stack = sys.argv[2:]
    stack = int(stack)
    before = resource.getrlimit(resource.RLIMIT_STACK)
    start = time.monotonic()
    with open(inp, 'rb') as f, open(out, 'wb') as g:
        p = subprocess.run([exe], stdin=f, stdout=g, stderr=subprocess.PIPE,
                           preexec_fn=lambda: set_child_soft_stack(stack), timeout=180)
    actual = stack if before[1] == resource.RLIM_INFINITY else min(stack, before[1])
    Path(receipt).write_text(json.dumps(dict(returncode=p.returncode, stderr=p.stderr.decode(errors='replace'),
        wall_seconds=time.monotonic()-start, peak_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        requested_soft_stack_bytes=stack, child_soft_stack_bytes=actual, unchanged_hard_stack_bytes=before[1]))+'\n')


def encode(n, edges):
    return (f'{n} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)).encode()


def objective(n, edges):
    reach = [1 << i for i in range(n)]
    for u,v in edges:
        reach[u-1] |= 1 << (v-1)
    for k in range(n):
        for i in range(n):
            if reach[i] >> k & 1:
                reach[i] |= reach[k]
    return min(x.bit_count() for x in reach)


def connected(n, edges):
    return objective(n, edges+[(v,u) for u,v in edges]) == n


def optimum(n, edges):
    # No lowlink/component implementation used: enumerate every directed assignment.
    return max(objective(n, [e[::-1] if mask >> i & 1 else e for i,e in enumerate(edges)])
               for mask in range(1 << len(edges)))


def validate(n, edges, output, expected, large=False):
    words = output.split()
    assert len(words) == 1+2*len(edges), 'Wrong token count'
    values = list(map(int, words))
    assert values[0] == expected, 'Wrong optimum'
    direction = list(zip(values[1::2], values[2::2]))
    for original, oriented in zip(edges, direction):
        assert oriented == original or oriented == original[::-1], 'Wrong edge ID/endpoints'
    if not large:
        assert objective(n, direction) == expected, 'Orientation does not achieve optimum'
    else:
        # Structural families have an optimum root component containing vertex 1.
        # Every vertex reaches 1 and 1 reaches exactly K: achieved minimum is K.
        def reaches(reverse):
            g = [[] for _ in range(n+1)]
            for u,v in direction:
                if reverse:
                    u,v = v,u
                g[u].append(v)
            seen = bytearray(n+1)
            seen[1] = 1
            queue = [1]
            for u in queue:
                for v in g[u]:
                    if not seen[v]:
                        seen[v] = 1
                        queue.append(v)
            return len(queue)
        assert reaches(True) == n and reaches(False) == expected


def small_cases():
    rng = random.Random(SEED)
    sample = list(map(int,(FIXTURES/'sample.in').read_text().split()))
    n = sample[0]
    edges = list(zip(sample[2::2],sample[3::2]))
    assert sample[1] == len(edges)
    yield 'official-sample', n, edges, 'official-domain'
    for n in range(2,6):
        pairs = list(itertools.combinations(range(1,n+1),2))
        for mask in range(1 << len(pairs)):
            edges = [e for i,e in enumerate(pairs) if mask >> i & 1]
            if not connected(n,edges):
                continue
            rng.shuffle(edges)
            edges = [e[::-1] if rng.randrange(2) else e for e in edges]
            yield f'exhaustive-{n}-{mask}',n,edges,'official-domain'
    for t in range(100):
        n = rng.randrange(2,9)
        edges = {(rng.randrange(1,v),v) for v in range(2,n+1)}
        possibilities = list(itertools.combinations(range(1,n+1),2))
        rng.shuffle(possibilities)
        for e in possibilities[:rng.randrange(5)]:
            edges.add(e)
        edges = list(edges)
        rng.shuffle(edges)
        edges = [e[::-1] if rng.randrange(2) else e for e in edges]
        yield f'random-{t}',n,edges,'official-domain'
    # Largest block away from DFS vertex 1, branches and tied largest blocks.
    yield 'root-away',7,[(1,2),(2,3),(3,4),(4,2),(1,5),(5,6),(5,7)],'official-domain'
    yield 'tied-largest',6,[(1,2),(2,3),(3,1),(3,4),(4,5),(5,6),(6,4)],'official-domain'
    yield 'singleton-api',1,[],'wider-api'
    yield 'loop-api',1,[(1,1),(1,1)],'wider-api'
    for t in range(100):
        n = rng.randrange(1,7)
        edges = [(rng.randrange(1,v),v) for v in range(2,n+1)]
        edges += [(rng.randrange(1,n+1),rng.randrange(1,n+1)) for _ in range(10-len(edges))]
        rng.shuffle(edges)
        yield f'multigraph-{t}',n,edges,'wider-api'


def large_cases():
    n = 400000
    yield 'path',n,[(i+1,i) for i in range(1,n)],1
    yield 'cycle',n,[(i,i+1) for i in range(1,n)]+[(n,1)],n
    yield 'star',n,[(i,1) for i in range(2,n+1)],1
    yield 'cycle-tail',n,[(i,i+1) for i in range(1,100001)]+[(100001,1)]+[(i+1,i) for i in range(100001,n)],100001


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


def main():
    assert __debug__ and os.environ.get('PYTHONOPTIMIZE') in (None,'','0'), 'Assertions required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sanitize',action='store_true')
    ap.add_argument('--prototype',action='store_true',help='Non-publication pre-registration development run')
    ap.add_argument('--report',type=Path)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(ROOT/'tools'),str(ROOT/'tests')]
    from compiler_config import CXX
    from usage_examples import records, expand
    san = args.sanitize or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'
    stack = SANITIZER_STACK if san else NORMAL_STACK
    root = ROOT/'build/edge-compression-next'
    root.mkdir(parents=True,exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix=mode+'-',dir=root))
    report_path = args.report or out/'report.json'
    report_path.parent.mkdir(parents=True,exist_ok=True)
    text = DRIVER.read_text()
    start = text.index('int main()')
    snippet = text[start:]
    registration = None
    tracked = [Path(__file__).resolve(),DRIVER,ROOT/'src/compact/biconnected_core.hpp',ROOT/'src/compact/graph.hpp',ROOT/'src/compact/edge_components.hpp',ROOT/'tools/usage_examples.py',ROOT/'tests/compiler_config.py']
    programs = {'direct':DRIVER}
    if args.prototype:
        programs['prototype-expanded'] = expand(text,DRIVER.parent,set())
    else:
        row = next(r for r in records() if r['symbol'] == 'EdgeCompression' and r['driver'] == str(DRIVER.relative_to(ROOT)))
        assert row['id'] == 'example-227' and row['kind'] == 'application'
        assert row['requires'] == ['BiconnectedCore','EdgeCompression','Lowlink','orient_edges']
        printed = ROOT/row['snippet_file']
        assert row['snippet'] == snippet == printed.read_text()
        snippet = printed.read_text()
        registration = {k:v for k,v in row.items() if k not in ('program','snippet')}
        programs['registered-expanded'] = row['program']
        tracked += [ROOT/'docs/usage-examples.json',ROOT/'docs/catalog.json',printed]
    components = definition(ROOT/'src/compact/biconnected_core.hpp','BiconnectedCore')
    components += definition(ROOT/'src/compact/edge_components.hpp','EdgeCompression')
    components += definition(ROOT/'src/compact/graph.hpp','Lowlink')
    edge_text = (ROOT/'src/compact/edge_components.hpp').read_text()
    components += edge_text.split('// BEGIN orient_edges\n',1)[1].split('// END orient_edges',1)[0]
    programs['actual-minimal-copied-context'] = '#include <bits/stdc++.h>\nusing namespace std;\n'+components+snippet
    tracked += sorted(p for p in FIXTURES.rglob('*') if p.is_file())
    bound = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    frontend = Path(subprocess.check_output([str(compiler),'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    compiler_hashes = {str(p):sha(p.read_bytes()) for p in (compiler,frontend)}
    flags = ['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if san else ['-std=c++20','-O2']
    env = os.environ.copy()
    if san:
        options = [x for x in env.get('ASAN_OPTIONS','').split(':') if x]
        assert not any('quarantine' in x for x in options), 'Default ASan quarantine required'
        options = [x for x in options if not x.startswith(('detect_leaks=','halt_on_error='))]
        env['ASAN_OPTIONS'] = ':'.join(options+['detect_leaks=0','halt_on_error=1'])
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    cases = [(label,n,e,domain,optimum(n,e)) for label,n,e,domain in small_cases()]
    validate(cases[0][1],cases[0][2],(FIXTURES/'sample.out').read_bytes(),cases[0][4])
    # Negative controls ensure checker rejects wrong objective, identity, length and direction quality.
    bad_outputs = [b'2\n1 2\n',b'1\n1 1\n',b'1\n',b'3\n1 2\n2 3\n1 3\n']
    for i,bad in enumerate(bad_outputs):
        try:
            validate(3 if i == 3 else 2,[(1,2),(2,3),(3,1)] if i == 3 else [(1,2)],bad,3 if i == 3 else 1)
        except AssertionError:
            pass
        else:
            raise AssertionError('Checker accepted negative control')
    report = dict(status='running',prototype=args.prototype,mode=mode,seed=SEED,sources=bound,
        registration=registration,compiler_binaries=compiler_hashes,compiler_version=subprocess.check_output([str(compiler),'--version'],text=True),
        flags=flags,environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','CXX','CPATH','CPLUS_INCLUDE_PATH','LIBRARY_PATH','LD_LIBRARY_PATH')},
        component_sha256=sha(components.encode()),snippet_sha256=sha(snippet.encode()),
        official_small_cases_per_form=sum(c[3]=='official-domain' for c in cases),wider_api_cases_per_form=sum(c[3]=='wider-api' for c in cases),
        checker_negative_controls=4,requested_child_soft_stack_bytes=stack,original_stack_limits=resource.getrlimit(resource.RLIMIT_STACK),
        scope='Local application evidence only; no online AC, known judge stack, universal stack sufficiency, formal template-problem status, full regression, or leak-detection claim. Large sanitizer RSS includes instrumentation. Prototype mode is non-publication evidence.',
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),forms={})
    def save():
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for form,source in programs.items():
            cpp = source if isinstance(source,Path) else out/(form+'.cpp')
            if not isinstance(source,Path):
                cpp.write_text(source)
            exe = out/form
            command = [str(compiler),*flags,str(cpp),'-o',str(exe)]
            subprocess.run(command,check=True)
            info = dict(command=command,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),small_cases=[],large_cases=[])
            report['forms'][form] = info
            for label,n,edges,domain,best in cases:
                report['active'] = [form,label]
                data = encode(n,edges)
                p = subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=60)
                info['small_cases'].append(dict(label=label,domain=domain,n=n,m=len(edges),expected=best,input_sha256=sha(data),output_sha256=sha(p.stdout),returncode=p.returncode,stderr=p.stderr.decode(errors='replace')))
                assert p.returncode == 0 and not p.stderr, (form,label,p.stderr)
                validate(n,edges,p.stdout,best)
            for label,n,edges,best in large_cases():
                report['active'] = [form,label]
                data = encode(n,edges)
                inp,output,stats = [out/(form+'-'+label+ext) for ext in ('.in','.out','.json')]
                inp.write_bytes(data)
                subprocess.run([sys.executable,str(Path(__file__).resolve()),'--measure-child',str(exe),str(inp),str(output),str(stats),str(stack)],check=True,env=env,timeout=200)
                result = json.loads(stats.read_text())
                result.update(label=label,n=n,m=len(edges),expected=best,input_sha256=sha(data),output_sha256=sha(output.read_bytes()))
                info['large_cases'].append(result)
                assert result['returncode'] == 0 and not result['stderr'], (form,label,result)
                validate(n,edges,output.read_bytes(),best,large=True)
                if form == 'direct' and label == 'path' and not san:
                    limited = out/'path-stack8.json'
                    subprocess.run([sys.executable,str(Path(__file__).resolve()),'--measure-child',str(exe),str(inp),str(out/'path-stack8.out'),str(limited),str(8<<20)],check=True,env=env,timeout=200)
                    report['eight_mib_resource_probe'] = json.loads(limited.read_text())
                    # Resource failure is evidence, not an algorithm pass. Compiler-dependent.
                    report['eight_mib_resource_probe']['historical_assessment_result'] = 'SIGSEGV at 8 MiB with g++ 14.2.0 -O2, n=400000 path'
                save()
        report['sources_after'] = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in tracked}
        report['compiler_binaries_after'] = {str(p):sha(p.read_bytes()) for p in (compiler,frontend)}
        assert bound == report['sources_after'], 'Bound inputs changed'
        assert compiler_hashes == report['compiler_binaries_after'], 'Compiler changed'
        assert tuple(report['original_stack_limits']) == resource.getrlimit(resource.RLIMIT_STACK), 'Parent stack limit changed'
        report['status'] = 'passed'
        report.pop('active',None)
    except BaseException:
        report['status'] = 'failed'
        report['error'] = traceback.format_exc()
        raise
    finally:
        report['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print(f'CF732F {mode}: {len(cases)} small cases and four maximum-size cases per {list(programs)} PASS; {report_path}')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--measure-child':
        measure_child()
    else:
        main()
