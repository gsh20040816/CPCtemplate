from pathlib import Path
import json,hashlib,subprocess,sys,os,re,shutil
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from run_provenance import snapshot,baseline_archive,baseline_hashes
from usage_examples import records
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=snapshot(R);summaries={}
for mode,name in [('normal','hld-ordered-normal-j7133ki_'),('sanitizer','hld-ordered-sanitizer-r0dyf4vb')]:
 p=R/'build'/name/'report.json';d=json.loads(p.read_text());assert d['passed'] and d['mode']==mode
 assert d['source_before_sha256']==d['source_after_sha256']==source
 assert H(d['compiler'])==d['compiler_sha256'] and H(d['frontend'])==d['frontend_sha256']
 for a in [*d['core'].values(),*d['programs'].values()]:
  assert H(R/a['source'])==a['source_sha256'] and H(R/a['binary'])==a['binary_sha256']
 for c in d['commands']:
  for k in ['stdin','stdout','stderr','expected']:
   if k in c:assert H(R/c[k])==c[k+'_sha256']
  if 'expected' in c:assert (R/c['stdout']).read_text().split()==(R/c['expected']).read_text().split()
  assert c['returncode'] in [0,-6]
  if c['returncode']==-6:assert 'actual == expected' in (R/c['stderr']).read_text()
 assert sum(c['returncode']==-6 for c in d['commands'])==3 and d['affine_order_negative_control']
 assert all(v['official_inputs']==104 and v['extension_inputs']==10 and v['cases']==114 for v in d['programs'].values())
 assert d['environment']['ASAN_OPTIONS']=='detect_leaks=0:halt_on_error=1'
 shutil.copyfile(p,R/f'verification/hld-ordered-{mode}.json')
 summaries[mode]={'report_sha256':H(p),'core':[v['stdout'] for v in d['core'].values()],'programs':d['programs'],'stack':d['stack']}
base=R/'build/hld-ordered-copy-final-20261003';d=json.loads((base/'report.json').read_text())
assert d['input_sha256_before']==d['input_sha256_after'] and not d['changed_inputs'] and d['unresolved_count']==0 and d['registered_count']==231
assert H(d['compiler']['path'])==d['compiler']['sha256']
for p,h in d['input_sha256_before'].items():assert H(R/p)==h
for stage in d['stages']:
 for row in stage['results']:
  assert hashlib.sha256(row['program'].encode()).hexdigest()==row['program_sha256']==row['source_sha256_after']==H(base/row['source_file'])
  assert H(base/row['diagnostics_file'])==row['diagnostics_sha256']
shutil.copyfile(base/'report.json',R/'verification/hld-ordered-copy-context.json')
rows=records();proof=json.loads((R/'verification/usage-examples.json').read_text());assert len(rows)==len(proof)==231
for row in rows:assert proof[row['id']]['program_sha256']==row['program_sha256'] and proof[row['id']]['modes']==['normal','sanitizer']
# Current official source hashes match the existing pinned reference, without running external code.
up=next(x for x in json.loads((R/'docs/library-checker-inventory.json').read_text())['problems'] if x['id']=='vertex_set_path_composite')
for name,evidence in up['sources'].items():assert H(R/'build/ordered-hld-upstream'/name)==evidence['sha256']
# Recheck compatibility against the current copied code and pinned historic baseline.
stage=R/'build/hld-ordered-compat-stage';old=json.loads((stage/'provenance.json').read_text());baseline=baseline_hashes(baseline_archive(R));assert baseline==old['baseline_sha256']
for p,h in source.items():
 if p.startswith(('src/','tests/')):assert H(stage/p)==h
