#!/usr/bin/env python3
"""Record source hashes after successful test runs. Does not confer OJ verification."""
import hashlib,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
logs={}
for name in ['local-tests.txt','sanitizer-tests.txt']:
 p=root/'verification'/name;s=p.read_text()
 if any(marker not in s for marker in ['lowlink removal oracle PASS', 'Sequence treap / vector oracle PASS', 'Tagged GCD treap / vector oracle and recycled capacity PASS', 'Blossom exhaustive n<=6, subset DP, duplicate edges and dense graph PASS', 'BM exhaustive minimality, recurrence holdout and uint64 matrix oracle PASS', 'Tarjan SCC exhaustive digraphs, reachability and condensation oracle PASS', 'Biconnected subset/removal oracles and block/bridge forests PASS', 'PAM exhaustive substrings, suffix links, repeated counts and 200000 letters PASS', 'Centroid distance/Floyd oracle, zero weights, overflow boundary and recursive chain PASS', 'DSU-on-tree ancestor histogram, reroot/reset, recursive chain and star PASS', 'Affine segment tree int128 oracle, composition, modulus one and large range PASS', 'Virtual tree all-pairs LCA closure, compressed paths, reroot and recursive chain PASS', 'P2495 dual-style bundled drivers / exhaustive edge cuts PASS', 'Persistent array branching versions, snapshots, allocation bounds and reserve PASS', 'Circle degeneracy, scale invariance and 100-digit overlap reference PASS']) or 'error:' in s or 'runtime error:' in s:raise SystemExit('Incomplete/failing log: '+name)
 logs[name]=s.splitlines()
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['src','tests'] for p in sorted((root/folder).rglob('*')) if p.is_file()}
(root/'verification/manifest.json').write_text(json.dumps({'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiler':'GCC 16.2.0, C++20, macOS arm64','verification':'local randomized/exhaustive small-instance oracles and ASan/UBSan; not a universal correctness proof','logs':logs,'sha256':files},indent=2)+'\n')
