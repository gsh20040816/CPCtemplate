#!/usr/bin/env python3
"""Signed rectangular Diophantine modeling; no new algorithm or OJ claim."""
import hashlib
import itertools
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
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from compiler_config import CXX


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bounds(z, step, low, high, mutant=''):
    if step == 0:
        return (None, None) if low <= z <= high else (1, 0)
    if step > 0 or mutant == 'negative-step':
        n, m, d = low - z, high - z, abs(step)
    else:
        n, m, d = z - high, z - low, -step
    if mutant == 'truncate':
        trunc = lambda v: (abs(v) // d) * (-1 if v < 0 else 1)
        return trunc(n), trunc(m)
    return -((-n) // d), m // d


def solve(a, b, c, particular, rect, mutant='', enumerate_points=True):
    lx, rx, ly, ry = rect
    if lx > rx or ly > ry:
        return set() if enumerate_points else 0
    if a == b == 0:
        if c:
            return set() if enumerate_points else 0
        return ({(x,y) for x in range(lx,rx+1) for y in range(ly,ry+1)}
                if enumerate_points else (rx-lx+1)*(ry-ly+1))
    g = math.gcd(a,b)
    if c % g:
        return set() if enumerate_points else 0
    x, y = particular
    dx, dy = b // g, -a // g
    intervals = [bounds(x,dx,lx,rx,mutant), bounds(y,dy,ly,ry,mutant)]
    lows = [l for l,r in intervals if l is not None]
    highs = [r for l,r in intervals if r is not None]
    low, high = max(lows), min(highs)
    if not enumerate_points:
        return max(0,high-low+1)
    return {(x+dx*t,y+dy*t) for t in range(low,high+1)}


def main():
    if not __debug__:
        raise RuntimeError('Reference checks require Python assertions')
    fixture = ROOT / 'tests/fixtures/diophantine-knowledge'
    manifest = json.loads((fixture/'manifest.json').read_text())
    original = (fixture/'original.tex').read_text()
    assert sha(original.encode()) == manifest['original_sha256']
    preserved = original
    for change in manifest['changes']:
        assert preserved.count(change['old']) == 1
        preserved = preserved.replace(change['old'],change['new'])
    source = (ROOT/'docs/knowledge-diophantine.tex').read_text()
    assert source.startswith(preserved)
    assert 'knowledge-diophantine-bounds' in source
    assert len(re.findall(r'^\\section\{', (ROOT/'docs/mathematics-legacy.tex').read_text(),re.M)) == 70
    before = snapshot(ROOT)
    mode = 'sanitizer' if os.environ.get('CPC_SANITIZE') == '1' else 'normal'
    out = Path(tempfile.mkdtemp(prefix='diophantine-knowledge-'+mode+'-',dir=ROOT/'build'))
    small = list(itertools.product(range(-3,4), repeat=3))
    edge = [-(1<<63), -(1<<63)+1, -1, 0, 1, (1<<63)-2, (1<<63)-1]
    rng = random.Random(20261003)
    equations = small + list(itertools.product(edge,repeat=3))
    equations += [tuple(rng.randrange(-(1<<63),1<<63) for _ in range(3)) for _ in range(2000)]
    data = ''.join(f'{a} {b} {c}\n' for a,b,c in equations).encode()
    (out/'equations.in').write_bytes(data)
    probe = (ROOT/'tests/diophantine_knowledge.cpp').read_text()
    components = {v['symbol']:v['code'] for v in extract_components(json.loads((ROOT/'docs/catalog.json').read_text()))}
    copied = '#include <algorithm>\n#include <iostream>\n#include <string>\nusing namespace std;\n'
    copied += components['extended_gcd']+'\n'+components['linear_equation']+'\n'
    copied += '\n'.join(probe.splitlines()[1:])
    flags = ['-std=c++20','-Wall','-Wextra'] + (['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env = os.environ.copy()
    if mode=='sanitizer':
        env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler = Path(shutil.which(CXX) or CXX).resolve()
    report = dict(mode=mode, source_before_sha256=before, compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,input_sha256=sha(data),programs=[],
                  rectangular_model_language='Python arbitrary-precision integers',
                  sanitizer_scope='Existing C++ linear_equation API probe and int128 output only; rectangle formulas and mutants execute in Python',
                  environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS')})
    for form, text in [('direct','#include "'+str(ROOT/'tests/diophantine_knowledge.cpp')+'"\n'),('copied',copied)]:
        cpp, exe = out/(form+'.cpp'),out/form
        cpp.write_text(text)
        subprocess.run([CXX,*flags,str(cpp),'-o',str(exe)],check=True,capture_output=True)
        run = subprocess.run([str(exe)],input=data,capture_output=True,env=env,timeout=30)
        assert run.returncode==0 and not run.stderr
        (out/(form+'.out')).write_bytes(run.stdout)
        answers = [tuple(map(int,line.split())) for line in run.stdout.splitlines()]
        assert len(answers)==len(equations)
        for (a,b,c),(ok,x,y) in zip(equations,answers):
            g=math.gcd(a,b);expected=(c==0 if g==0 else c%g==0)
            assert ok in (0,1) and bool(ok)==expected
            assert (a*x+b*y==c) if ok else (x==y==0)
        intervals = [(l,r) for l in range(-3,4) for r in range(l,4)] + [(1,0)]
        count = 0
        rejected = {'truncate':0,'negative-step':0}
        for (a,b,c),(_,x,y) in zip(small,answers):
            g=math.gcd(a,b)
            for (lx,rx),(ly,ry) in itertools.product(intervals,repeat=2):
                rect=(lx,rx,ly,ry)
                expected={(u,v) for u in range(lx,rx+1) for v in range(ly,ry+1) if a*u+b*v==c}
                observed=solve(a,b,c,(x,y),rect)
                assert observed==expected,(a,b,c,rect)
                assert solve(b,a,c,(y,x),(ly,ry,lx,rx))=={(v,u) for u,v in expected}
                assert solve(-a,-b,-c,(x,y),rect)==expected
                if g and c%g==0:
                    assert solve(a,b,c,(x+7*(b//g),y-7*(a//g)),rect)==expected
                for mutant in rejected:
                    if not rejected[mutant] and solve(a,b,c,(x,y),rect,mutant)!=expected:
                        rejected[mutant]+=1
                count+=1
        assert all(rejected.values())
        lo,hi=-(1<<63),(1<<63)-1
        huge=[(0,0,0,(0,0),(lo,hi,lo,hi),1<<128),
              (1,0,lo,(lo,0),(lo,hi,lo,hi),1<<64),
              (0,-1,lo,(0,-lo),(lo,hi,lo,hi),0),
              (1,-1,0,(0,0),(lo,hi,lo,hi),1<<64),
              (lo,0,lo,(1,0),(lo,hi,lo,hi),1<<64)]
        for a,b,c,part,rect,expected in huge:
            assert solve(a,b,c,part,rect,enumerate_points=False)==expected
        report['programs'].append(dict(form=form,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(run.stdout),equations=len(equations),rectangles=count,large_closed_forms=len(huge),rejected_mutants=rejected))
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Formula/model and existing API checks, not new algorithm, full suite, online AC or LeakSanitizer certification.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Diophantine knowledge {mode}: {count} complete rectangle sets per form PASS; {out.relative_to(ROOT)}/report.json')


if __name__=='__main__':
    main()
