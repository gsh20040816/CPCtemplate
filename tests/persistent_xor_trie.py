#!/usr/bin/env python3
"""Independent single-key enumeration, copies, bit boundaries and closed forms."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_provenance import snapshot
from audit_copy_context import extract_components
from compiler_config import CXX

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    if not __debug__:raise RuntimeError('Python checks must stay enabled')
    mode='sanitizer' if os.environ.get('CPC_SANITIZE')=='1' else 'normal'
    out=Path(tempfile.mkdtemp(prefix='persistent-xor-'+mode+'-',dir=ROOT/'build'))
    before=snapshot(ROOT)
    probe=(ROOT/'tests/persistent_xor_trie_probe.cpp').read_text()
    core=next(x['code'] for x in extract_components(json.loads((ROOT/'docs/catalog.json').read_text())) if x['symbol']=='PersistentXorTrie')
    prelude=''.join('#include <'+x+'>\n' for x in ['algorithm','cassert','climits','cstdint','iostream','optional','random','stdexcept','vector'])+'using namespace std;\n'
    copied=prelude+core+'\n'+probe.replace('#include "../src/compact/persistent_xor_trie.hpp"','')
    flags=['-std=c++20','-Wall','-Wextra']+(['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer'] if mode=='sanitizer' else ['-O2'])
    env=os.environ.copy()
    if mode=='sanitizer':env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    compiler=Path(shutil.which(CXX) or CXX).resolve()
    report=dict(mode=mode,source_before_sha256=before,compiler=str(compiler),compiler_sha256=sha(compiler.read_bytes()),flags=flags,programs=[])
    for form,source in [('header','#include "'+str(ROOT/'tests/persistent_xor_trie_probe.cpp')+'"\n'),('copied',copied)]:
        for nd in [False,True]:
            name=form+('-ndebug' if nd else '-assert');cpp=out/(name+'.cpp');exe=out/name;cpp.write_text(source)
            cmd=[CXX,*flags,*(['-DNDEBUG'] if nd else []),str(cpp),'-o',str(exe)]
            subprocess.run(cmd,capture_output=True,check=True)
            p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=600)
            assert p.returncode==0 and not p.stderr,(name,p.returncode,p.stderr[-1000:])
            lines=p.stdout.decode().splitlines();assert len(lines)==3 and lines[-1].startswith('PASS '),lines
            for i in range(2):assert list(map(int,lines[i].split()[1:]))[2:]==[15000026,600002]
            (out/(name+'.out')).write_bytes(p.stdout)
            report['programs'].append(dict(name=name,compile_command=cmd,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),output_sha256=sha(p.stdout),result=lines))
    report['mutants']=[]
    for name,old,new in [('minimum-not-maximum','int k = (x >> d & 1) ^ 1;','int k = x >> d & 1;'),('ignore-left-prefix','int a = root[l], b = root[r];','int a = root[0], b = root[r];'),('drop-query-x','return x ^ y;','return y;'),('truncate-result','return x ^ y;','return uint32_t(x ^ y);'),('collapse-multiplicity','t[p].cnt++;','t[p].cnt = 1;')]:
        assert old in copied,name
        text=copied.replace(old,new)
        cpp,exe=out/(name+'.cpp'),out/name;cpp.write_text(text)
        cmd=[CXX,*flags,'-DNDEBUG',str(cpp),'-o',str(exe)]
        subprocess.run(cmd,check=True,capture_output=True)
        p=subprocess.run([str(exe)],capture_output=True,env=env,timeout=180)
        assert p.returncode==0 and not p.stderr and p.stdout==b'ORACLE_REJECT\n',(name,p.returncode,p.stdout,p.stderr[-1000:])
        (out/(name+'.out')).write_bytes(p.stdout)
        report['mutants'].append(dict(name=name,source_sha256=sha(cpp.read_bytes()),binary_sha256=sha(exe.read_bytes()),compile_command=cmd,output_sha256=sha(p.stdout),independent_oracle_rejected=True))
    report.update(source_after_sha256=snapshot(ROOT),passed=True,scope='Prefix-only single-key XOR; copied/assert/NDEBUG forms, independent enumeration and two maximum-capacity closed forms. Not an OJ timing, full-suite or leak check.')
    assert before==report['source_after_sha256']
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Persistent XOR trie',mode,'PASS:',out/'report.json')
if __name__=='__main__':main()
