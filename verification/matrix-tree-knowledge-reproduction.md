# MatrixTree knowledge: targeted reproduction

Both final local profiles passed five selected tests. This is TARGETED evidence under schema `cpc-targeted-matrix-tree-knowledge-v1`; it is not a full-suite, CI, online-judge, leak-detection, or formal-proof claim.

## Selected tests

- `tests/matrix_tree.cpp`
- `tests/matrix_tree_mod.cpp`
- `tests/determinant_mod.cpp`
- `tests/matrix_tree_application.py` (compact P6178 driver, 103 complete invocations)
- `tests/matrix_tree_knowledge.py` (finite exact Python checks; not sanitizer-instrumented code)

## Reproduction

Run from the repository root with GNU C++ 14.2.0 and the existing Boost include tree. The helper uses `tools.run_provenance.stage_inputs` and fixed baseline `1a9fa3e91d7dff58915341040be069611370054c`; that commit must exist locally. A new stage and retained logs are created for each run.

```sh
mkdir -p build
cp verification/matrix-tree-knowledge-check.py build/matrix-tree-knowledge-check.py
python3 build/matrix-tree-knowledge-check.py --mode normal --root "$PWD" --boost-include "$PWD/build/deps/boost-1.83/usr/include"
python3 build/matrix-tree-knowledge-check.py --mode sanitizer --root "$PWD" --boost-include "$PWD/build/deps/boost-1.83/usr/include"
```

Normal C++ flags: `-std=c++20 -Wall -Wextra -O2`. Sanitizer C++ flags: `-std=c++20 -Wall -Wextra -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer`. The unchanged Python application owns its compiler flags, captured in the subprocess trace.

Sanitizer options: `ASAN_OPTIONS=detect_leaks=0:halt_on_error=1`, `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`. PIE and quarantine use compiler/runtime defaults. Each child receives a 524288 KiB soft stack capped by the inherited hard limit; the hard limit is unchanged.

## Retained provenance

Each receipt includes original and staged file hashes before/after, fixed-baseline hashes, exact commands, command stdout/stderr, separate retained logs and hashes, Boost manifest, compiled-artifact hashes, compiler driver and cc1plus hashes before/after, and helper hash and full command recipe. The exact tested helper is retained here as `matrix-tree-knowledge-check.py`.

Helper SHA256: `8f12ebf5ddd214d896f64852bdc84fe1e966e54475882cad849dd4c32525143c`

Independent post-run validation checked both current and staged source maps, baseline/archive, every retained command log, combined logs, generated artifacts, all 105 actual P6178 subprocess calls (bundle + compile + 103 invocations), Boost manifest/files, compiler driver/frontend, and the helper. Result: PASS for both profiles.

Original-source manifest SHA256: `9e032ed8480fa3f4b8cf94b6fd847fe3008ad3dbbe47d5321be112946ccd0038`

Staged-source manifest SHA256: `cabcd2eeb36531964efc7b790836f275cfa7778eeec4d3d92ed1a83f1a93aecf`

- normal receipt SHA256: `29b53965117ee50102a497b7debf6b1959d91b07abbc3554e746db385937e867`
- normal combined-log SHA256: `c9a3d9ac8161e6e88e5a1d8df2076eb3ac8fddb9d5b5c2801fd449ae7cb4062d`
- sanitizer receipt SHA256: `5d0d15b1cfeed11ab5f1cf8170ea0419e65c30c183c0d4af9d03222786bd4445`
- sanitizer combined-log SHA256: `c39ea91222277ddfd8583cb58d4834f8fae5b782725fb00351766ef37a2ab5cf`
