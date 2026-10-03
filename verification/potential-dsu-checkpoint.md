# PotentialDSU checkpoint — 2026-10-03

This additive batch introduces an independent exact additive-potential DSU and formal Library Checker usage232. Existing plain/rollback DSU and other production algorithms are unchanged. Semantics, derivation and limits: [POTENTIAL-DSU.md](../docs/POTENTIAL-DSU.md).

- Final source snapshot: 1334 inputs under src/tests/tools/verify/docs; before and after maps match the actual final files
- Each ordinary and ASan/UBSan profile runs full-header and minimal-standard-header core forms. Each core form checks 231714 graph states and 7574415 ordered-pair differences, plus 200000-node balanced/sequential merge cases
- Core reference is an independently traversed accepted-constraint graph. Integer and modular groups include signed/zero differences, composite moduli, modulus1 structural connectivity, tag isolation, repeated/rejected/self constraints, root swaps, and large alternating/all-positive/all-negative offsets within the stated safe bound
- Five named mutated implementations are rejected by actual oracle assertions: wrong offset sign, omitted sign reversal on root swap, omitted parent offset on compression, accepted contradiction and unknown-as-zero
- Direct, registered-expanded and actually copied formal programs each run 103 generated official-domain inputs per profile: 100 small BFS-oracle cases, a hand certificate and two N=Q=200000 cases. These are local inputs within official constraints, not upstream official test files
- Stack limits are inherited unchanged (8MiB soft/unlimited hard in this run). No custom large-stack requirement for this union-by-size find
- New canonical usage232 was freshly executed in both profiles. The preceding231 program hashes and records remain unchanged; they were not all reexecuted in this batch
- Fresh copied-context audit covers232 programs:226 standard and6 explicit GNU contexts; unresolved0. Syntax/copyability is separate from correctness
- Four fixed-version upstream statement/parameter/checker/verifier hashes match the existing inventory. No external source was executed
- Nine actual PDF pages inspected: main230–232, data-structures13–15 and147–148, infra10. Core is split at a method boundary with continuous line numbers; usage and mint dependency resolve correctly. Fonts unchanged
- All eight PDFs have warning-free final logs and contiguous page destinations;1163 dependency name/page/section groups and16 cross-PDF jumps resolve. Five unrelated PDFs retain prior bytes after comparison of text, full named destination properties and annotations

Receipts: [normal](potential-dsu-normal.json), [ASan/UBSan](potential-dsu-sanitizer.json), [copied contexts](potential-dsu-copy-context.json), [visual checks](potential-dsu-visual.json), [input/artifact manifest](potential-dsu-checkpoint.json). [The validator](potential-dsu-validate.py) checks compiler/frontend, generated sources, binaries and recorded stdin/expected/stdout/stderr against their hashes before publishing.

No new online AC, speed rank, CI result, full tools/test.sh run or LeakSanitizer certification is claimed. The most recent full-suite checkpoint remains the separate static-ModInt run; later changes have explicitly scoped targeted evidence.
