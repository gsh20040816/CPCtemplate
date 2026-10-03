"""Enumerate paths and reflection bijections, then test actual binomial APIs."""
import argparse, hashlib, itertools, json, math, os, random, subprocess, sys, tempfile
from collections import Counter
from pathlib import Path
if not __debug__:
    raise RuntimeError('Run this test without Python optimization')
from compiler_config import CXX
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from run_provenance import snapshot


def choose(n, k):
    return 0 if n < 0 or k < 0 or k > n else math.comb(n, k)


def bounded(l, h, e):
    if h < 0 or e < 0 or abs(e - h) > l or (l + e - h) % 2: return 0
    k = (l + e - h) // 2
    return choose(l, k) - choose(l, k + h + 1)


def weak(p, q):
    return 0 if p < q else choose(p + q, q) - choose(p + q, q - 1)


def strict(p, q):
    if p + q == 0: return 1
    return 0 if p <= q else choose(p + q - 1, q) - choose(p + q - 1, q - 1)


def walk(steps, h):
    result = [h]
    for step in steps: result.append(result[-1] + step)
    return result


def reflect(steps, h, target):
    heights = walk(steps, h)
    t = heights.index(target)
    return tuple(-x for x in steps[:t]) + steps[t:]


def dynamic(l, h):
    current = {h: 1}
    for _ in range(l):
        nxt = Counter()
        for y, count in current.items():
            nxt[y + 1] += count
            if y: nxt[y - 1] += count
        current = nxt
    return current


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sanitizer', action='store_true'); args = ap.parse_args()
    san = args.sanitizer or os.environ.get('SANITIZE') == '1' or os.environ.get('CPC_SANITIZE') == '1'
    mode = 'sanitizer' if san else 'normal'; before = snapshot(ROOT)
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    text = (ROOT / 'docs/knowledge-ballot.tex').read_text()
    assert text.count(r'\label{knowledge-ballot-reflection}') == 1
    assert (ROOT / 'docs/mathematics.tex').read_text().count(r'\input{knowledge-ballot.tex}') == 1
    data = json.loads((ROOT / 'docs/knowledge-taxonomy.json').read_text())
    row = [r for r in data['entries'] if r['label'] == 'knowledge-ballot-reflection']
    assert len(row) == 1 and row[0]['path'] == 'math/combinatorics/catalan.md'
    for symbol in ['Binomial', 'Lucas', 'ExLucas']:
        assert r'\ref{compact-' + symbol + '}' in text and r'\pageref{compact-' + symbol + '}' in text
    counts = Counter(); api_cases = []; formula_checks = 0
    for l in range(13):
        sequences = list(itertools.product([-1, 1], repeat=l))
        wcounts = Counter(); scounts = Counter(); strict_images = {}
        for steps in sequences:
            heights = walk(steps, 0); q = steps.count(-1); p = l - q
            if min(heights) >= 0: wcounts[p,q] += 1
            if all(y > 0 for y in heights[1:]): scounts[p,q] += 1
            if min(heights) < 0 and p >= q:
                transformed = reflect(steps, 0, -1)
                assert transformed.count(-1) == q - 1
                assert reflect(transformed, 0, 1) == steps
                counts['weak_reflections'] += 1
            if l and all(y > 0 for y in heights[1:]):
                assert steps[0] == 1 and min(walk(steps[1:],0)) >= 0
                strict_images.setdefault(q, set()).add(steps[1:])
                counts['strict_first_step_bijections'] += 1
        if l:
            weak_tails = {}
            for tail in itertools.product([-1, 1], repeat=l-1):
                if min(walk(tail,0)) >= 0:
                    weak_tails.setdefault(tail.count(-1), set()).add(tail)
                    assert all(y > 0 for y in walk((1,) + tail,0)[1:])
            assert strict_images == weak_tails
        for q in range(l + 1):
            p = l - q
            assert weak(p,q) == wcounts[p,q] and strict(p,q) == scounts[p,q]
            api_cases += [(1,p,q,0,wcounts[p,q]), (2,p,q,0,scounts[p,q])]
            formula_checks += 2
        for h in range(5):
            good = Counter(); reflected = set(); targets = set()
            for steps in sequences:
                heights = walk(steps,h); e = heights[-1]
                counts['walks'] += 1
                if min(heights) >= 0: good[e] += 1
                elif e >= 0:
                    transformed = reflect(steps,h,-1)
                    assert walk(transformed,-h-2)[-1] == e
                    assert reflect(transformed,-h-2,-1) == steps
                    assert transformed not in reflected
                    reflected.add(transformed); counts['general_reflections'] += 1
                if walk(steps,-h-2)[-1] >= 0: targets.add(steps)
            assert reflected == targets
            assert good == dynamic(l,h)
            for e in range(h+l+3):
                assert bounded(l,h,e) == good[e]
                api_cases.append((0,l,h,e,good[e])); formula_checks += 1
    rng = random.Random(233)
    for _ in range(150):
        l = rng.randrange(13,151); h = rng.randrange(21); e = rng.randrange(h+l+4)
        value = dynamic(l,h).get(e,0)
        assert bounded(l,h,e) == value; formula_checks += 1
        api_cases.append((0,l,h,e,value))
    # Independent Catalan recurrence and unit-boundary examples.
    catalan = [1]
    for n in range(1,61): catalan.append(sum(catalan[i]*catalan[n-1-i] for i in range(n)))
    for n, value in enumerate(catalan):
        assert weak(n,n) == value and value == choose(2*n,n)//(n+1)
        api_cases.append((1,n,n,0,value)); formula_checks += 1
    assert bounded(4,2,0) == 3 and weak(3,2) == 5 and strict(3,2) == 2
    assert strict(0,0) == weak(0,0) == bounded(0,2,2) == 1
    assert bounded(0,2,0) == bounded(3,0,0) == bounded(2,0,4) == 0
    assert choose(4,2)%6//3 != catalan[2]%6
    # Wrong boundary shift, weak/strict conflation, and unsafe modular division controls.
    k = (4+0-2)//2
    assert choose(4,k)-choose(4,k+2) != bounded(4,2,0)
    assert weak(3,2) != strict(3,2)
    backends = [('F',1000003)] + [('L',p) for p in [2,3,5,7,11,97]] + [('E',m) for m in [1,4,6,8,9,12,25,60]]
    lines = []; answers = []; api_counts = Counter()
    for op,mod in backends:
        for kind,a,b,c,value in api_cases:
            lines.append(f'{op} {mod} {kind} {a} {b} {c}')
            answers.append(str(value%mod)); api_counts[op] += 1
    (ROOT/'build').mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='ballot-knowledge-'+mode+'-',dir=ROOT/'build'))
    inp = '\n'.join(lines)+'\n'; want = '\n'.join(answers)+'\n'
    (out/'input.txt').write_text(inp); (out/'expected.txt').write_text(want)
    compiler = Path(subprocess.check_output(['which',CXX],text=True).strip()).resolve()
    frontend = Path(subprocess.check_output([CXX,'-print-prog-name=cc1plus'],text=True).strip()).resolve()
    ch,fh = sha(compiler),sha(frontend)
    flags = ['-std=c++20'] + (['-O1','-g','-fsanitize=address,undefined'] if san else ['-O2'])
    exe = out/'probe'; cmd = [CXX,*flags,str(ROOT/'tests/ballot_knowledge_probe.cpp'),'-o',str(exe)]
    build = subprocess.run(cmd,text=True,capture_output=True)
    (out/'compile.stdout').write_text(build.stdout); (out/'compile.stderr').write_text(build.stderr)
    assert build.returncode == 0,build.stderr
    run = subprocess.run([str(exe)],input=inp,text=True,capture_output=True,timeout=180)
    (out/'actual.txt').write_text(run.stdout); (out/'stderr.txt').write_text(run.stderr)
    assert run.returncode == 0 and not run.stderr,run.stderr
    assert run.stdout.splitlines() == answers
    assert snapshot(ROOT) == before and sha(compiler) == ch and sha(frontend) == fh
    report = dict(mode=mode,passed=True,source_before_sha256=before,source_after_sha256=snapshot(ROOT),
                  counts=dict(counts),formula_checks=formula_checks,api_counts=dict(api_counts),
                  compiler=str(compiler),compiler_sha256=ch,frontend=str(frontend),frontend_sha256=fh,
                  compile_command=cmd,compile_returncode=build.returncode,run_returncode=run.returncode,
                  environment={k:os.environ.get(k) for k in ['CXX','ASAN_OPTIONS','UBSAN_OPTIONS']},
                  artifacts={str(p.relative_to(ROOT)):sha(p) for p in out.iterdir() if p.is_file()},
                  scope='Explicit short walks, invertible first-hit reflection, strict first-step reduction, independent DP and Catalan recurrence; actual existing Binomial/Lucas/ExLucas under stated domains. Knowledge only; no new algorithm/online AC/full-suite/LeakSanitizer claim.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Ballot knowledge {mode}: {dict(counts)}, {formula_checks} formula checks, {dict(api_counts)} API answers PASS; report {out.relative_to(ROOT)}/report.json',flush=True)

if __name__ == '__main__': main()