for p,h in baseline.items():assert H(stage/p)==h
compiler='/usr/bin/x86_64-linux-gnu-g++-14';compiler_sha=H(compiler);env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
compat=[]
for mode,flags in [('normal',['-O2']),('sanitizer',['-O1','-g','-fsanitize=address,undefined'])]:
 exe=stage/f'hld-final-{mode}';cmd=[compiler,'-std=c++20','-pthread',*flags,str(stage/'tests/hld.cpp'),'-o',str(exe)]
 for operation,command in [('compile',cmd),('run',[str(exe)])]:
  p=subprocess.run(command,cwd=R,env=env,text=True,capture_output=True,timeout=180);assert p.returncode==0 and not p.stderr,(command,p.stderr)
  output=stage/f'final-{mode}-{operation}.stdout';output.write_text(p.stdout)
  compat.append(dict(mode=mode,operation=operation,command=command,returncode=0,stdout_sha256=H(output),binary_sha256=H(exe)))
# Previously executed old usage drivers have unchanged current expanded sources.
old_usages={}
for mode in ['normal','sanitizer']:
 p=R/f'verification/mo-tree-usages-{mode}.json';report=json.loads(p.read_text());assert report['mode']==mode
 for name,program in report['programs'].items():
  fresh=R/f'build/hld-ordered-check-{name}-{mode}.cpp'
  subprocess.run(['python3','tools/bundle.py',program['driver'],str(fresh)],check=True)
  assert H(fresh)==program['bundle_sha256']==H(R/f'build/mo-tree-{mode}/{name}.cpp')
 old_usages[mode]=dict(report_sha256=H(p),counts=report['counts'],binaries={name:H(R/f'build/mo-tree-{mode}/{name}') for name in report['programs']})
# Verify all printed HLD ranges cover its full struct exactly once.
tex=(R/'docs/generated.tex').read_text();ranges=re.findall(r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,firstnumber=\d+)?\]\{\.\./src/compact/tree.hpp\}',tex)
lines=(R/'src/compact/tree.hpp').read_text().splitlines();start=lines.index('struct HLD');indices=[i for lo,hi in ranges for i in range(int(lo)-1,int(hi))];assert indices==list(range(start,len(lines)))
visual=[]
for stem,pages in json.loads((R/'build/hld-ordered-qa/pages.json').read_text()).items():
 pdf=R/f'output/pdf/{stem}.pdf';visual.append(dict(pdf=str(pdf.relative_to(R)),pdf_sha256=H(pdf),physical_pages_seen=pages,render_png_sha256={f'build/hld-ordered-qa/{stem}-{n}.png':H(R/f'build/hld-ordered-qa/{stem}-{n}.png') for n in pages},findings='Actual images inspected: full HLD across three numbered continuation pages, old P3384 usage, new two-page affine usage, graph-volume segtree dependency and infrastructure references; no clipping or orphan headings; unchanged font settings.'))
assert sum(len(v['physical_pages_seen']) for v in visual)==17
(R/'verification/hld-ordered-visual.json').write_text(json.dumps(dict(scope='17 targeted actual pages; not full-book visual certification',pdfs=visual),indent=2)+'\n')
assert snapshot(R)==source and H(compiler)==compiler_sha
summary=dict(source_sha256=source,source_inputs=len(source),dedicated=summaries,copy_context=[{k:s[k] for k in ['name','count','passed','failed']} for s in d['stages']],compatibility=compat,baseline_sha256=baseline,old_usage_regressions=old_usages,upstream_sources=up['sources'],printed_hld_ranges=ranges,visual_sha256=H(R/'verification/hld-ordered-visual.json'),pdf_preservation=json.loads((R/'build/hld-ordered-pdf-restore.json').read_text()),scope='Targeted final normal/ASan/UBSan and preserved old-interface checks; 225 standard plus 6 explicit GNU copied contexts. Selected canonical usages44/170/231 freshly executed, other228 program hashes current, not a fresh all231 runtime/full-suite run. Recursive stack limitations remain. No online AC, CI, or LeakSanitizer certification.')
(R/'verification/hld-ordered-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified final inputs, compiler/frontend, binaries, logs, 231 copied contexts, historic HLD compatibility, current old-driver bundles and 17 PDF pages')
