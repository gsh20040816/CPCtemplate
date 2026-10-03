# Manhattan MST checkpoint

Added the four-sweep O(n log n) Manhattan MST component, formal Library Checker example236 and one graph knowledge section. The implementation supports the full signed64 coordinate domain by widening before arithmetic, returns an exact signed128 total and original vertex indices, preserves duplicates and does not mutate input. The shared ordinary dsu is unchanged; size-based root choice is local to Kruskal.

## Final source-bound checks

The four final reports bind the same 1,371 source files before and after execution. Earlier runs overlapping document/layout edits were rejected by source-integrity guards and are not used as final evidence.

- Ordinary and ASan/UBSan core: 10,426 point sets in four forms per mode, header/minimal-copy × assertions/NDEBUG. Independent Python arbitrary-precision dense Prim checks small/random instances; six 200,000-point closed-form families check scale, duplicate classes, fullwidth signed64 coordinates and a total exceeding signed64
- For n≤8, candidate distances, repeated-call determinism and 234,917 cut-minimum certificates per form are checked. Larger cases check returned tree, weight and unchanged input, not exhaustive cuts
- Five mutations are rejected. Three connectivity mutations fail the implementation’s final tree-size assertion; wrong-weight and narrow-coordinate mutations fail independent output checks. This is not a claim that all five are independently rejected with assertions disabled
- Ordinary and ASan/UBSan application: 84 inputs × three full programs per mode, direct driver/printed expansion/minimal copy. Every input passes the pinned official verifier; output is checked both by the official checker and an independent tree certificate validator. The official Fenwick reference has a different structure from the map sweep; small references are cross-checked with dense Prim and the five local maximum-size families have closed-form optima
- The 84 inputs consist of 69 local/fixture cases plus 15 instances from five locked upstream generator families using explicitly local seeds0,1,2. They are not the canonical hidden judge dataset. The official sample is byte-equal to pinned upstream example_00.in. Reference output and checker result bytes are hashed
- Official reference/checker/verifier/generators use ordinary O2 builds even when candidate programs are sanitized. LSan is disabled. No online AC, judge ranking or five-second judge-limit certification is claimed
- Central example236 passes normal and ASan/UBSan. All old235 usage records and program hashes are unchanged; this is not a rerun of every old example. The output checker accepts alternative optimal trees and rejects wrong cost, suboptimal trees, cycles, invalid endpoints and wrong edge counts; all28 existing/new invalid certificate controls pass
- Fresh236-program copy audit:230 standard-header successes, six documented GNU-header successes, zero unresolved, stable input hashes. This is syntax/copyability evidence, not runtime coverage

## Sources, proof and printed artifacts

KACTL’s single CC0 ManhattanMST.h is pinned at27faa89f9b47e5fa4578eadea6122b59da544052; retrieved bytes independently reproduce the Git blob ID and have a SHA256 receipt. Library Checker task/common sources, tools and generated input/output hashes are recorded. This does not commit to whole-KACTL coverage. kuangbin4.19’s original PDF page remains unreviewed.

The closed-cone proof explicitly handles equality. Duplicate zero chains either provide a cut’s zero minimum or allow contraction. Among closest crossing pairs, maximizing the sum of endpoint x coordinates rules out equality substitutions; diagonal edges choose a shallow right-facing cone. The half-open-octant strict lemma is not copied into the closed implementation. Independent review found no algorithm, contract or proof blocker.

Actual final PDF file pages inspected: total book417–421 and425–427; graph volume53–57 and61–63; infra10. The71-line component is split before the activity map, with continuous numbering and explicit continuation context. The complete example and complete knowledge derivation each stay on their own page. Font sets are unchanged. Five unrelated PDFs preserve original bytes after text, all named-destination properties and annotation equivalence. Dependency audit:1,183 groups; infra:16 verified external jumps; eight final logs have no layout warnings and page anchors are contiguous.

Counts:212 components/236 uses,158 formal-template +43 application-only +11 API-only, no missing direct use;29 classified knowledge sections across16 sources (math26,graph3),70 legacy sections remain unclassified. Formal-example status is separate from online AC. This checkpoint does not replace historical full-suite evidence at4f7d654; a new full pair is required for the added source.
