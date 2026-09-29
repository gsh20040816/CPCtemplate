#!/usr/bin/env python3
"""Reproduce NERC 2024 K's 117 test recipes from the official public archive.

The generator's unused final out-of-bounds read is removed explicitly. Expected
outputs are cross-checked using two archive solutions marked accepted, then the
unmodified official checker tests both current-driver builds. This is local evidence.
"""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import shlex
import subprocess
import xml.etree.ElementTree as ET

ap=argparse.ArgumentParser()
ap.add_argument('archive',type=Path)
a=ap.parse_args()
root=Path(__file__).resolve().parents[1]
base=root/'build/knowns-official'
base.mkdir(parents=True,exist_ok=True)
prefix='problems/knowns-and-unknowns/'
refs=['solutions/295961327_ksun48_ok.cpp','solutions/295429966__LeMur__ok.cpp']
files=['problem.xml','files/gen_random.cpp','files/testlib.h','files/validate.cpp','check.cpp','tests/01','tests/02',*refs]
source_hashes={}
sha=lambda b:hashlib.sha256(b).hexdigest()
with ZipFile(a.archive) as z:
    for name in files:
        raw=z.read(prefix+name);source_hashes[name]=sha(raw)
        dest=base/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
gen=(base/'files/gen_random.cpp').read_text()
old='for (int i = 0; i <= count; i++) {'
new='for (int i = 0; i < count; i++) {'
assert gen.count(old)==1
(base/'files/gen_random.checked.cpp').write_text(gen.replace(old,new))
cxx=os.environ.get('CXX','g++')
for src,exe in [('files/gen_random.checked.cpp','gen'),('files/validate.cpp','validate'),('check.cpp','checker'),(refs[0],'ref0'),(refs[1],'ref1')]:
    subprocess.run([cxx,'-std=c++20','-O2','-include','cassert','-I',str(base/'files'),str(base/src),'-o',str(base/exe)],check=True)
subprocess.run(['python3',str(root/'tools/bundle.py'),str(root/'verify/qoj/10424.compact.cpp'),str(base/'driver.cpp')],check=True)
flags={'normal':['-std=c++20','-O2'],'sanitizer':['-std=c++20','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']}
for mode,opts in flags.items():
    subprocess.run([cxx,*opts,str(base/'driver.cpp'),'-o',str(base/mode)],check=True)
xml=ET.parse(base/'problem.xml')
tests=xml.findall('./judging/testset/tests/test')
assert len(tests)==117
rows=[]
for i,t in enumerate(tests,1):
    path=base/f'tests/{i:02d}'
    command=None
    if t.get('method')=='generated':
        command=shlex.split(t.attrib['cmd'])
        assert command[0]=='gen_random'
        p=subprocess.run([str(base/'gen'),*command[1:]],capture_output=True,check=True,timeout=60)
        assert not p.stderr,p.stderr
        path.write_bytes(p.stdout)
    raw_data=path.read_bytes()
    data=raw_data.replace(b'\r\n',b'\n')
    path.write_bytes(data)
    valid=subprocess.run([str(base/'validate')],input=data,capture_output=True,timeout=60)
    assert valid.returncode==0,(i,valid.stderr)
    answers=[]
    for ref in ['ref0','ref1']:
        p=subprocess.run([str(base/ref)],input=data,capture_output=True,check=True,timeout=60)
        assert not p.stderr,(i,ref,p.stderr)
        answers.append(p.stdout)
    assert answers[0].split()==answers[1].split(),(i,'archive accepted references disagree')
    answer=path.with_suffix('.a');answer.write_bytes(answers[0])
    for mode in flags:
        p=subprocess.run([str(base/mode)],input=data,capture_output=True,check=True,timeout=60)
        assert not p.stderr,(i,mode,p.stderr)
        out=path.with_suffix('.'+mode);out.write_bytes(p.stdout)
        verdict=subprocess.run([str(base/'checker'),str(path),str(out),str(answer)],capture_output=True,timeout=60)
        assert verdict.returncode==0,(i,mode,verdict.stderr)
    rows.append(dict(test=i,recipe=command,raw_input_sha256=sha(raw_data),input_sha256=sha(data),newline_normalized=raw_data!=data,answer_sha256=sha(answers[0]),modes=['normal','sanitizer'],verdict='official_checker_accepted_locally'))
    if i%20==0:print(f'{i}/117 official recipes validated and checked in both modes',flush=True)
wrong=base/'wrong.out';wrong.write_text('invalid-output\n')
v=subprocess.run([str(base/'checker'),str(base/'tests/01'),str(wrong),str(base/'tests/01.a')],capture_output=True,timeout=30)
assert v.returncode!=0
report=dict(scope='117 NERC 2024 K official recipes regenerated locally, not downloaded original judge data. Two archive accepted references agree; official checker accepts current driver in both modes. No online AC or ranking.',recorded_at_utc=datetime.now(timezone.utc).isoformat(),archive_url='https://neerc.ifmo.ru/archive/2024/nef-2024-archive.zip',archive_sha256=sha(a.archive.read_bytes()),upstream_sources=source_hashes,generator_patch=dict(old=old,new=new,reason='random_partition used i<=count and read a[count+1] beyond vector size count+1; final written element is immediately popped. Omit only that unused last iteration; no extra RNG calls or seed added.',patched_source_sha256=sha((base/'files/gen_random.checked.cpp').read_bytes())),compiler=subprocess.check_output([cxx,'--version'],text=True).splitlines()[0],driver='verify/qoj/10424.compact.cpp',bundled_source_sha256=sha((base/'driver.cpp').read_bytes()),flags=flags,negative_control=dict(verdict='rejected',returncode=v.returncode),tests=rows)
(root/'verification/knowns-official.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 117 official recipes, 234 local official-checker acceptances, two accepted-reference outputs agree, wrong-output control rejected',flush=True)
