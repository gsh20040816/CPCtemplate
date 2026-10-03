# Frozen knowledge-expansion regression checkpoint

Tested source: `f341b631022cd4fc755bad88db153b25fcd23d7c`, with 1,305 unchanged source inputs and 93 pinned classic baseline files. Counts remain 208 algorithms and 228 usages; classified knowledge is now 24 sections in 11 sources.

- Full normal suite: exit 0, 24m40.475s
- Full ASan/UBSan suite: exit 0, 56m29.363s

Both official receipts were independently validated against current source and staged-baseline hashes, their complete logs, actual stack observations, compiler-driver identity and the separately captured compiler-frontend fingerprint. The aggregate manifest is `20261003-knowledge24-full-regression.json`; concise evidence hashes and receipt paths are in `20261003-knowledge24-checkpoint.json`.

This integrates the floor-sum migration, Matrix Tree proof/graph routing, and partition constraint conversions into the full test run. It includes their new preservation, classification and mathematical checks. The full suite remains the exact command `bash tools/test.sh` with its recorded environment; this is not a separately repeated exhaustive execution of all 228 printed programs. Earlier all-printed and copy-context proofs retain their original input scope and are not relabeled as new runs.

GNU14.2, the fixed classic baseline `1a9fa3e91d7dff58915341040be069611370054c`, and a 512 MiB process soft stack are recorded. LeakSanitizer is disabled. Interpolation stages keep the documented 32 MiB global /128 KiB thread quarantine exception. Nested CF732F maximum cases retain their documented soft stacks, capped at the unchanged hard limit. The partition/recurrence application script's two independent reference programs stay plain -O2 even in sanitizer mode; its tested application binaries use the selected profile. RealPolarLess additionally checks float-cast-overflow. Compiler warnings are retained in logs.

Two earlier attempts had no terminal receipt: one normal and one sanitizer. Their logs and separate interruption notes are preserved. Their exit status and interruption cause remain unknown, so neither pass nor algorithm failure is inferred. Only the two completed receipts above support this checkpoint.

Known default floating-circle judge precision mismatches, ComplexFFT timing/platform assumptions, and outstanding online coverage remain unchanged. No CI query, online acceptance, entire source-page coverage, whole-toolchain identity or universal correctness claim is made. This proof-only publication does not cover later source edits.
