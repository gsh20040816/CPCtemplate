# Bounded adaptive Simpson checkpoint

Added one callable long-double component, API-only example 235, and one classified numerical-integration knowledge section. The result exposes value, an error indicator, evaluation count and met. met is an estimated-condition result, not certified accuracy. Depth, sample budget, coordinate stagnation and nonfinite arithmetic have visible stopping behavior; exceptions propagate. No forced-minimum-depth policy is copied from OI Wiki.

## Final targeted checks

- Ordinary and ASan/UBSan reports bind the same 1,361 source files. Each runs 191 cases in four core forms (header/copied, assertions/NDEBUG), with counted callbacks and independently computed analytic references. Runtime uses mpmath 1.3.0 at 100 decimal digits; version observation is recorded separately, not a hermetic dependency attestation.
- References include polynomial antiderivatives, atan, exp, cos and erf; interval reversal, zero length, shift/scale, cancellation and narrow intervals. Maximum absolute error among successful ordinary analytic cases is about 1.081e-12; this explicitly excludes the deliberate alias and forced-stop cases.
- Exact Fraction expansion gives the smooth five-node alias integral 5/1419264, while the algorithm deliberately reports 0 / error 0 / met=true. This is a retained limitation test, not hidden failure or universal accuracy proof.
- Budgets 0..10 include partial-child exhaustion. The limit 7 quartic fallback is independently 2461/12288, checking the unvisited sibling is retained. Tests also cover depth exhaustion, adjacent/two-ULP endpoints, nonfinite samples, arithmetic overflow, tolerance underflow and callback exception propagation.
- The parent-sum overflow case and an odd-subnormal budget case are executed. For eps=3d, rounded child budgets 2d each accept error 2d; the parent must reject summed 4d. Five deliberately wrong implementations, including removal of that parent check, are rejected; their sources, binaries and actual output files are retained locally and hashed in reports.
- Each of three complete API program forms runs 25 valid/protocol inputs plus five rejection cases per mode. The central example 235 is independently executed in both modes. Old 234 usage records and expanded program hashes are unchanged; this is not a rerun of all usage programs.
- Fresh 235-example syntax/copy audit: 229 with standard headers, six with documented GNU headers, zero unresolved. It does not certify algorithm correctness.

## Sources and rendering

Pinned WIDA and OI Wiki blobs were read; returned bytes independently reproduce their Git blob IDs and have recorded SHA256 hashes. WIDA's original global integrand/submissions are not reproduced. OI Wiki's fixed-grid implementation and minimum-depth behavior are outside this replacement. Only the two relevant ledger rows become partial. kuangbin's locked PDF page was not obtained and remains pending.

Actual final total-book pages 218–222, mathematics 181–185 and infra 10 were inspected. The 62-line component breaks at the recursive-lambda boundary with continuous numbering; the main and knowledge derivation each stay together. Fonts unchanged. Six unrelated PDFs retain original bytes after text/destination/annotation equivalence checks. Dependency audit: 1,177 groups; infra: 16 jumps.

Counts: 211 components / 235 uses, 157 formal-template + 43 application-only + 11 API-only; 28 classified knowledge sections across 15 sources (math 26, graph 2), 70 legacy sections remain. No online AC, formal-problem credit, performance ranking, complete source-page coverage, new full-suite run or LeakSanitizer certification is claimed. The 18a054b paired full-suite evidence remains historical.
