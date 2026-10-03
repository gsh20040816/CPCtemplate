"""Check current source and the bounded knowledge batch's local receipts."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
R = Path.cwd(); sys.path.insert(0, str(R/'tools'))
from run_provenance import snapshot
from usage_examples import records
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
source = snapshot(R); summaries = {}
for mode, suffix in [('normal','kocfwwh8'),('sanitizer','1b4jzdi6')]:
    path = R/f'build/ballot-knowledge-{mode}-{suffix}/report.json'
    d = json.loads(path.read_text())
    assert d['passed'] and d['mode'] == mode
    assert d['source_before_sha256'] == d['source_after_sha256'] == source
    assert H(d['compiler']) == d['compiler_sha256'] and H(d['frontend']) == d['frontend_sha256']
    for p,h in d['artifacts'].items(): assert H(R/p) == h
    folder = path.parent
    assert (folder/'actual.txt').read_bytes() == (folder/'expected.txt').read_bytes()
    assert not (folder/'stderr.txt').read_bytes()
    assert d['compile_returncode'] == d['run_returncode'] == 0
    assert d['formula_checks'] == 1108 and d['api_counts'] == {'F':1108,'L':6648,'E':8864}
    assert d['counts'] == {'walks':40955,'strict_first_step_bijections':988,'weak_reflections':2821,'general_reflections':6961}
    shutil.copyfile(path,R/f'verification/ballot-knowledge-{mode}.json')
    summaries[mode] = dict(report_sha256=H(path), counts=d['counts'], formula_checks=d['formula_checks'], api_counts=d['api_counts'])
# This knowledge-only batch has no production or registered-use changes.
assert not subprocess.check_output(['git','diff','619f7960272e17c1fb810e5264ae9f32e4625ee6','--','src','verify','docs/usage','docs/usage-examples.json','docs/catalog.json'])
rows = records(); previous = json.loads(subprocess.check_output(['git','show','619f796:verification/usage-examples.json'],text=True))
assert len(rows) == len(previous) == 232
for row in rows: assert row['program_sha256'] == previous[row['id']]['program_sha256']
knowledge = json.loads((R/'docs/knowledge-taxonomy.json').read_text())
assert len(knowledge['entries']) == knowledge['scope']['classified_section_count'] == 26
assert len(knowledge['scope']['source_files']) == 13
assert sum(r['path'].startswith('math/') for r in knowledge['entries']) == 24
# Every previous knowledge source remains byte-identical.
old = json.loads(subprocess.check_output(['git','show','619f796:docs/knowledge-taxonomy.json'],text=True))
for p in old['scope']['source_files']:
    assert (R/p).read_bytes() == subprocess.check_output(['git','show','619f796:'+p])
assert not subprocess.check_output(['git','diff','619f796','--','docs/main.tex','docs/preamble.tex'])
visual = []
for stem, pages in json.loads((R/'build/ballot-knowledge-qa/pages.json').read_text()).items():
    pdf = R/f'output/pdf/{stem}.pdf'
    visual.append(dict(pdf=str(pdf.relative_to(R)),pdf_sha256=H(pdf),physical_pages_seen=pages,
                       render_png_sha256={f'build/ballot-knowledge-qa/{stem}-{n}.png':H(R/f'build/ballot-knowledge-qa/{stem}-{n}.png') for n in pages},
                       findings='Actual final images inspected: two-page reflection note, readable equations, modular-condition references, subsequent Stirling core and infrastructure. Explicit page boundary prevents the newly inserted note from splitting the next full core. Fonts unchanged.'))
assert sum(len(r['physical_pages_seen']) for r in visual) == 9
(R/'verification/ballot-knowledge-visual.json').write_text(json.dumps(dict(scope='Nine targeted actual pages, not full-book visual certification',pdfs=visual),indent=2)+'\n')
assert snapshot(R) == source
summary = dict(source_sha256=source,source_inputs=len(source),dedicated=summaries,
               preserved_program_hashes=232,preserved_prior_knowledge_sources=12,knowledge_sections=26,
               visual_sha256=H(R/'verification/ballot-knowledge-visual.json'),
               pdf_preservation=json.loads((R/'build/ballot-knowledge-pdf-restore.json').read_text()),
               scope='Knowledge-only addition. Actual existing combinatorial APIs tested on bounded cases; no new algorithm, copied-context rerun, all-usage-runtime run, full-suite, online AC, CI or LeakSanitizer claim.')
(R/'verification/ballot-knowledge-checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified final source, compiler/frontend, input/expected/output/binary artifacts, 232 unchanged programs, 12 preserved knowledge files and nine actual PDF pages')
