# Ordered HLD checkpoint

The existing HLD component gains path_ordered(u,v,work,edge=false). The old commutative path interface and both recursive DFS bodies are unchanged, verified against the retained original header. This is one component extension, not a new algorithm-count entry.

- Callback intervals are closed and 1-based. rev selects decreasing or increasing dfn order, and callbacks themselves occur in actual u→v order. Edge mode excludes only the LCA position; it does not invert edge operators. Rebuilding with another root requires rebuilding dfn-dependent structures.
- New official-template usage 231 pairs existing segtree with forward/reverse affine aggregates. Its statement, info, checker and verifier were read from fixed upstream commit e64660561a995c357cdc61ddee1bde68b80528db and their hashes match the existing inventory. N,Q≤200000; official slopes are nonzero. This is the static-tree problem, not link/cut.
- Each final normal and ASan/UBSan run executes 1546 trees and 765632 exact directed vertex/edge path checks in each of two core forms. Independent BFS parent/depth reconstruction supplies ordered paths; tests include exhaustive labelled trees through 6 vertices, all roots and pairs, reversed adjacency, relabelled trees, a multi-chain certificate and 200000-vertex chain/star/binary trees.
- Each of direct, registered-expanded and actual copied full programs runs 114 inputs per mode: 104 official-domain inputs and 10 zero-slope extensions. Three official inputs have N=Q=200000. Small cases use literal function-by-function path evaluation; maximum star is direction-sensitive, while maximum chain/binary cases emphasize size and path length with independent formulas.
- Three deliberately wrong HLD versions fail the exact-order oracle. A separate reversed affine-intercept formula returns 15 instead of 13 in a hand certificate. Optimized Python execution is refused.
- The child soft stack is explicitly 512MiB, preserving the inherited hard limit. Old hld.cpp compatibility uses its existing 256MiB pthread stack. Recursive DFS stack sensitivity remains; local timings and these stack settings do not certify the judge environment or a speed rank.
- Old hld.cpp passes both modes against the pinned historical baseline. The existing mo_tree_usages suite also passes both modes: 302 modified-Mo inputs, 247 path-intersection inputs and 251 diameter inputs, including CF379F with q=500000 and 1000004 vertices. Expanded current-source hashes are checked separately.
- Canonical printed usages 44, 170 and 231 were freshly executed in both modes; the other 228 hashes remain current. No fresh all 231 runtime run or full tools/test.sh run is claimed.
- Fresh all 231 copied-context syntax audit: 225 standard contexts plus 6 explicitly GNU-dependent, no unresolved contexts. Parent validation checks current source maps, compiler/frontend, generated code, binaries, stdin/expected/stdout/stderr artifacts, official source hashes and printed ranges.
- Seventeen actual PDF pages were inspected, including the new graph-volume segtree dependency. Fonts are unchanged; five unrelated PDFs retain their previous bytes after semantic equality checks. An unintended ModifiedMo pagination change was detected during preservation comparison and restored before final reruns. 1157 dependency groups and 16 cross-volume links resolve.

Reports: hld-ordered-normal.json, hld-ordered-sanitizer.json, hld-ordered-copy-context.json, hld-ordered-checkpoint.json and hld-ordered-visual.json. The adjacent validation helper operates from the repository root with the recorded build artifacts. Reproduce dedicated cases with:

- CXX=/usr/bin/x86_64-linux-gnu-g++-14 python3 tests/hld_ordered.py
- CXX=/usr/bin/x86_64-linux-gnu-g++-14 ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 python3 tests/hld_ordered.py --sanitizer

Current counts: 208 components, 231 uses; 156 formal-template-use components, 43 application-only, 8 API-only, 1 pending. Knowledge counts remain 25 separately mapped sections. No new online AC, CI query or LeakSanitizer certification.
