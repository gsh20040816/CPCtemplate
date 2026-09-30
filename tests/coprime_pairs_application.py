"""P2522 full input: direct rectangle oracle and independent totient-square identity."""
from compiler_config import CXX
from pathlib import Path
import argparse,hashlib,json,math,os,random,subprocess,sys,time
parser=argparse.ArgumentParser()
parser.add_argument("--usage", action="store_true")
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
rng=random.Random(2522)
def brute(a,b,c,d,k):
    return sum(math.gcd(x,y)==k for x in range(a,b+1) for y in range(c,d+1))
cases=[]
for _ in range(500):
    a,b=sorted(rng.choices(range(1,61),k=2))
    c,d=sorted(rng.choices(range(1,61),k=2))
    k=rng.randrange(1,70)
    cases.append(((a,b,c,d,k),brute(a,b,c,d,k)))
phi=list(range(50001))
for p in range(2,50001):
    if phi[p]==p:
        for j in range(p,50001,p): phi[j]-=phi[j]//p
prefix=[0]*50001
for i in range(1,50001): prefix[i]=prefix[i-1]+phi[i]
fixtures=[((1,50000,1,50000,k),2*prefix[50000//k]-1) for k in (1,2,3,49999,50000)]
for q in [(49999,50000,1,50000,1),(1,1,1,50000,1),(40000,50000,40000,50000,50000)]:
    if q[-1]==50000: fixtures.append((q,1))
    else: fixtures.append((q,brute(*q)))
while len(cases)<50000: cases.append(fixtures[len(cases)%len(fixtures)])
data=str(len(cases))+'\n'+''.join(' '.join(map(str,q))+'\n' for q,ans in cases)
expected=[str(ans) for q,ans in cases]
if args.usage:
    sys.path.insert(0, str(root / 'tools'))
    from usage_examples import records
    row = next(r for r in records() if r['id'] == 'example-195')
    bundle = root / 'build/coprime-pairs-usage.cpp'
    bundle.write_text(row['program'])
    modes = ['normal', 'sanitizer']
else:
    bundle = root / 'build/P2522.compact.cpp'
    subprocess.run(['python3', 'tools/bundle.py', 'verify/luogu/P2522.compact.cpp', str(bundle)], cwd=root, check=True)
    modes = ['sanitizer' if os.environ.get('SANITIZE') == '1' else 'normal']
for mode in modes:
    exe = root / ('build/coprime-pairs-' + mode)
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run([os.environ.get('CXX', CXX), '-std=c++20', *flags, str(bundle), '-o', str(exe)], check=True)
    start = time.monotonic()
    result = subprocess.run([str(exe)], input=data, text=True, capture_output=True, check=True, timeout=30)
    seconds = time.monotonic() - start
    assert result.stdout.splitlines() == expected
    assert not result.stderr, result.stderr
    report = dict(usage='example-195' if args.usage else None, mode=mode,
                  program_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  queries=len(cases), invocations=1, seconds=round(seconds,4), flags=flags,
                  stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),
                  input_sha256=hashlib.sha256(data.encode()).hexdigest(), online_ac=False,
                  oracle='500 brute gcd rectangles; independent totient square counts; scaled k and boundary strips repeated to 50000 queries')
    (root / ('verification/coprime-pairs-usage-' + mode + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(f'P2522 {mode}: 50000 queries, independent rectangle and totient oracles PASS')
