from pathlib import Path
import json, hashlib, subprocess, sys, datetime, collections
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from run_provenance import snapshot, validate_receipt, baseline_archive, baseline_hashes
from usage_examples import records
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
M=json.loads((R/'verification/runs/20261003-static-modint-full-regression.json').read_text())
old=M['source_sha256']; now=snapshot(R)
changed=sorted(k for k in old.keys()|now.keys() if old.get(k)!=now.get(k))
assert changed==['docs/USAGE-COVERAGE.md','docs/usage-coverage.json']
old_cov=json.loads(subprocess.check_output(['git','show','48829b07:docs/usage-coverage.json'],cwd=R))
new_cov=json.loads((R/'docs/usage-coverage.json').read_text())
assert len(old_cov)==len(new_cov)==208
count=0
for a,b in zip(old_cov,new_cov):
 assert {k:v for k,v in a.items() if k!='status'}=={k:v for k,v in b.items() if k!='status'}
 if a['status']!=b['status']:
  assert a['status']=='generated_unverified' and b['status'].startswith('locally_checked_');count+=1
assert count==43
old_md=subprocess.check_output(['git','show','48829b07:docs/USAGE-COVERAGE.md'],cwd=R).decode().splitlines()
new_md=(R/'docs/USAGE-COVERAGE.md').read_text().splitlines()
assert len(old_md)==len(new_md)
for a,b in zip(old_md,new_md):
 if a!=b:
  assert a.endswith('| generated_unverified |')
  assert a.rsplit('|',2)[0]==b.rsplit('|',2)[0]
proof=json.loads((R/'verification/usage-examples.json').read_text())
rows=records();assert len(rows)==228
for row in rows:
 p=proof[row['id']];assert p['program_sha256']==row['program_sha256'] and p['modes']==['normal','sanitizer']
P=json.loads((R/'verification/runs/20261003-static-modint-fixed-all-printed.json').read_text())
assert P['source_before_sha256']==P['source_after_sha256']==old and P['passed']
assert P['proof_sha256']==H(R/'verification/usage-examples.json')
assert P['log_sha256']==H(R/'verification/runs/20261003-static-modint-fixed-all-printed.log')
assert P['wrapper_sha256']==H(R/'build/check-static-modint-fixed-all-printed.py')
for key in ['compiler','frontend']:
 assert P[key+'_sha256']==P[key+'_after_sha256']==H(P[key])
B=baseline_hashes(baseline_archive(R)); durations={}
for mode,dirname in [('normal','20261003T025115.559649Z-normal-10cbebd8'),('sanitizer','20261003T031626.374804Z-sanitizer-b8aed013')]:
 x=validate_receipt(R,R/'verification/runs'/dirname/'receipt.json',mode,old,B)
 durations[mode]=(datetime.datetime.fromisoformat(x['end']['finished_at_utc'])-datetime.datetime.fromisoformat(x['start']['started_at_utc'])).total_seconds()
V=json.loads((R/'verification/static-modint-visual.json').read_text())
for p in V['pdfs']:
 assert H(R/p['pdf'])==p['pdf_sha256']
 for path,h in p['render_png_sha256'].items():assert H(R/path)==h
assert sum(len(p['physical_pages_seen']) for p in V['pdfs'])==13
out={'tested_source_commit':'48829b07d1e2a55125f67d86c2d09589466ebe7b','tested_inputs':len(old),'full_suite_seconds':durations,'printed_programs':228,'printed_cases_per_mode':628,'printed_executions':1256,'printed_seconds':P['seconds'],'copy_context':'222 standard plus 6 explicitly GNU-dependent, no unresolved syntax contexts','visual_pages':13,'post_run_metadata_only_changes':{k:{'before':old[k],'after':now[k]} for k in changed},'coverage_status_changes':count,'coverage_counts':dict(collections.Counter(x['status'] for x in new_cov)),'scope':'Full receipts bind the tested 48829b07 snapshot. Afterwards only two coverage indexes were refreshed from current program-hash evidence; no code, tests, snippets, PDF or other source changed. This checked metadata delta is not a new full-suite run. No online AC, CI, LeakSanitizer or universal correctness claim. The earlier failed full receipt remains preserved.'}
(R/'verification/runs/20261003-static-modint-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
