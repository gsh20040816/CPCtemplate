# Static 3D weak-dominance checkpoint

One independently encapsulated Dominance3D component returns original-order counts of other coordinatewise-smaller-or-equal input occurrences. Exact duplicate groups contribute multiplicity−1 internally, full signed64 coordinates require comparisons only, input is preserved, and repeated/empty calls have no external state. The sufficient n≤INT_MAX/2 bound also protects the shared signed-int Fenwick update step; Fenwick itself is unchanged. Formal P3810 example237 converts these counts to the required histogram.

## Final targeted evidence

- Ordinary and ASan/UBSan core each check6,975 point sets in four forms: header/minimal-copy × assertions/NDEBUG. Independent Python pairwise comparisons, not a duplicate CDQ, check the complete {0,1}³ multiset family through size6 and shuffled orders, fixed-coordinate ties, random and signed64 extremes
- Metamorphic families cover input permutation, all six axis permutations, strictly increasing coordinate relabeling and triplication q(count+1)−1. Every case also checks unchanged input, repeated calls and interleaved empty/two-duplicate calls
- Six100,000-point families have independent closed forms: chain, antichain, identical extremes, Cartesian grid, duplicated grid and fullwidth signed64 chain
- Nine deliberately wrong implementations are independently rejected with -DNDEBUG: strict y, strict z, unit insert, missing self exclusion, missing rollback, x-only sorting, collapsed group index, balanced±1 weights, and wrong original-index scattering. Mutants exit normally without sanitizer diagnostics; rejection comes from result checks
- Ordinary and ASan/UBSan P3810 application each check71 valid inputs across direct driver, printed expansion and minimal-copy program. Five100,000-point families have closed-form histograms; all other references use direct quadratic coordinate comparisons. All output lengths, values and histogram totals are checked
- The official statement was read for its exact weak relations, self exclusion, duplicate behavior, domain and histogram output. Retrieved text did not expose samples; the five-point illustration and all local test cases are not advertised as official samples, hidden judge data or an official checker
- Central example237 passes both modes. Old236 usage records and program hashes remain unchanged; this is not a rerun of all old examples
- ASan/UBSan apply to compiled candidate programs. Python exact reference calculations are not sanitized, LSan is disabled. No online AC, submission ranking or complete-source-page certification

The source pin is the OI Wiki navigation revision bc070e827180fbd75c2e27a16c1212f1d671d949 with its CDQ page as conceptual reference. The connector-returned text has a SHA256 receipt, explicitly not an independently reproduced Git blob ID. This implementation uses its own local-vector interface and existing Fenwick. Static point-pair counting is distinguished from the existing ordered convolution-DP CDQ; dynamic events, strict variants, weighted counts and dynamic MST remain outside this component.

PDF, copy-context, final source hashes and counts are recorded in the adjacent JSON checkpoint. This targeted checkpoint does not claim a new full-suite run; the completed Manhattan recovery pair remains tied to its earlier source snapshot.

## Rendering and final counts

All four final reports bind the same1,378 source files, unchanged before/after. Fresh237-program copy audit has231 standard-header successes plus six documented GNU-header successes, zero unresolved and stable inputs. This audit is syntax-only.

Actual final file pages viewed: total book611–615 and miscellaneous volume4–7 (nine pages). The63-line component splits at the CDQ lambda with continuous numbering; the second page also contains the complete P3810 call. Eight PDFs have unchanged font sets, final logs contain no warnings, and six unrelated PDFs preserve original bytes after full text, destination-property and annotation equivalence. Dependency audit:1,194 groups; infra:16 external jumps.

Counts:213 components/237 uses;159 formal-template,43 application-only,11 API-only, no missing direct use. Classified knowledge remains29 sections in16 files (math26,graph3),70 legacy sections; the standalone derivation here does not inflate classified-section counts. No source-ledger pending row was silently closed merely because the new component exists.
