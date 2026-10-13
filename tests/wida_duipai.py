"""Audit the WIDA checker notes without treating Windows tools as available."""
import hashlib, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compiler_config import CXX
root = Path(__file__).resolve().parents[1]
blob = Path('/tmp/wida-duipai.md').read_bytes()
fix = root / 'tests/fixtures/wida_duipai'
fix.mkdir(parents=True, exist_ok=True)
(fix / 'main.md').write_bytes(blob)
(fix / 'LICENSE').write_bytes((root / 'tests/fixtures/wida_decimal_hash/LICENSE').read_bytes())
assert hashlib.sha1(b'blob %d\0' % len(blob) + blob).hexdigest() == '632a72ec2ef746f054de87c894848f8474587237'
text = blob.decode().replace('\r\n', '\n')
assert 'exit(0);' in text and 'if errorlevel==1' in text and 'freopen("Ask.txt", "w", stdout);' in text
parts = text.split('```')
cpp, bat, gen, shen, juruo = (x.split('\n', 1)[1] for x in (parts[1], parts[3], parts[5], parts[7], parts[9]))
assert cpp.startswith('#include') and bat.startswith(':loop')
out = root / 'build/wida-duipai'
out.mkdir(parents=True, exist_ok=True)
(out / 'checker.cpp').write_text(cpp)
(out / 'gen.cpp').write_text(gen)
(out / 'shen.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + shen + '\nsigned main(){std::string s; std::cin>>s; std::cout<<s;}\n')
(out / 'juruo.cpp').write_text('#include <bits/stdc++.h>\nusing namespace std;\n' + juruo + '\nsigned main(){std::string s; std::cin>>s; std::cout<<s;}\n')
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
report = []
clk = subprocess.run([CXX, '-std=c++20', '-x', 'c++', '-E', '-dM', '-'], input='#include <ctime>\n', text=True, capture_output=True, check=True)
clocks = [line for line in clk.stdout.splitlines() if 'CLOCKS_PER_SEC' in line]
assert clocks and '1000000' in clocks[0]
exe = out / 'checker'
subprocess.run([CXX, '-std=c++20', '-O2', str(out / 'checker.cpp'), '-o', str(exe)], check=True)
proc = subprocess.Popen([str(exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=out)
try:
    out_raw, err_raw = proc.communicate(timeout=3)
    finished = True
except subprocess.TimeoutExpired:
    proc.kill()
    out_raw, err_raw = proc.communicate()
    finished = False
out_text = (out_raw or b'').decode('utf-8', 'replace')
err_text = (err_raw or b'').decode('utf-8', 'replace')
assert not finished
assert 'Juruo.exe: command not found' in err_text
assert 'Shenben.exe: command not found' in err_text
assert 'Ask.exe: command not found' in err_text
report.append(dict(checker='fc did not return within 3s; the three exe names were not found', clocks=clocks[0]))
bare = subprocess.run([CXX, '-std=c++20', str(out / 'gen.cpp'), '-o', str(out / 'gen-bare')], text=True, capture_output=True)
assert bare.returncode != 0 and 'wida.h' in bare.stderr
subprocess.run([CXX, '-std=c++20', '-DONLINE_JUDGE', '-O2', str(out / 'gen.cpp'), '-o', str(out / 'gen')], check=True)
ask = out / 'Ask.txt'
if ask.exists(): ask.unlink()
subprocess.run([str(out / 'gen')], cwd=out, check=True, timeout=15)
assert ask.read_text() == ''
for name in ('shen', 'juruo'):
    subprocess.run([CXX, '-std=c++20', '-O2', str(out / f'{name}.cpp'), '-o', str(out / name)], check=True)
ask.write_text('ping\n')
subprocess.run([str(out / 'shen')], cwd=out, check=True, timeout=15)
subprocess.run([str(out / 'juruo')], cwd=out, check=True, timeout=15)
assert (out / 'Shenben.out').read_text() == 'ping' and (out / 'Juruo.out').read_text() == 'ping'
report.append(dict(redirect='ping'))
print('PASS', clocks[0], flush=True)
import json
(root / 'verification/wida-duipai.json').write_text(json.dumps(dict(
    scope='The checker is a Windows loop. On this machine the three .exe names are missing and system("fc ...") does not return within 3 seconds, so the Wrong Answer path is not reached. CLOCKS_PER_SEC is 1000000 while the source labels the difference ms. A failing compare would call exit(0). The bat line if errorlevel==1 was not run. The sample program needs ONLINE_JUDGE or bits/wida.h. The two freopen snippets copy Ask.txt. No online AC.',
    blob='632a72ec2ef746f054de87c894848f8474587237', runs=report), indent=2) + '\n')
