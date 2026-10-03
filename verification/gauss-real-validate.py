"""Validate final GaussReal source and artifact-bound local numerical receipts."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
R=Path.cwd();sys.path[:0]=[str(R/'tools'),str(R/'tests')]
from run_provenance import snapshot
from usage_examples import records
import gauss_real
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=snapshot(R);cases=gauss_real.make_cases();selected=cases[:9]+cases[-14:];summaries={}
for mode,suffix in [('normal','wf5hkzmo'),('sanitizer','f3ekdpkz')]:
    p=R/f'build/gauss-real-{mode}-{suffix}/report.json';d=json.loads(p.read_text())
    assert d['passed'] and d['mode']==mode and d['source_before_sha256']==d['source_after_sha256']==source
    assert H(d['compiler'])==d['compiler_sha256'] and H(d['frontend'])==d['frontend_sha256']
    assert H(R/d['exact_reference_file'])==d['exact_reference_sha256']
    for a in [*d['core'].values(),*d['programs'].values(),*d['mutations'].values()]:
        assert H(R/a['source'])==a['source_sha256'] and H(R/a['binary'])==a['binary_sha256']
    assert len(d['core'])==4 and all(v['cases']==456 for v in d['core'].values())
    assert len(d['programs'])==3 and all(v['cases']==23 for v in d['programs'].values())
    assert len(d['mutations'])==5
    core_bins={str(R/v['binary']) for v in d['core'].values()};program_bins={str(R/v['binary']) for v in d['programs'].values()}
    cursor={p:0 for p in program_bins};checked=0
    for c in d['commands']:
        for k in ['stdin','stdout','stderr']:
            if k in c:assert H(R/c[k])==c[k+'_sha256']
        assert c['returncode'] in [0,-6]
        if c['returncode']==-6:assert 'Assertion' in (R/c['stderr']).read_text()
        if len(c['command'])==1 and c['command'][0] in core_bins:
            assert (R/c['stdin']).read_text()==str(len(cases))+'\n'+''.join(gauss_real.input_case(x) for x in cases)
            gauss_real.validate_output((R/c['stdout']).read_text(),cases);checked+=1
        if len(c['command'])==1 and c['command'][0] in program_bins:
            key=c['command'][0];case=selected[cursor[key]];cursor[key]+=1
            assert (R/c['stdin']).read_text()==gauss_real.input_case(case)
            gauss_real.validate_output((R/c['stdout']).read_text(),[case],False)
    assert checked==4 and all(v==23 for v in cursor.values())
    assert sum(c['returncode']==-6 for c in d['commands'])==9
    shutil.copyfile(p,R/f'verification/gauss-real-{mode}.json')
    summaries[mode]=dict(report_sha256=H(p),core=d['core'],programs=d['programs'],negative_mutations=5,debug_assertion_rejections=8)
base=R/'build/gauss-real-copy-final-allman-20261003';d=json.loads((base/'report.json').read_text())
assert d['input_sha256_before']==d['input_sha256_after'] and not d['changed_inputs'] and d['unresolved_count']==0 and d['registered_count']==233
assert H(d['compiler']['path'])==d['compiler']['sha256']
for p,h in d['input_sha256_before'].items():assert H(R/p)==h
for stage in d['stages']:
    for row in stage['results']:
        assert hashlib.sha256(row['program'].encode()).hexdigest()==row['program_sha256']==row['source_sha256_after']==H(base/row['source_file'])
        assert H(base/row['diagnostics_file'])==row['diagnostics_sha256']
shutil.copyfile(base/'report.json',R/'verification/gauss-real-copy-context.json')
rows=records();proof=json.loads((R/'verification/usage-examples.json').read_text());old=json.loads(subprocess.check_output(['git','show','89251e8:verification/usage-examples.json'],text=True))
assert len(rows)==len(proof)==233
for row in rows:
    assert row['program_sha256']==proof[row['id']]['program_sha256'] and proof[row['id']]['modes']==['normal','sanitizer']
    if row['id']!='example-233':assert proof[row['id']]==old[row['id']]
# Verify addition-only production scope and existing font settings.
changed=subprocess.check_output(['git','diff','89251e8','--name-only','--','src','verify'],text=True).splitlines()
assert set(changed)<={'src/compact/gauss_real.hpp','verify/api/real_linear_system.compact.cpp'}
assert not subprocess.check_output(['git','diff','89251e8','--','docs/main.tex','docs/preamble.tex'])
assert max(map(len,(R/'src/compact/gauss_real.hpp').read_text().splitlines()))<=88
tex=(R/'docs/generated.tex').read_text();ranges=re.findall(r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,firstnumber=\d+)?\]\{\.\./src/compact/gauss_real.hpp\}',tex)
lines=(R/'src/compact/gauss_real.hpp').read_text().splitlines();start=lines.index('// BEGIN GaussReal')+1;end=lines.index('// END GaussReal')
assert [i for lo,hi in ranges for i in range(int(lo)-1,int(hi))]==list(range(start,end))
visual=[]
for stem,pages in json.loads((R/'build/gauss-real-qa/pages.json').read_text()).items():
    pdf=R/f'output/pdf/{stem}.pdf'
    visual.append(dict(pdf=str(pdf.relative_to(R)),pdf_sha256=H(pdf),physical_pages_seen=pages,render_png_sha256={f'build/gauss-real-qa/{stem}-{n}.png':H(R/f'build/gauss-real-qa/{stem}-{n}.png') for n in pages},findings='Final actual images inspected: complete two-page core with continuous numbering, API-only protocol, probability linkage and infra. No clipping, font settings unchanged.'))
assert sum(len(r['physical_pages_seen']) for r in visual)==9
(R/'verification/gauss-real-visual.json').write_text(json.dumps(dict(scope='Nine targeted actual pages; not full-book visual certification',pdfs=visual),indent=2)+'\n')
assert snapshot(R)==source
summary=dict(source_sha256=source,source_inputs=len(source),dedicated=summaries,copy_context=[{k:s[k] for k in ['name','count','passed','failed']} for s in d['stages']],preserved_old_programs=232,printed_core_ranges=ranges,visual_sha256=H(R/'verification/gauss-real-visual.json'),pdf_preservation=json.loads((R/'build/gauss-real-pdf-restore.json').read_text()),scope='New numerical-model API only, targeted ordinary/ASan/UBSan including valid NDEBUG. Small exact arithmetic plus constructed size100 and explicit threshold references. Not exact rank, arbitrary-original-system accuracy, P3389 full-domain, online AC, all-use runtime, full tools/test.sh, CI or LeakSanitizer certification.')
(R/'verification/gauss-real-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified final GaussReal source, numerical outputs, compiler/frontend, binaries, all recorded streams, 233 copied contexts and nine actual PDF pages')
