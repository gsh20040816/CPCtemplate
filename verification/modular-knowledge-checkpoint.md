# Modular-condition knowledge checkpoint

This batch changes knowledge organization and tests, not algorithm implementations or usage programs.

- Move the original “模运算的适用条件” section into the pinned 数学 → 数论 → 模算术简介 leaf. The original prefix is preserved except its explicit label and a corrected prime-modulus qualification for factorial/inverse-factorial preprocessing; the source fixture and two exact amendments are retained.
- Add complete congruence root families using the actual ax+b≡0 API convention, nonunit examples, integer quotient lifting modulo md, safe signed64 right-hand-side normalization, prime-factorial/Lucas limitations, and the generalized Euler threshold proof and counterexamples. Modulus1 and zero exponents are explicit. A lifted modulus must remain valid for the algorithm computing its numerator.
- Correct the adjacent Binomial expansion prose to extended-Euclidean inversion, matching current ModInt. Its asymptotic bound and prime-only contract are unchanged.
- Each final normal and ASan/UBSan run checks 960 inverse calls, 39950 congruences, 3025 CRT merges, 56904 exponentiations and 10065 Lucas queries: 110904 actual API answers. Independent references enumerate full residue sets, use repeated multiplication, and construct exact Pascal rows. In addition, 120600 integer quotient identities cover negative and positive numerators.
- The new exponent probe uses moduli 1..40. The separate existing euler_power.cpp was recompiled and rerun in both modes for its selected full-unsigned64 moduli, 65-bit reduced exponent cases and 200-digit exponents. This broader evidence is not attributed to the small-modulus probe. Neither probe newly certifies ModInt, Binomial or ExLucas.
- Final source, compiler/frontend, actual inputs, expected/actual outputs and executable hashes were independently checked. The scope consists of 1322 source inputs; no new full tools/test.sh run or LeakSanitizer certification is claimed.
- All 230 printed-program hashes remain unchanged. There are still 208 components, 156 formal-template-use components, 43 application-only, 8 API-only and 1 pending; no new algorithm, example count or online AC is added.
- Knowledge classification is now 25 labeled sections across 12 source files: 23 mathematics and 2 graph theory. The legacy appendix retains 71 sections, including non-mathematics material; this does not assert those are 71 missing mathematical topics.
- Nine actual PDF pages were inspected: three new pages and the corrected Binomial paragraph in each of the main/math books, plus the infrastructure jump index. Fonts are unchanged, five other PDF files retain their previous bytes after semantic equality checks. Final books: 638 main pages and 218 mathematics pages including front matter. All 1152 dependency groups and 16 cross-volume links resolve.

Final local reports: modular-knowledge-normal.json, modular-knowledge-sanitizer.json, modular-knowledge-checkpoint.json and modular-knowledge-visual.json. The adjacent validation helper checks the retained artifacts and reruns the separate Euler test; run it from the repository root after materializing its recorded build artifacts.

Dedicated tests can be reproduced with GNU C++ 14 via CXX, ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 and UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1:

- python3 tests/modular_knowledge.py
- python3 tests/modular_knowledge.py --sanitizer
- python3 tests/knowledge_taxonomy.py
- python3 tests/math_knowledge_integration.py
- python3 tests/floor_knowledge_migration.py

No CI query or online submission was performed. Earlier provisional checks are not relabeled as the final source-bound runs.
