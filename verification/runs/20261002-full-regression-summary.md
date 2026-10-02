# Full regression checkpoint: b5e25ec

Both staged full-suite runs passed against the same frozen src/tests/tools/verify/docs inputs and pinned historical classic baseline. The manifest validates their complete input hashes, log hashes, compiler fingerprints, recorded stack settings, return codes, and absence of ASan/UBSan failure diagnostics.

- Normal: `20261002T093458.243548Z-normal-d9831e2d/receipt.json`
- ASan/UBSan: `20261002T095502.751924Z-sanitizer-50e9ef63/receipt.json`
- Aggregate: `20261002-full-regression.json`
- All 213 exact printed programs separately rerun in both modes: `20261002-all-printed-usages.json`, 570 cases per mode, 1140 executions

LeakSanitizer was disabled. The interpolation core stage explicitly uses 32 MiB global / 128 KiB thread-local ASan quarantine, as recorded by the runner; it must not be described as an all-default-quarantine run. Other stages retain their recorded environment. Existing compiler warnings in legacy tests are retained in logs; passing sanitizer diagnostics does not mean warning-free compilation.

This checkpoint applies to b5e25ec inputs only. Later changes require their own validation, and this is local regression evidence, not online AC or a universal correctness proof.
