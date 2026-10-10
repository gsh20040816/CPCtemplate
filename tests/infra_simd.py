import hashlib
import json
import platform
import random
import re
import statistics
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
work = root / 'build/infra-simd'
work.mkdir(parents=True, exist_ok=True)
records = []
for sanitizer in [False, True]:
    flags = ['-std=c++23', '-O2', '-mavx2', '-Wall', '-Wextra']
    if sanitizer:
        flags += ['-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    for file in ['examples/infra/simd_demo.cpp', 'tests/infra_simd.cpp']:
        exe = work / (Path(file).stem + ('_san' if sanitizer else ''))
        vec_log = work / (exe.name + '.vec')
        vec_log.unlink(missing_ok=True)
        cmd = [CXX, *flags, '-fopt-info-vec-optimized=' + str(vec_log), str(root / file), '-o', str(exe)]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
        run = subprocess.run([str(exe)], capture_output=True, text=True, check=True, timeout=30)
        records.append(dict(command=cmd, compiler_stderr=p.stderr, stdout=run.stdout, stderr=run.stderr))
        print(run.stdout.strip(), flush=True)
vec = (work / 'infra_simd.vec').read_text()
assembly = subprocess.check_output(['objdump', '-d', '-C', str(work / 'infra_simd')], text=True)
(work / 'infra_simd.asm').write_text(assembly)
automatic_asm = re.search(r'<automatic_add\([^\n]+>:\n(.*?)(?=\n\n)', assembly, re.S).group(0)
assert 'vpaddd' in automatic_asm and '%ymm' in automatic_asm
samples = {str(i): [] for i in range(3)}
rng = random.Random(17)
for repeat in range(9):
    order = list(samples)
    rng.shuffle(order)
    for mode in order:
        p = subprocess.run([str(work / 'infra_simd'), mode], capture_output=True,
                           text=True, check=True, timeout=30)
        samples[mode].append(float(p.stdout))
    print('SIMD benchmark', repeat + 1, flush=True)
files = [root / p for p in ['examples/infra/simd.hpp', 'examples/infra/simd_demo.cpp',
                           'tests/infra_simd.cpp', 'tests/infra_simd.py']]
cpu = subprocess.check_output(['lscpu'], text=True)
report = dict(status='pass', platform=platform.platform(), cpu=cpu,
              compiler=subprocess.check_output([CXX, '--version'], text=True).splitlines()[0],
              records=records, vectorization_report=vec, samples_ms=samples,
              median_ms={k:statistics.median(v) for k,v in samples.items()},
              benchmark='O2 -mavx2, 2^20 uint32 elements, 100 additions per process, 9 interleaved samples; 0=compiler loop, 1=manual AVX2, 2=manual AVX512F. Setup and result check outside timing; compiler memory barrier retains every repetition.',
              automatic_add_assembly=automatic_asm,
              asm_sha256=hashlib.sha256(assembly.encode()).hexdigest(),
              source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
(root / 'verification/infra-simd.json').write_text(json.dumps(report, indent=2) + '\n')
print(report['median_ms'])
