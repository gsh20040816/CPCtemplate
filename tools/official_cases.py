#!/usr/bin/env python3
"""Run a current driver against generated, pinned Library Checker cases.

Generate first with upstream generate.py. Results are local evidence, not OJ AC.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import tomllib

root = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('checkout', type=Path)
ap.add_argument('problem')
ap.add_argument('driver', type=Path)
ap.add_argument('report', type=Path)
ap.add_argument('--sanitize', action='store_true')
ap.add_argument('--timeout', type=float, default=30)
args = ap.parse_args()
up = args.checkout.resolve()
matches = [p for p in up.rglob('info.toml') if p.parent.name == args.problem and p.relative_to(up).parts[0] != 'test']
assert len(matches) == 1, matches
folder = matches[0].parent
meta = tomllib.loads(matches[0].read_text())
commit = subprocess.check_output(['git','-C',str(up),'rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','-C',str(up),'diff','HEAD','--'],text=True), 'Modified tracked reference files'
work = root/'build/official-cases'/args.problem/('sanitized' if args.sanitize else 'normal')
work.mkdir(parents=True, exist_ok=True)
bundle = work/'main.cpp'
subprocess.run(['python3',str(root/'tools/bundle.py'),str(args.driver),str(bundle)],check=True)
cxx = os.environ.get('CXX') or shutil.which('g++-16') or 'g++'
flags = ['-std=c++20','-O2']
if args.sanitize: flags=['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
# Match contest recursion stack on macOS; DFS remains recursive.
if os.uname().sysname=='Darwin': flags += ['-Wl,-stack_size,0x20000000']
exe = work/'main'
subprocess.run([cxx,*flags,str(bundle),'-o',str(exe)],check=True)
checker = folder/'checker'
assert checker.is_file(), 'Run upstream generator first'
inputs=sorted((folder/'in').glob('*.in'))
assert len(inputs)==sum(t['number'] for t in meta['tests']), 'Incomplete generated test set'
expected_names={f"{Path(t['name']).stem}_{i:02d}.in" for t in meta['tests'] for i in range(t['number'])}
assert {p.name for p in inputs}==expected_names, 'Case names do not match metadata'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for inp in inputs:
    ans=folder/'out'/(inp.stem+'.out')
    assert ans.is_file()
    actual=work/(inp.stem+'.out')
    err=work/(inp.stem+'.err')
    start=time.monotonic()
    # Per-process resident bytes from macOS time; not cumulative child rusage.
    command=[str(exe)]
    if os.uname().sysname=='Darwin': command=['/usr/bin/time','-l',*command]
    with inp.open('rb') as fi, actual.open('wb') as fo, err.open('wb') as fe:
        subprocess.run(command,stdin=fi,stdout=fo,stderr=fe,check=True,timeout=args.timeout)
    elapsed=time.monotonic()-start
    stderr=err.read_text()
    assert not any(x in stderr for x in ['runtime error:', 'ERROR: AddressSanitizer', 'LeakSanitizer']), stderr
    check=subprocess.run([str(checker),str(inp),str(actual),str(ans)],capture_output=True,text=True,check=True,timeout=10)
    rss=re.search(r'(\d+)\s+maximum resident set size',stderr)
    rows.append(dict(case=inp.stem,input_sha256=sha(inp),answer_sha256=sha(ans),output_sha256=sha(actual),elapsed_seconds=round(elapsed,4),resident_bytes=int(rss[1]) if rss else None,checker_message=check.stderr.strip(),verdict='local_checker_accepted'))
# Verify the checker rejects a deliberately wrong answer, not just exits zero.
wrong=work/'negative-control.out';wrong.write_text('not-a-valid-answer\n')
first=inputs[0];ans=folder/'out'/(first.stem+'.out')
negative=subprocess.run([str(checker),str(first),str(wrong),str(ans)],capture_output=True,text=True,timeout=10)
assert negative.returncode in (1, 2), (negative.returncode,negative.stderr)
report=dict(problem=args.problem,scope='Local official generated tests only; not online AC or controlled OJ speed ranking',reference_commit=commit,reference_problem_path=str(folder.relative_to(up)),metadata_sha256=sha(matches[0]),checker_source_sha256=sha(folder/'checker.cpp'),checker_binary_sha256=sha(checker),driver=str(args.driver),bundle_sha256=sha(bundle),compiler=subprocess.check_output([cxx,'--version'],text=True).splitlines()[0],flags=flags,recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),negative_control='deliberately wrong output rejected',negative_control_exit_code=negative.returncode,negative_control_message=negative.stderr.strip(),cases=rows)
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'{args.problem}: {len(rows)} official local cases PASS; sanitizer={args.sanitize}; not online AC')
