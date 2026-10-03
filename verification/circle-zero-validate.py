from pathlib import Path
import json,hashlib,sys,subprocess,os,re,shutil
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from run_provenance import snapshot
from usage_examples import records
from aoj_cases import compare
from decimal import Decimal
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=snapshot(R); summaries={}
for mode,path in [('normal','build/circle-zero-normal-do9fq7_9/report.json'),('sanitizer','build/circle-zero-sanitizer-ccb90oz8/report.json')]:
 p=R/path;d=json.loads(p.read_text());assert d['passed'] and d['mode']==mode
 assert d['source_before_sha256']==d['source_after_sha256']==source
 assert H(d['compiler'])==d['compiler_sha256'] and H(d['frontend'])==d['frontend_sha256']
 for ctx in [*d['core_artifacts'].values(),*d['complete_programs'].values()]:
  assert H(R/ctx['source'])==ctx['source_sha256'] and H(R/ctx['binary'])==ctx['binary_sha256']
 for c in d['commands']:
  for k in ['stdout','stderr']:assert H(R/c[k])==c[k+'_sha256']
  if 'stdin' in c:assert H(R/c['stdin'])==c['input_sha256']
  assert c['returncode'] in [0,1,-6]
  if c['returncode']==-6:assert (R/c['stdin']).read_text().split()[1]=='-1'
  if c['returncode']==1:
   assert any(x in c['command'] for x in ['-ffast-math','-mlong-double-64']) or c['command'][0].endswith('-rounding')
 assert d['numeric_negative_controls']==10
 shutil.copyfile(p,R/f'verification/circle-zero-{mode}.json')
 summaries[mode]={'report_sha256':H(p),'line_cases':d['line_cases'],'circle_cases':d['circle_cases'],'max_core_error':d['core_max_absolute_error'],'programs':d['complete_programs'],'platform':d['platform']}
copybase=R/'build/circle-zero-copy-20261003';c=json.loads((copybase/'report.json').read_text())
assert c['input_sha256_before']==c['input_sha256_after'] and not c['changed_inputs']
for path,h in c['input_sha256_before'].items():assert H(R/path)==h
assert c['registered_count']==230 and c['unresolved_count']==0 and c['exit_status']==0
assert H(c['compiler']['path'])==c['compiler']['sha256']
for stage in c['stages']:
 for row in stage['results']:
  assert hashlib.sha256(row['program'].encode()).hexdigest()==row['program_sha256']==row['source_sha256_after']==H(copybase/row['source_file'])
  assert H(copybase/row['diagnostics_file'])==row['diagnostics_sha256']
shutil.copyfile(copybase/'report.json',R/'verification/circle-zero-copy-context.json')
rows={r['id']:r for r in records()};proof=json.loads((R/'verification/usage-examples.json').read_text());assert len(rows)==len(proof)==230
for k,r in rows.items():assert proof[k]['program_sha256']==r['program_sha256'] and proof[k]['modes']==['normal','sanitizer']
public=[];env=os.environ.copy();env.update(ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
for usage,letter,count in [('example-229','D',12),('example-230','E',25)]:
 for mode in ['normal','sanitizer']:
  p=R/f'verification/circle-zero-aoj-{usage[8:]}-{mode}.json';d=json.loads(p.read_text());cache=R/f'build/aoj-data/CGL_7_{letter}'
  assert d['program_sha256']==rows[usage]['program_sha256']
  assert d['test_sha256']==H(R/'tools/aoj_cases.py') and H(cache/'header.json')==d['header_sha256']
  exe=R/f'build/aoj-{usage}-{mode}';assert H(exe.with_suffix('.cpp'))==d['program_sha256']
  assert len(d['cases'])==count
  for case in d['cases']:
   serial=case['serial'];inp=cache/f'{serial}.in';ans=cache/f'{serial}.out'
   assert H(inp)==case['input_sha256'] and H(ans)==case['expected_sha256'] and case['verdict']=='local_comparator_accepted'
   q=subprocess.run([str(exe)],input=inp.read_bytes(),capture_output=True,env=env,check=True)
   assert not q.stderr and hashlib.sha256(q.stdout).hexdigest()==case['actual_sha256']
   assert compare(q.stdout.decode(),ans.read_text(),Decimal('0.000001'))
  public.append(dict(report=str(p.relative_to(R)),report_sha256=H(p),program_sha256=H(exe.with_suffix('.cpp')),binary_sha256=H(exe),cases=count))
visual=[]
for stem,pages in json.loads((R/'build/circle-zero-qa/pages.json').read_text()).items():
 p=R/f'output/pdf/{stem}.pdf';visual.append(dict(pdf=str(p.relative_to(R)),pdf_sha256=H(p),physical_pages_seen=pages,render_png_sha256={f'build/circle-zero-qa/{stem}-{n}.png':H(R/f'build/circle-zero-qa/{stem}-{n}.png') for n in pages},findings='Actual images inspected: complete line function, explicit two-page circle function with continuation line numbers, two complete main programs, numeric-contract note and neighboring transition/index; no clipping or orphan heading; existing font settings unchanged.'))
(R/'verification/circle-zero-visual.json').write_text(json.dumps(dict(scope='14 targeted actual pages, not full-book visual certification',pdfs=visual),indent=2)+'\n')
# Verify current printed ranges reproduce the entire component without omissions.
tex=(R/'docs/generated.tex').read_text();ranges={}
for name in ['line_circle_intersections','circle_intersections']:
 pairs=re.findall(r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,firstnumber=\d+)?\]\{\.\./src/compact/'+name+r'\.hpp\}',tex)
 lines=(R/f'src/compact/{name}.hpp').read_text().splitlines();begin=lines.index('// BEGIN '+name)+1;end=lines.index('// END '+name)
 indices=[i for lo,hi in pairs for i in range(int(lo)-1,int(hi))]
 assert indices==list(range(begin,end))
 ranges[name]=pairs
assert snapshot(R)==source
summary=dict(source_sha256=source,source_inputs=len(source),dedicated=summaries,copy_context={'stages':[{k:s[k] for k in ['name','count','passed','failed']} for s in c['stages']],'unresolved':0},public_data=public,printed_ranges=ranges,visual_sha256=H(R/'verification/circle-zero-visual.json'),restored_pdfs=json.loads((R/'build/circle-zero-pdf-restore.json').read_text()),scope='Targeted final normal and ASan/UBSan validation, fresh 230-program copied-context syntax audit, 37 official public cases per mode with local comparator; two new canonical printed programs executed, existing 228 hashes unchanged. No new full tools/test.sh run, online AC, CI query or LeakSanitizer certification.')
(R/'verification/circle-zero-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Validated source/compiler/frontend/input/log/binary bindings, public outputs, printed ranges and PDF artifacts')
