# Static ModInt unit-inverse checkpoint

Tested implementation and compatibility repair: `48829b07d1e2a55125f67d86c2d09589466ebe7b`, after `cd7a9918e0b9771372332230f4bf1b45a93b17c3`.

- Static `ModInt` now supports unit inverses for every positive int modulus; `try_inv` reports nonunits, while `inv` and division retain an invertibility precondition. This expands the former prime-only contract; Binomial, NTT, Gauss and FPS retain their independent prime assumptions.
- Full normal suite: 1510.351080 seconds. Full ASan/UBSan suite: 3483.227190 seconds. Both receipts bind the same 1308 source inputs and 93 pinned historical-baseline files. See `20261003-static-modint-full-regression.json`.
- Fresh exact printed programs: 228 programs, 628 canonical cases per mode, 1256 executions, 1145.456403 seconds. These are execution certificates, not universal correctness or online acceptance.
- Separate copied-context syntax audit: 222 standard and 6 explicitly GNU-dependent programs, no unresolved context. Dedicated static inverse tests also compile and exercise the actual narrow-header class with assertions and NDEBUG.
- Thirteen actual PDF pages were inspected. Their PDF and rendered-image hashes were rechecked; no font changes.
- Preserve the earlier full-suite failure: two old minimal test preludes omitted the newly required standard headers. Both were fixed, and the P1313 full-program pin was updated only after proving the old class substitution reproduces the old hash. Oracles were not weakened.
- After the full run, only `docs/USAGE-COVERAGE.md` and `docs/usage-coverage.json` were refreshed from the verified current program hashes. The 43 changed statuses are explicitly recorded in `20261003-static-modint-checkpoint.json`; no implementation, test, snippet, PDF or other source changed. The executable check in the adjacent `.py` verifies this metadata-only delta against the frozen receipts. It does not relabel these receipts as a run on the refreshed metadata.
- Current component usage categories: 154 formal-template uses, 43 application-only, 8 API-only, 3 pending. These are not counts of online AC.
- No CI queries or online submissions were performed for this batch. LeakSanitizer is disabled. Existing specialized test memory/stack settings and unsanitized independent reference helpers remain as documented by their individual tests.
