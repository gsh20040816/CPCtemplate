#!/usr/bin/env python3
"""Record source hashes after successful test runs. Does not confer OJ verification."""
import hashlib,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
logs={}
for name in ['local-tests.txt','sanitizer-tests.txt']:
 p=root/'verification'/name;s=p.read_text()
 if 'lowlink removal oracle PASS' not in s or 'error:' in s or 'runtime error:' in s:raise SystemExit('Incomplete/failing log: '+name)
 logs[name]=s.splitlines()
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['src','tests'] for p in sorted((root/folder).rglob('*')) if p.is_file()}
(root/'verification/manifest.json').write_text(json.dumps({'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler':'GCC 16.2.0, C++20, macOS arm64','verification':'local randomized/exhaustive small-instance oracles and ASan/UBSan; not a universal correctness proof','logs':logs,'sha256':files},indent=2)+'\n')
