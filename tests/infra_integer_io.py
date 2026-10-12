#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
out = root / 'build/kuangbin-io'
out.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
tex = (root / 'docs/infra-integer-io.tex').read_text()
parts = []
for opt, path in re.findall(r'\\lstinputlisting\[([^]]*)\]\{\.\./([^}]+)\}', tex):
    if path.endswith('integer_io.cpp'):
        lines = (root / path).read_text().splitlines()
        first = int(re.search(r'firstline=(\d+)', opt)[1])
        last = re.search(r'lastline=(\d+)', opt)
        parts += lines[first-1:int(last[1]) if last else len(lines)]
printed = '#include <bits/stdc++.h>\nusing namespace std;\n' + '\n'.join(parts) + '\n'
(out / 'printed.cpp').write_text(printed)
core = printed[:printed.index('int main()')]
probe = core + '''int main()
{
    long long x = 1234567;
    bool ok = read_ll(x);
    printf("%d %lld\\n", int(ok), x);
}
'''
(out / 'probe.cpp').write_text(probe)
rng = random.Random(1480)
values = [0, 1, -1, -(1 << 63), (1 << 63)-1] + [rng.randrange(-(1 << 63), 1 << 63) for _ in range(10000)]
space = [' ', '\t', '\n', '\r', '\v', '\f', '\r\n']
tokens = []
for x in values:
    tokens.append(('-' if x < 0 else rng.choice(['', '+'])) + '0'*rng.randrange(5) + str(abs(x)))
data = '\t' + ''.join(s + rng.choice(space) for s in tokens) + '  \n\t'
expected = ''.join(str(x) + '\n' for x in values)
invalid = ['', ' ', '\n\t\r', '+', '-', 'x', '+x', '12x', '--1', '1-2', '9223372036854775808', '-9223372036854775809', '9'*100]
line_cases = [('', '0'), ('  ', '0'), ('\t', '0'), ('+0 -0 0002', '3 0 0 2')]
for text in invalid[3:]:
    line_cases.append((text, 'invalid'))
    line_cases.append(('1 ' + text, 'invalid'))
for _ in range(1000):
    a = [rng.choice(values) for _ in range(rng.randrange(20))]
    line_cases.append((' \t'.join(map(str, a)), ' '.join(map(str, [len(a), *a]))))
report = {}
for mode in ('normal', 'sanitizer'):
    flags = ['-std=c++20', '-O2', '-Wall', '-Wextra']
    if mode == 'sanitizer':
        flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    for name, src in [('header', root/'examples/infra/integer_io.cpp'), ('printed', out/'printed.cpp'), ('probe', out/'probe.cpp'), ('line', root/'examples/infra/line_integers.cpp')]:
        exe = out/(name+'-'+mode)
        subprocess.run([CXX, *flags, str(src), '-o', str(exe)], check=True)
        def run(text):
            p = subprocess.run([str(exe)], input=text, text=True, capture_output=True, env=env, timeout=10)
            assert p.returncode == 0, p.stderr
            return p.stdout
        if name in ('header', 'printed'):
            assert run(data) == expected
            for text, want in [('0','0\n'), ('-9223372036854775808','-9223372036854775808\n'), ('1 2  ', '1\n2\n'), (' \t\n', '')]:
                assert run(text) == want
        if name == 'probe':
            for text in invalid:
                assert run(text) == '0 1234567\n', repr(text)
            for x in values[:5]:
                assert run(str(x)) == f'1 {x}\n'
        if name == 'line':
            assert run('\n'.join(t for t,w in line_cases) + '\n') == ''.join(w+'\n' for t,w in line_cases)
            assert run('1 -2') == '2 1 -2\n'
            assert run('9223372036854775808') == 'invalid\n'
        report[name+'-'+mode] = 'pass'
# Exact functional source code (Unicode minus normalized); inject test driver only.
original = '''#include <cstdio>
template <class T>
inline bool scan_d(T &ret) {
 char c; int sgn;
 if(c=getchar(),c==EOF) return 0;
 while(c!='-'&&(c<'0'||c>'9')) c=getchar();
 sgn=(c=='-')?-1:1;
 ret=(c=='-')?0:(c-'0');
 while(c=getchar(),c>='0'&&c<='9') ret=ret*10+(c-'0');
 ret*=sgn;
 return 1;
}
inline void out(int x) {
 if(x>9) out(x/10);
 putchar(x%10+'0');
}
int main(int argc,char **argv) {
 if(argc>1) {out(-12);return 0;}
 long long x=7;
 if(scan_d(x)) printf("%lld\\n",x);
}
'''
(out/'original.cpp').write_text(original)
exe=out/'original'
subprocess.run([CXX,'-std=c++20','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(out/'original.cpp'),'-o',str(exe)],check=True)
assert subprocess.check_output([str(exe)],input='-123\n',text=True)=='-123\n'
try:
    subprocess.run([str(exe)],input='  \n',text=True,capture_output=True,timeout=0.5)
except subprocess.TimeoutExpired:
    report['source_trailing_whitespace']='timeout reproduced'
else:
    raise AssertionError('source EOF loop was not detected')
p=subprocess.run([str(exe)],input='-9223372036854775808\n',text=True,capture_output=True,env=env)
assert p.returncode != 0 and 'overflow' in p.stderr
report['source_min_negative']=p.stderr.strip()
p=subprocess.run([str(exe),'output'],capture_output=True,text=True,check=True)
assert p.stdout != '-12'
report['source_negative_output']=repr(p.stdout)
# 8.3 token loop, fed a bounded known string instead of removed gets.
parser = r'''#include <cstdio>
#include <cstring>
int main() {
 char buf[100];
 if(!fgets(buf,sizeof(buf),stdin)) return 0;
 int v;
 char *p=strtok(buf," ");
 while(p) {
  sscanf(p,"%d",&v);
  printf("%d\n",v);
  p=strtok(NULL," ");
 }
}
'''
(out/'source-line.cpp').write_text(parser)
line_exe=out/'source-line'
subprocess.run([CXX,'-std=c++20','-O2',str(out/'source-line.cpp'),'-o',str(line_exe)],check=True)
for text,expected_source in [('1 x 2','1\n1\n2\n'),('1\t2 3','1\n3\n')]:
    got=subprocess.check_output([str(line_exe)],input=text,text=True)
    assert got==expected_source
report['source_line_parser']='Ignored sscanf failure reuses 1; space-only strtok loses tab-separated 2, reproduced with bounded input'
paths=['examples/infra/integer_io.cpp','examples/infra/line_integers.cpp','docs/infra-integer-io.tex','tests/infra_integer_io.py']
result=dict(status='pass',results=report,integer_values=len(values),line_cases=len(line_cases),invalid_tokens=len(invalid),hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},printed_sha256=hashlib.sha256(printed.encode()).hexdigest(),scope='Local source audit and actual printed signed64 IO; no OJ or fastest-runtime claim')
(root/'verification/infra-integer-io.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
