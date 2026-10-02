#!/usr/bin/env python3
"""Narrow Linux official-corpus receipt runner; no network or tracked-checkout writes.

Uses the repository's bundler, but adds verifier, pinned hash checks, Linux
per-child wait4 RSS, and durable partial receipts missing from official_cases.py.
"""
import argparse, datetime, hashlib, json, os, platform, shutil, subprocess, time, tomllib
from pathlib import Path

PIN = 'e64660561a995c357cdc61ddee1bde68b80528db'
PROBLEM = 'data_structure/dynamic_sequence_range_affine_range_sum'
p = argparse.ArgumentParser(__doc__)
p.add_argument('checkout', type=Path)
p.add_argument('bundler', type=Path)
p.add_argument('driver', type=Path)
p.add_argument('report', type=Path)
p.add_argument('--program', type=Path, help='Exact pre-extracted program; no registration claim is implied')
p.add_argument('--timeout', type=float, default=60)
p.add_argument('--sanitize', action='store_true', help='ASan+UBSan, LSan disabled')
p.add_argument('--work-dir', type=Path, required=True, help='Raw outputs and binaries go here, outside receipt directory')
a = p.parse_args()
a.report = a.report.resolve()
assert not a.report.exists(), 'Refuse to overwrite historical receipts; choose a new report filename'
a.report.parent.mkdir(parents=True, exist_ok=True)
w = a.work_dir.resolve()
assert not w.exists(), 'Choose a fresh work directory to preserve prior evidence'
assert a.report.parent not in w.parents and w != a.report.parent, 'Raw work directory must be outside receipt directory'
w.mkdir(parents=True)
up = a.checkout.resolve(); folder = up / PROBLEM
def sha(f):
    h = hashlib.sha256()
    with Path(f).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
mode = 'asan_ubsan_lsan_off' if a.sanitize else 'normal'
flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-sanitize-recover=all'] if a.sanitize else ['-std=c++20', '-O2']
env = os.environ.copy()
overrides = {'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1:abort_on_error=1', 'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'} if a.sanitize else {}
env.update(overrides)
bindings = {'WORK':w, 'CHECKOUT':up, 'DRIVER':a.driver.resolve(), 'BUNDLER':a.bundler.resolve()}
if a.program: bindings['PROGRAM'] = a.program.resolve()
def portable(value):
    value = str(value)
    for name, path in sorted(bindings.items(), key=lambda item:len(str(item[1])), reverse=True):
        value = value.replace(str(path), '${'+name+'}')
    return value
report = dict(status='running', scope='Local pinned official generated corpus only; not online AC, printed registration verification, or controlled speed ranking', reference_commit=PIN, reference_problem_path=PROBLEM, recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=[], timing_definition='Wall seconds from before Popen through wait4 reap, including launch and up to 5ms polling overhead; shared host, not isolated OJ timing', rss_definition='Per-child Linux wait4 ru_maxrss in KiB, converted to bytes; launch-inclusive process high-water mark, not algorithm-only RSS, not cumulative child usage', platform=platform.platform())
report.update(schema_version=2, mode=mode, compiler_flags=flags, environment_overrides=overrides, effective_sanitizer_environment={k:env.get(k) for k in ('ASAN_OPTIONS','UBSAN_OPTIONS','LSAN_OPTIONS')}, runner_sha256=sha(__file__), path_bindings={k:os.path.relpath(v,a.report.parent) for k,v in bindings.items()}, raw_artifact_policy='Binaries, bundle, outputs and raw logs are outside receipt directory; receipt contains hashes and bounded stderr excerpts')
def save():
    temp = a.report.with_suffix('.tmp')
    temp.write_text(json.dumps(report, indent=2)+'\n'); temp.replace(a.report)
def run(command, label, inp=None, timeout=60):
    out = w/(label+'.stdout'); err = w/(label+'.stderr')
    start = time.monotonic(); timedout=False
    with (Path(inp).open('rb') if inp else open(os.devnull,'rb')) as fi, out.open('wb') as fo, err.open('wb') as fe:
        child = subprocess.Popen([str(x) for x in command], stdin=fi, stdout=fo, stderr=fe, env=env)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid: break
            if time.monotonic()-start > timeout:
                timedout=True; child.kill(); pid,status,usage=os.wait4(child.pid,0); break
            time.sleep(.005)
        child.returncode=os.waitstatus_to_exitcode(status)
    return dict(command=[portable(x) for x in command], exit_code=child.returncode, timeout=timedout, wall_launch_inclusive_seconds=round(time.monotonic()-start,6), rss_launch_inclusive_bytes=usage.ru_maxrss*1024, stdout=portable(out), stderr=portable(err), stdout_sha256=sha(out), stderr_sha256=sha(err), stderr_excerpt=err.read_text(errors='replace')[:8000], stderr_excerpt_truncated=err.stat().st_size>8000)
def ok(receipt):
    assert receipt['exit_code']==0 and not receipt['timeout'], receipt
