"""Validate this batch's archived local evidence against its recorded source snapshot."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
R = Path.cwd(); sys.path.insert(0, str(R / 'tools'))
from run_provenance import snapshot
from usage_examples import records
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source = snapshot(R); summaries = {}
for mode, suffix in [('normal', 'bsducj__'), ('sanitizer', 'fy91hqeo')]:
    p = R / f'build/potential-dsu-{mode}-{suffix}/report.json'; d = json.loads(p.read_text())
    assert d['passed'] and d['mode'] == mode
    assert d['source_before_sha256'] == d['source_after_sha256'] == source
    assert H(d['compiler']) == d['compiler_sha256'] and H(d['frontend']) == d['frontend_sha256']
    for a in [*d['core'].values(), *d['programs'].values(), *d['negative_mutations'].values()]:
        assert H(R / a['source']) == a['source_sha256'] and H(R / a['binary']) == a['binary_sha256']
    for c in d['commands']:
        for k in ['stdin', 'stdout', 'stderr', 'expected']:
            if k in c: assert H(R / c[k]) == c[k + '_sha256']
        if 'expected' in c:
            assert (R / c['stdout']).read_text().split() == (R / c['expected']).read_text().split()
        assert c['returncode'] in [0, -6]
        if c['returncode'] == -6: assert 'Assertion' in (R / c['stderr']).read_text()
    assert sum(c['returncode'] == -6 for c in d['commands']) == len(d['negative_mutations']) == 5
    assert all(v['official_domain_inputs'] == v['cases'] == 103 for v in d['programs'].values())
    assert d['environment']['ASAN_OPTIONS'] == 'detect_leaks=0:halt_on_error=1'
    assert all('231714 graph states, 7574415 full-pair differences' in v['stdout'] for v in d['core'].values())
    shutil.copyfile(p, R / f'verification/potential-dsu-{mode}.json')
    summaries[mode] = dict(report_sha256=H(p), core=[v['stdout'] for v in d['core'].values()],
                           programs=d['programs'], inherited_stack=d['inherited_stack'])
base = R / 'build/potential-dsu-copy-final-20261003'; d = json.loads((base / 'report.json').read_text())
assert d['input_sha256_before'] == d['input_sha256_after'] and not d['changed_inputs']
assert d['unresolved_count'] == 0 and d['registered_count'] == 232
assert H(d['compiler']['path']) == d['compiler']['sha256']
for p, h in d['input_sha256_before'].items(): assert H(R / p) == h
for stage in d['stages']:
    for row in stage['results']:
        assert hashlib.sha256(row['program'].encode()).hexdigest() == row['program_sha256'] == row['source_sha256_after'] == H(base / row['source_file'])
        assert H(base / row['diagnostics_file']) == row['diagnostics_sha256']
shutil.copyfile(base / 'report.json', R / 'verification/potential-dsu-copy-context.json')
rows = records(); proof = json.loads((R / 'verification/usage-examples.json').read_text())
assert len(rows) == len(proof) == 232
previous = json.loads(subprocess.check_output(['git', 'show', 'd3c8c6b560a70638297019c78af936ce1753741e:verification/usage-examples.json'], text=True))
for row in rows:
    assert proof[row['id']]['program_sha256'] == row['program_sha256'] and proof[row['id']]['modes'] == ['normal','sanitizer']
    if row['id'] != 'example-232': assert proof[row['id']] == previous[row['id']]
up = next(x for x in json.loads((R / 'docs/library-checker-inventory.json').read_text())['problems'] if x['id'] == 'unionfind_with_potential')
for name, evidence in up['sources'].items(): assert H(R / 'build/potential-dsu-upstream' / name) == evidence['sha256']
tex = (R / 'docs/generated.tex').read_text()
ranges = re.findall(r'\\lstinputlisting\[firstline=(\d+),lastline=(\d+)(?:,firstnumber=\d+)?\]\{\.\./src/compact/potential_dsu.hpp\}', tex)
lines = (R / 'src/compact/potential_dsu.hpp').read_text().splitlines()
start, end = lines.index('// BEGIN PotentialDSU') + 1, lines.index('// END PotentialDSU')
assert [i for lo, hi in ranges for i in range(int(lo)-1, int(hi))] == list(range(start, end))
# No pre-existing core, driver, or font/configuration file was changed by this additive batch.
changed = subprocess.check_output(['git','diff','d3c8c6b560a70638297019c78af936ce1753741e','--name-only','--','src','verify'], text=True).splitlines()
assert set(changed) <= {'src/compact/potential_dsu.hpp','verify/library_checker/unionfind_with_potential.compact.cpp'}
font_changes = subprocess.check_output(['git','diff','d3c8c6b560a70638297019c78af936ce1753741e','--','docs/main.tex','docs/preamble.tex'], text=True)
assert not font_changes
visual = []
for stem, pages in json.loads((R / 'build/potential-dsu-qa/pages.json').read_text()).items():
    pdf = R / f'output/pdf/{stem}.pdf'
    visual.append(dict(pdf=str(pdf.relative_to(R)), pdf_sha256=H(pdf), physical_pages_seen=pages,
                       render_png_sha256={f'build/potential-dsu-qa/{stem}-{n}.png': H(R / f'build/potential-dsu-qa/{stem}-{n}.png') for n in pages},
                       findings='Actual images inspected: full core across two numbered method-boundary pages, formal usage, dynamic mint dependency and infrastructure references. No clipping, unchanged fonts.'))
assert sum(len(v['physical_pages_seen']) for v in visual) == 9
(R / 'verification/potential-dsu-visual.json').write_text(json.dumps(dict(scope='Nine targeted actual pages, not full-book visual certification', pdfs=visual), indent=2) + '\n')
assert snapshot(R) == source
summary = dict(source_sha256=source, source_inputs=len(source), dedicated=summaries,
               copy_context=[{k:s[k] for k in ['name','count','passed','failed']} for s in d['stages']],
               old_program_hashes_preserved=231, upstream_sources=up['sources'], printed_core_ranges=ranges,
               visual_sha256=H(R / 'verification/potential-dsu-visual.json'),
               pdf_preservation=json.loads((R / 'build/potential-dsu-pdf-restore.json').read_text()),
               scope='New independent PotentialDSU only; targeted normal/ASan/UBSan and new use232. The other231 program records retain unchanged current hashes, not a new full-runtime run. Generated formal-domain inputs are not upstream official test files. No online AC, ranking, CI, full tools/test.sh or LeakSanitizer claim.')
(R / 'verification/potential-dsu-checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
print('Verified final source, compiler/frontend, generated source/binaries, all recorded inputs/expected/output, 232 copied contexts and nine PDF pages')
