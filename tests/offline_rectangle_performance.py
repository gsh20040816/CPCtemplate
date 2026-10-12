from pathlib import Path
import subprocess,time,statistics,json,hashlib
p=Path('build/library-checker-reference/data_structure/rectangle_sum'); o=Path('build/offline-rectangle')
subprocess.run(['/opt/homebrew/bin/g++-16','-O2','-std=c++20',str(p/'sol/correct.cpp'),'-o',str(o/'reference')],check=True)
results=[]
for inp in sorted((p/'in').glob('max_random*.in')):
 times={'normal':[],'reference':[]}
 for repeat in range(3):
  for mode in (['normal','reference'] if repeat%2==0 else ['reference','normal']):
   with inp.open('rb') as f:
    start=time.perf_counter();subprocess.run([str(o/mode)],stdin=f,stdout=subprocess.DEVNULL,check=True);times[mode].append(time.perf_counter()-start)
 med={k:statistics.median(v) for k,v in times.items()};ratio=med['normal']/med['reference']
 results.append(dict(case=inp.stem,seconds=times,median_seconds=med,ratio=ratio,over_80_percent_slower=ratio>1.8))
report=dict(tested_bundle_sha256=hashlib.sha256((o/'submission.cpp').read_bytes()).hexdigest(),scope='Local same compiler C++20 O2 sequential alternating runs; wall-clock includes I/O, not OJ ranking',reference='Official offline Fenwick sweep; same algorithmic approach',reference_source_sha256=hashlib.sha256((p/'sol/correct.cpp').read_bytes()).hexdigest(),cases=results)
Path('verification/offline-rectangle-performance.json').write_text(json.dumps(report,indent=2)+'\n')
print([(x['case'],round(x['ratio'],2)) for x in results])