save()
try:
    assert platform.system()=='Linux', 'RSS units and wait4 semantics currently Linux-only'
    assert subprocess.check_output(['git','-C',str(up),'rev-parse','HEAD'],text=True).strip()==PIN
    assert not subprocess.check_output(['git','-C',str(up),'diff','HEAD','--'],text=True), 'Tracked reference files changed'
    meta=tomllib.loads((folder/'info.toml').read_text())
    names={f"{Path(t['name']).stem}_{i:02d}.in" for t in meta['tests'] for i in range(t['number'])}
    assert len(names)==33 and {f.name for f in (folder/'in').glob('*.in')}==names
    official_hash=json.loads((folder/'hash.json').read_text())
    report.update(metadata_sha256=sha(folder/'info.toml'), official_hash_manifest_sha256=sha(folder/'hash.json'), driver=portable(a.driver.resolve()), driver_sha256=sha(a.driver), corpus_count=33, parameters=meta['params'])
    compiler=os.environ.get('CXX') or shutil.which('g++-16') or shutil.which('g++')
    report['compiler']=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    bundle=w/'main.cpp'
    if a.program:
        bundle.write_bytes(a.program.read_bytes()); report['program_source']=portable(a.program.resolve()); report['program_source_sha256']=sha(a.program)
    else:
        report['bundle_receipt']=run(['python3',a.bundler,a.driver,bundle],'bundle'); save(); ok(report['bundle_receipt'])
    report['bundle_sha256']=sha(bundle)
    exe=w/'main'; verifier=w/'verifier'
    report['compile_receipt']=run([compiler,*flags,bundle,'-o',exe],'compile',timeout=120); save(); ok(report['compile_receipt'])
    report['verifier_compile_receipt']=run([compiler,'-std=c++17','-O2','-I',up/'common',folder/'verifier.cpp','-o',verifier],'compile-verifier',timeout=120); save(); ok(report['verifier_compile_receipt'])
    report.update(executable_sha256=sha(exe), verifier_source_sha256=sha(folder/'verifier.cpp'), verifier_binary_sha256=sha(verifier), checker_source_sha256=sha(folder/'checker.cpp'), checker_binary_sha256=sha(folder/'checker'))
    for name in sorted(names):
        inp=folder/'in'/name; ans=folder/'out'/(inp.stem+'.out')
        row=dict(case=inp.stem, input_sha256=sha(inp), answer_sha256=sha(ans), status='running'); report['cases'].append(row); save()
        assert row['input_sha256']==official_hash[inp.name] and row['answer_sha256']==official_hash[ans.name], 'Upstream hash mismatch'
        row['official_manifest_hashes_match']=True
        row['verifier']=run([verifier],inp.stem+'-verify',inp,a.timeout); save(); ok(row['verifier'])
        row['candidate']=run([exe],inp.stem+'-candidate',inp,a.timeout); save(); ok(row['candidate'])
        actual=w/(inp.stem+'-candidate.stdout'); row['output_sha256']=sha(actual)
        candidate_stderr=(w/(inp.stem+'-candidate.stderr')).read_text(errors='replace')
        assert not any(marker in candidate_stderr for marker in ('runtime error:', 'ERROR: AddressSanitizer', 'AddressSanitizer:DEADLYSIGNAL', 'LeakSanitizer')), candidate_stderr[:8000]
        row['checker']=run([folder/'checker',inp,actual,ans],inp.stem+'-check',timeout=15); save(); ok(row['checker'])
        row['checker_message']=(w/(inp.stem+'-check.stderr')).read_text().strip()
        row['status']='local_official_verifier_and_checker_accepted'; save()
        print(inp.stem, 'PASS', row['candidate']['wall_launch_inclusive_seconds'], row['candidate']['rss_launch_inclusive_bytes'], flush=True)
    inp=folder/'in'/'example_00.in'; ans=folder/'out'/'example_00.out'
    # Valid-looking, numerically wrong output tests wrong-answer rejection rather than just format rejection.
    tokens=ans.read_text().split(); assert tokens
    tokens[0]=str((int(tokens[0])+1)%998244353)
    wrong=w/'negative-control.out'; wrong.write_text('\n'.join(tokens)+'\n')
    report['negative_control']=run([folder/'checker',inp,wrong,ans],'negative-control',timeout=15); save()
    assert report['negative_control']['exit_code']==1 and not report['negative_control']['timeout'], report['negative_control']
    report['negative_control']['description']='Numerically wrong first answer in otherwise valid example output rejected with WA (exit 1)'
    report['negative_control']['message']=(w/'negative-control.stderr').read_text().strip()
    assert sha(a.driver)==report['driver_sha256'], 'Driver changed during run'
    assert sha(bundle)==report['bundle_sha256'], 'Bundle changed during run'
    if a.program: assert sha(a.program)==report['program_source_sha256'], 'Program source changed during run'
    report['status']='pass'; save(); print(mode, '33/33 official cases PASS; wrong-output negative control rejected; not online AC',flush=True)
except BaseException as exc:
    report['status']='failed'; report['failure']=portable(repr(exc)); save(); raise
