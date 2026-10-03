# Static ModInt compatibility repair record

This is the repair-stage record, not the final full-suite result.

At source `cd7a9918e0b9771372332230f4bf1b45a93b17c3`, the new type's dedicated ordinary/ASan-UBSan checks and copy-context audit passed. The first full normal run stopped when the inclusion-exclusion test's narrow copied-component prelude lacked `<optional>`. Its failed receipt and complete log are preserved under `runs/20261003T021811.373969Z-normal-724e7305/`. Source hashes were unchanged. The sequential full sanitizer had not started.

A read-only audit found the same omission in `tests/binomial_coefficient_application.py`. Both minimal preludes now explicitly include `<optional>` and `<utility>` for the new return type and `swap`. They remain narrow standard-header contexts; they were not replaced by `bits/stdc++.h`. No production implementation changed in this repair.

P1313's deliberately pinned expanded-program hash also required an explicit reviewed refresh. The driver hash is unchanged. Replacing only the new `ModInt` class with its old class reproduces the old full-program hash exactly, proving that all bytes outside the intentional class extension are unchanged. The source-pin guard remains in place; cases and independent oracles were not weakened. See `static-modint-program-pin-migration.json`.

After these changes:

- Inclusion-exclusion: both profiles passed 26,983 queries in each of two contexts, with source/dependency/compiler/frontend/generated-file bindings independently checked. New receipts: `static-modint-inclusion-normal.json` and `static-modint-inclusion-sanitizer.json`
- P1313: both profiles passed 2,657 cases in each of three contexts, with source/compiler/program/binary bindings independently checked. Current receipts: `binomial-coefficient-normal.json` and `binomial-coefficient-sanitizer.json`

The first all-printed runtime run at `cd7a9918` also passed: 228 programs, 628 canonical cases per profile and 1,256 executions in 1,120.080 seconds. Its report is `runs/20261003-static-modint-all-printed.json`; its exact canonical proof is archived as `runs/20261003-static-modint-first-usage-proof.json`. It is not relabeled as a full-suite pass or as a run of the later repaired source snapshot.

A new full normal/sanitizer checkpoint and fresh all-printed runtime run are required for the repaired snapshot. Their final receipts, rather than these intermediate observations, determine completion. No CI or online-acceptance claim is made.
