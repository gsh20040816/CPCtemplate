# Numerical real Gaussian elimination — 2026-10-03

New independent GaussReal and API usage 233. [Contract and derivation](../docs/GAUSS-REAL.md). Existing exact modular/XOR solvers are unchanged. Coefficient-row scaling, partial pivoting and explicit eps define a numerical model; rank/consistency/kernel are not exact original-system certificates. The probability note now links to the interface while retaining the separate absorption/finite-expectation proof.

## Bounded local verification

Final ordinary and ASan/UBSan profiles each execute 456 systems in four core forms: full header and minimal standard headers, each with assertions and with NDEBUG. Includes rectangular/empty shapes, independent Fraction arithmetic on small integer systems, planted rank/contradictions, row permutations and power-of-two scaling, exact binary threshold expectations, significant tiny-factor updates, and structured 100×100 full-rank/rank 50 cases.

The Fraction reference is an independent exact-arithmetic implementation of Gauss–Jordan mathematics, not a different algorithm. Strict row diagonal dominance and explicit [I | tail] constructions provide separate references for the two size 100 cases. Threshold examples are compared against the declared truncated model, not falsely asserted to be exact nullspaces of the original input.

Each profile also runs:

- Five rejected mutants: no row swap, wrong elimination sign, omitted RHS elimination, skipped small factor, retained skipped active column. The first triggers a nonfinite assertion; the other four disagree with the independent expected result
- Four representative invalid preconditions (zero eps, INT_MAX n, malformed row, NaN input) in each assertion-enabled core form. These are not run with NDEBUG and are not exhaustive invalid-input/overflow detection
- 23 complete numerical-protocol inputs in each of direct/registered-expanded/actually-copied API programs; independent parsing rejects invalid status integers, incorrect rank/output lengths and nonfinite values

Vector comparison uses |actual−expected|/(1+|expected|). Separately, non-threshold cases check each original equation with |Ax−b|/(sum|a_j x_j|+|b|), using 0/0=0; kernel directions use b=0. Decimal arithmetic with 100 digits recomputes these residuals. The stored maximum combines the mixed vector-comparison metric and componentwise residual; it is not a pure relative-forward-error bound or a universal accuracy guarantee.

Final source map has 1343 inputs; compiler/frontend, generated sources, binaries and all stdin/stdout/stderr streams are hashed. The exact rational case/expectation artifact is retained. [Validator](gauss-real-validate.py) recomputes the cases and reparses all core and complete-program output streams against their expected models, then checks artifact hashes. [Normal](gauss-real-normal.json), [ASan/UBSan](gauss-real-sanitizer.json), [manifest](gauss-real-checkpoint.json).

## Copying and presentation

New canonical usage 233 executes in both modes. The previous 232 expanded program hashes/records stay unchanged; they were not all reexecuted. Fresh 233-program copied-context syntax audit has 227 standard plus 6 explicit GNU contexts, unresolved 0. [Copy report](gauss-real-copy-context.json).

Nine final actual pages inspected: main 223–225 and 211; mathematics 185–187 and 173; infra 10. Complete core is split at the normalization/elimination boundary with continuous line numbers. Allman braces and 88-column limit are retained. The usage is explicitly API-only. Probability references and source/usage page numbers resolve. Font settings unchanged; six unrelated PDFs retain prior bytes after text, full named-destination properties and annotation checks.1173 dependency groups and 16 cross-PDF jumps pass. [Visual evidence](gauss-real-visual.json).

Counts:210 components,233 uses;157 formal-template-covered,43 application-only,9 API-only,1 pending. GaussReal adds one API-only component, not a new formally verified P3389 driver. Knowledge classification stays 26 sections. No online AC, speed rank, CI, all-usage-runtime, full tools/test.sh, exact-rank/full-domain numerical guarantee or LeakSanitizer certification is claimed.
