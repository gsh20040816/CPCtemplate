import math,random,subprocess,tempfile
from pathlib import Path
assert (-3)//2==-2
assert pow(3,-1,7)==5
assert math.isqrt(10**30)==10**15
rng=random.Random(20260913)
assert 1<=rng.randrange(1,100)<100
with tempfile.TemporaryDirectory(prefix='cpc-infra-') as tmp:
    path=Path(tmp)
    script='set -euo pipefail\nname="file with spaces.txt"\nprintf "%s\\n" \'literal $value\' > "$name"\ncat < "$name"\n'
    result=subprocess.run(['bash','-c',script],cwd=path,text=True,capture_output=True,check=True)
    assert not result.stderr and result.stdout=='literal $value\n'
print('Infra Python/Bash examples: exact arithmetic, fixed random bounds and quoted file paths PASS')
