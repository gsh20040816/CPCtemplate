from pathlib import Path
import hashlib,json,sys,shutil,subprocess,os
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from run_provenance import snapshot
from usage_examples import records
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=snapshot(R);reports={}
for mode,name in [('normal','modular-knowledge-normal-ih4hskwy'),('sanitizer','modular-knowledge-sanitizer-k7dfni6j')]:
 p=R/'build'/name/'report.json';d=json.loads(p.read_text());assert d['passed'] and d['mode']==mode
 assert d['source_before_sha256']==d['source_after_sha256']==source
 assert H(d['compiler'])==d['compiler_sha256'] and H(d['frontend'])==d['frontend_sha256']
 assert d['compile_returncode']==d['run_returncode']==0
 for path,h in d['artifacts'].items():assert H(R/path)==h
 assert sum(d['counts'].values())==110904 and d['quotient_checks']==120600
 shutil.copyfile(p,R/f'verification/modular-knowledge-{mode}.json');reports[mode]=dict(path=str(p.relative_to(R)),sha256=H(p),counts=d['counts'],quotient_checks=d['quotient_checks'])
# Bind the separate broader Euler test rather than assigning that coverage to the new small-modulus probe.
compiler='/usr/bin/x86_64-linux-gnu-g++-14';frontend=subprocess.check_output([compiler,'-print-prog-name=cc1plus'],text=True).strip()
out=R/'build/modular-knowledge-regression';env=os.environ.copy();env.update(CPLUS_INCLUDE_PATH=str(R/'build/deps/boost-1.83/usr/include'),ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
euler=[];compiler_before=H(compiler);frontend_before=H(frontend);boost=R/'build/deps/libboost1.83-dev_1.83.0-4.2_amd64.deb';boost_sha=H(boost)
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=out/f'euler-{mode}';cmd=[compiler,'-std=c++20',*flags,'tests/euler_power.cpp','-o',str(exe)]
 for op,command in [('compile',cmd),('run',[str(exe)])]:
  p=subprocess.run(command,cwd=R,env=env,capture_output=True,text=True,timeout=180)
  stdout=out/f'{mode}-{op}.stdout';stderr=out/f'{mode}-{op}.stderr';stdout.write_text(p.stdout);stderr.write_text(p.stderr)
  assert p.returncode==0 and not p.stderr,(command,p.stderr)
  euler.append(dict(mode=mode,operation=op,command=command,returncode=p.returncode,stdout_sha256=H(stdout),stderr_sha256=H(stderr),binary_sha256=H(exe)))
assert compiler_before==H(compiler) and frontend_before==H(frontend) and boost_sha==H(boost)
proof=json.loads((R/'verification/usage-examples.json').read_text());rows=records();assert len(rows)==230
for row in rows:assert proof[row['id']]['program_sha256']==row['program_sha256'] and proof[row['id']]['modes']==['normal','sanitizer']
assert not subprocess.check_output(['git','diff','--','src/compact'],cwd=R)
visual=[]
for stem,pages in json.loads((R/'build/modular-knowledge-qa/pages.json').read_text()).items():
 p=R/f'output/pdf/{stem}.pdf'
 visual.append(dict(pdf=str(p.relative_to(R)),pdf_sha256=H(p),physical_pages_seen=pages,render_png_sha256={f'build/modular-knowledge-qa/{stem}-{n}.png':H(R/f'build/modular-knowledge-qa/{stem}-{n}.png') for n in pages},findings='Actual images inspected: three complete modular-condition pages, corrected Binomial inverse description, references and infrastructure links readable; no clipping or orphan heading; fonts unchanged.'))
(R/'verification/modular-knowledge-visual.json').write_text(json.dumps(dict(scope='Nine actual pages, targeted inspection only',pdfs=visual),indent=2)+'\n')
assert snapshot(R)==source
summary=dict(source_sha256=source,source_inputs=len(source),dedicated=reports,euler_regression=euler,compiler_sha256=compiler_before,frontend_sha256=frontend_before,boost_package_sha256=boost_sha,visual_sha256=H(R/'verification/modular-knowledge-visual.json'),unchanged_pdfs=json.loads((R/'build/modular-knowledge-pdf-restore.json').read_text()),scope='Knowledge migration plus targeted ordinary/ASan/UBSan actual-API tests. New probe Euler m<=40; separate existing euler_power.cpp checks selected full-width moduli, 65-bit reduced exponents and 200-digit exponents. No implementation changes, fresh full-suite run, new online AC, CI, or LeakSanitizer claim. All 230 usage program hashes unchanged, not newly executed in this batch.')
(R/'verification/modular-knowledge-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified migration/runtime/artifact bindings, separate broader Euler runs, unchanged usage hashes and nine rendered pages')
