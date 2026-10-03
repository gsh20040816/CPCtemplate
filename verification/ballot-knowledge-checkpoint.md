# Catalan and ballot reflection checkpoint — 2026-10-03

Knowledge-only addition: [knowledge-ballot.tex](../docs/knowledge-ballot.tex). Covers weak prefix balance, Catalan, strict ballot first-step reduction, arbitrary nonnegative initial/final heights, reachability/parity, empty paths, and modular binomial selection. Exact primary grouping is the pinned OI Wiki Catalan leaf. There are now26 classified sections in13 sources (24 mathematics,2 graph theory); prior12 knowledge sources remain byte-identical, and71 legacy sections are still not comprehensively classified.

## Local evidence

Each final ordinary/ASan/UBSan profile:

- Enumerates40955 short path/start-height pairs
- Checks2821 weak first-hit reflections and6961 generalized reflections, including inverse, injectivity and complete target-set equality
- Checks988 nonempty strict first-step reductions; images equal the entire corresponding weak-tail sets, including empty tails
- Checks1108 formula cases against literal walks, independent height-state DP, or Catalan convolution recurrence
- Executes the actual existing Binomial/Lucas/ExLucas APIs for1108/6648/8864 answers (16620 total), including prime-crossing Lucas, composite moduli, modulus1, negative binomial-index guards, and normalized subtraction
- Checks wrong boundary shift, weak/strict conflation and invalid modular division counterexamples; these are mathematical negative controls, not five mutated production implementations

Final source map contains1337 inputs. Both mode receipts bind the exact source before/after, compiler/frontend, executable, actual input, expected output, actual output and diagnostics. [Validator](ballot-knowledge-validate.py), [normal](ballot-knowledge-normal.json), [ASan/UBSan](ballot-knowledge-sanitizer.json), [full manifest](ballot-knowledge-checkpoint.json).

All13 knowledge-taxonomy tests pass. The232 existing expanded program fingerprints remain unchanged; no copied-context or all-usage runtime rerun is claimed for this knowledge-only batch. No production header or registered driver changed.

## PDF review

Nine final actual pages inspected: main170–173, mathematics132–135, infra10. The knowledge note uses two pages, breaking at the initial-height generalization and before subsequent algorithms. This prevents insertion from splitting the previously complete Stirling core. Font settings are unchanged. Six unrelated PDFs retain prior bytes after text, named-destination properties and annotation comparisons.

Eight final logs are warning-free, page anchors remain contiguous,1169 dependency name/page/section groups and16 cross-PDF jumps resolve. [Visual evidence](ballot-knowledge-visual.json). This is targeted inspection, not a claim that every book page was visually rechecked.

No new algorithm/template/OJ coverage, online AC, speed rank, CI, full-suite or LeakSanitizer claim. The new result is a checked modeling explanation using existing arithmetic interfaces.
