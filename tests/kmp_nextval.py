#!/usr/bin/env python3
"""Optimized failure table independently enumerates borders, never trusts KMP."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from usage_examples import records
from audit_copy_context import candidate, extract_components


def table(t):
    v = [-1] * (len(t) + 1)
    for i in range(1, len(t) + 1):
        for j in range(i - 1, -1, -1):
            if t[:j] == t[i - j:i] and (i == len(t) or t[j] != t[i]):
                v[i] = j
                break
    return v


def oracle(s, t):
    return table(t), [i for i in range(len(s) - len(t) + 1) if s[i:i + len(t)] == t]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sanitize', action='store_true')
    args = ap.parse_args()
    mode = 'sanitizer' if args.sanitize else 'normal'
    out = ROOT / 'build/kmp-nextval' / mode
    out.mkdir(parents=True, exist_ok=True)
    row = next(r for r in records() if r['id'] == 'example-344')
    sha = lambda x: hashlib.sha256(x).hexdigest()
    paths = ['src/compact/string.hpp', row['driver'], 'tests/kmp_nextval.py',
             'tests/fixtures/kmp_nextval_sources/kuangbin.cpp', 'docs/catalog.json',
             'docs/usage-examples.json', 'tools/usage_examples.py', 'tools/audit_copy_context.py']
    snapshot = {p: sha((ROOT / p).read_bytes()) for p in paths}
    texts = [bytes(x) for n in range(8) for x in itertools.product((1, 255), repeat=n)]
    patterns = [bytes(x) for n in range(1, 6) for x in itertools.product((1, 2, 255), repeat=n)]
    # Tables computed once per pattern; reference scans every candidate text window.
    refs = {t: table(t) for t in patterns}
    cases = [(s, t, refs[t], [i for i in range(len(s)-len(t)+1) if s[i:i+len(t)] == t]) for s in texts for t in patterns]
    rng = random.Random(20261009)
    for _ in range(300):
        s = bytes(rng.randrange(1, 256) for _ in range(rng.randrange(100)))
        t = bytes(rng.randrange(1, 256) for _ in range(rng.randrange(1, 50)))
        v, positions = oracle(s, t)
        cases.append((s, t, v, positions))
    for n, m in [(200000, 10009), (10009, 10009), (0, 10009)]:
        cases.append((b'a'*n, b'a'*m, [-1]*m+[m-1], list(range(n-m+1))))
    extension = []
    for n in range(1, 9):
        for x in itertools.product((0, 255), repeat=n):
            t = bytes(x)
            s = t + t
            v, positions = oracle(s, t)
            extension.append((s, t, v, positions))
    for _ in range(300):
        s = bytes(rng.randrange(256) for _ in range(rng.randrange(150)))
        t = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 60)))
        v, positions = oracle(s, t)
        extension.append((s, t, v, positions))
    n, m = 1000000, 500000
    extension.append((bytes(n), bytes(m), [-1]*m+[m-1], list(range(n-m+1))))
    # A long last-character mismatch traverses many ordinary borders but one optimized link.
    t = b'a'*(m-1)+b'b'
    extension.append((b'a'*n, t, [-1]*(m-1)+[m-2, 0], []))
    flags = ['-std=c++20', '-O1' if args.sanitize else '-O2']
    if args.sanitize:
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    env = {**os.environ, 'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1', 'UBSAN_OPTIONS':'halt_on_error=1'}
    def compile(src, exe, extra=()):
        p = subprocess.run([CXX, *flags, *extra, str(src), '-o', str(exe)], text=True, capture_output=True)
        assert p.returncode == 0, p.stderr
    def check(exe, batch, source=False):
        data = ''.join(f'{len(s)} {len(t)}\n'+ ' '.join(map(str,s))+'\n'+' '.join(map(str,t))+'\n' for s,t,_,_ in batch)
        p = subprocess.run([str(exe)], input=data, text=True, capture_output=True, timeout=180, env=env)
        assert p.returncode == 0, p.stderr
        lines = p.stdout.splitlines()
        stride = 2 if source else 3
        assert len(lines) == stride*len(batch), (exe,len(lines),len(batch))
        for k, (_,t,v,positions) in enumerate(batch):
            assert list(map(int,lines[stride*k].split())) == v, (exe,'table',t[:50])
            assert int(lines[stride*k+1]) == len(positions), (exe,'count',t[:50])
            if not source:
                assert list(map(int,lines[stride*k+2].split())) == positions, (exe,'positions',t[:50])
    components = {r['symbol']: r for r in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    programs = []
    for form in ('source', 'header', 'ndebug', 'expanded', 'copied'):
        exe = out/form
        src = ROOT/row['driver']
        if form == 'source':
            src = exe.with_suffix('.cpp')
            fixture = ROOT/'tests/fixtures/kmp_nextval_sources/kuangbin.cpp'
            src.write_text('#include <bits/stdc++.h>\nusing namespace std;\nnamespace original {\n#include "'+str(fixture)+'"\n}\n'+r'''
int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<char> s(n + 1), t(m + 1);
        for (int i = 0; i < n; i++)
        {
            int x;
            cin >> x;
            s[i] = x;
        }
        for (int i = 0; i < m; i++)
        {
            int x;
            cin >> x;
            t[i] = x;
        }
        vector<int> v(m + 1);
        original::preKMP(t.data(), m, v.data());
        for (int x : v)
            cout << x << ' ';
        cout << '\n';
        cout << original::KMP_Count(t.data(), m, s.data(), n) << '\n';
    }
    return 0;
}
''')
        elif form in ('expanded', 'copied'):
            src = exe.with_suffix('.cpp')
            src.write_text(row['program'] if form=='expanded' else candidate(row,row['requires'],components)['program'])
        compile(src,exe,['-DNDEBUG'] if form=='ndebug' else [])
        check(exe,[],form=='source')
        check(exe,cases,form=='source')
        if form!='source':
            check(exe,extension)
        programs.append(dict(form=form,source_cases=len(cases),extension_cases=0 if form=='source' else len(extension),source_sha256=sha(src.read_bytes())))
        print(mode,form,'PASS',flush=True)
    mutants=[]
    if not args.sanitize:
        for name,old,new,batch in [
            ('ordinary-not-optimized','t[i] == t[j] ? nextval[j] : j','j',cases[:363]),
            ('lost-overlap','nextval[m] = p[m - 1];','nextval[m] = -1;',cases[:363]),
            ('zero-tail-collision','nextval[m] = p[m - 1];','nextval[m] = t[m - 1] == 0 ? -1 : p[m - 1];',extension[:510]),
            ('wrong-start','i - m + 1','i - m',cases[:2000])]:
            assert old in row['program']
            src=out/(name+'.cpp');src.write_text(row['program'].replace(old,new));exe=out/name;compile(src,exe)
            try:
                check(exe,batch)
            except AssertionError:
                mutants.append(dict(name=name,detected=True))
            else:
                raise AssertionError('surviving mutant '+name)
    assert all(sha((ROOT/p).read_bytes())==v for p,v in snapshot.items())
    report=dict(mode=mode,source_cases=len(cases),extension_cases=len(extension),programs=programs,mutants=mutants,snapshot=snapshot,usage=row['id'],program_sha256=row['program_sha256'],scope='All optimized table entries and overlapping positions checked against enumerated borders/window equality. Original47-line fragment preKMP and KMP_Count in namespace; source domain nonzero bytes,m<=10009. New zero bytes and million-text/500000-pattern extensions separate. No online AC.')
    (ROOT/f'verification/kmp-nextval-{mode}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(mode,len(cases),len(extension),'PASS',flush=True)


if __name__=='__main__':
    main()
