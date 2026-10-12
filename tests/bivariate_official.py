"""Pinned Library Checker inputs and official answers; local verification only."""
from pathlib import Path
import hashlib
import base64
import json
import os
import subprocess
import time
import tomllib
import sys
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
out = root/'build/bivariate/official'
manifest = json.loads((root/'tests/fixtures/bivariate_official/sources.json').read_text())
for item in manifest['files']:
    dest = out/item['destination']
    if not dest.exists():
        response = json.loads(subprocess.check_output(['gh','api','repos/'+manifest['repository']+'/git/blobs/'+item['blob']],text=True))
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(base64.b64decode(response['content']))
    data = dest.read_bytes()
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == item['blob'], item['path']
info = tomllib.loads((out/'info.toml').read_text())
hashes = json.loads((out/'hash.json').read_text())
(out/'params.h').write_text('#pragma once\n#define NM_MAX 500000\n#define MOD 998244353\n')
report = dict(commit='1814c4e5205517e368bb57a8d1127eb961cfeaae', scope='Official generator/input and official reference-output hash verification, local runs of exact printed program in O2 and ASan/UBSan. Not an online verdict or SOTA timing.', cases=[], files={})
sys.path.insert(0,str(root/'tools'))
from usage_examples import records
row = next(r for r in records() if r['id']=='example-453')
assert (root/row['snippet_file']).read_text() == row['snippet']
(out/'printed.cpp').write_text(row['program'])
for name,src,flags in [('reference',out/'sol/correct.cpp',['-O2']),('normal',out/'printed.cpp',['-O2','-DNDEBUG']),('sanitizer',out/'printed.cpp',['-O1','-g','-fsanitize=address,undefined'])]:
    subprocess.run([CXX,'-std=c++20',*flags,str(src),'-o',str(out/name)],check=True)
env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
for item in info['tests']:
    name = Path(item['name']).stem
    if item['name'].endswith('.cpp'):
        subprocess.run([CXX,'-std=c++20','-O2','-I'+str(out),str(out/'gen'/item['name']),'-o',str(out/('gen-'+name))],check=True)
    for seed in range(item['number']):
        label = f'{name}_{seed:02d}'
        data = (out/'gen'/f'{label}.in').read_bytes() if item['name'].endswith('.in') else subprocess.check_output([str(out/('gen-'+name)),str(seed)])
        assert hashlib.sha256(data).hexdigest() == hashes[label+'.in'],label
        result = dict(label=label,dimensions=data.splitlines()[0].decode(),input_sha256=hashes[label+'.in'],runs=[])
        expected = None
        for mode in ['reference','normal','sanitizer']:
            start = time.monotonic()
            r = subprocess.run([str(out/mode)],input=data,capture_output=True,timeout=300,env=env)
            elapsed = time.monotonic()-start
            assert r.returncode == 0 and not r.stderr,(label,mode,r.returncode,r.stderr)
            if mode == 'reference':
                assert hashlib.sha256(r.stdout).hexdigest() == hashes[label+'.out'],label
                expected = r.stdout.split()
            else:
                assert r.stdout.split() == expected,(label,mode)
            result['runs'].append(dict(mode=mode,seconds=elapsed,output_sha256=hashlib.sha256(r.stdout).hexdigest()))
        report['cases'].append(result)
        print(label,result['dimensions'],result['runs'],flush=True)
        (root/'verification/bivariate-official-progress.json').write_text(json.dumps(report,indent=2)+'\n')
paths = list((out/'gen').glob('*'))+[out/'sol/correct.cpp',out/'task.md',out/'info.toml',out/'hash.json',out/'random.h',out/'params.h',root/'tests/bivariate_official.py']
report['files'] = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
report['program_sha256'] = row['program_sha256']
report['status'] = 'passed'
(root/'verification/bivariate-official.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'verification/bivariate-official-progress.json').unlink()
print('All',len(report['cases']),'official cases PASS',flush=True)
