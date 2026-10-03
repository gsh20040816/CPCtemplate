# Source-bound local verification

The old `verification/local-tests.txt`, `sanitizer-tests.txt`, and
`manifest.json` are historical evidence. A PASS marker in those files does **not**
verify today's source. Do not relabel, refresh, or overwrite them to imply it does.

## Run and aggregate

From the repository root, after completing all source and documentation changes:

```sh
bash tools/test.sh
SANITIZE=1 bash tools/test.sh
```

Each command uses `tools/test_baseline.py`, stages the suite (including `docs/`),
overlays `src/classic` from the pinned commit
`1a9fa3e91d7dff58915341040be069611370054c`, and executes `bash tools/test.sh`.
It streams output and prints the unique receipt path at the end. The retained files
are `verification/runs/<UTC-mode-random-id>/output.log` and `receipt.json`.
A failing process or changed inputs produces a failed receipt and a nonzero exit;
an interruption/staging error may leave an incomplete run directory, which cannot
be aggregated. No prior receipt/log is overwritten. Do not set
`CPC_BASELINE_STAGED=1` manually: that bypasses receipt capture.

Use the two explicitly selected receipt paths:

```sh
python3 tools/manifest.py \
  --normal verification/runs/<normal-run>/receipt.json \
  --sanitizer verification/runs/<sanitizer-run>/receipt.json \
  --output verification/runs/<new-manifest-name>.json
```

The output must be a new file under `verification/runs/`. Existing files, including
historical manifests, are never overwritten. No arguments means an error, not a
fallback to old text logs. Both runs must match the current inputs exactly. A source,
test, tool, driver, or documentation change requires rerunning both modes. Run the
two modes against a stable checkout; concurrent edits deliberately invalidate them.

## Recursive-test stack on Linux

Linux suite children request a 524288 KiB (512 MiB) soft stack limit by default,
matching the existing macOS recursive-test stack allocation. Override for this
invocation with `CPC_TEST_STACK_KIB=<positive-integer>` (at most ten digits). The
requested soft value is capped at the inherited hard limit; the hard limit is
never changed. This affects only the suite shell and its child processes, not
system settings or the invoking parent's resource limits. If the hard limit is too
small for a recursive test, that run can still fail and cannot be certified.

The receipt distinguishes an environment-supplied request from the default and
records inherited soft/hard limits and the planned capped soft limit. The suite
logs the actual soft/hard limits after adjustment in `CPC_TEST_STACK`; capture and
aggregation require that observation to match the plan. The actual observation is
also retained in the receipt's end record. Both the shell change and provenance
helpers are source-bound, so pre-change receipts cannot certify this change.

A focused Linux check reproduced the 200000-node lowlink test's SIGSEGV with an
8192 KiB stack; the same normal binary and its ASan/UBSan counterpart passed with
524288 KiB. The latter used `ASAN_OPTIONS=detect_leaks=0`. This is a local diagnosis
of stack exhaustion for that test, not a full-suite result or an algorithm rewrite.

## Binding and metadata

- Input SHA256 maps include the required top-level `README.md` and every regular file under `src/`, `tests/`, `tools/`,
  `verify/`, and `docs/`, excluding Python caches (`__pycache__`, `*.pyc`). Symlinks
  within that scope are rejected. This includes the test runner itself and the
  documentation/catalog consumed by the basic-scope preflight.
- The stage must match the original hashes plus the separately hashed pinned
  historical overlay before execution. Origin and staged source maps are checked
  again after execution; additions, deletions, or modifications fail the run.
- Historical `verification/` files are copied for compatibility, but are **not**
  hashed source inputs or proof of current success. Generated outputs are excluded
  from input fingerprints. Previous `verification/runs/` directories are never
  copied into the stage. Tests' additional generated stage reports remain temporary;
  the aggregate claims only the full-suite process recorded in its retained log.
- The receipt binds the exact command, selected normal/sanitizer mode, return code,
  source maps, run identity, log SHA256, compiler and platform metadata. Matching
  structured start/end records are embedded in the log. Aggregation validates those
  bindings rather than maintaining an increasingly stale list of PASS strings.
- Compiler selection matches the shell runner (`CXX`, otherwise `g++-16`, otherwise
  `g++`) and is resolved to the executable used. Version, target triple, executable
  SHA256 before/after, OS/platform/architecture and Python version are observed.
  A bounded environment allowlist records compiler/test/sanitizer and include/link
  path settings. The full environment, unrelated variables and credentials are
  never serialized. `PYTHONOPTIMIZE` that would disable assertions is rejected.
- The hashed `tools/test.sh` defines compiler flags and test selection. Environment
  flags are recorded as observations, not as a claim that every child honors them.
  A nonzero suite exit or recognized ASan/UBSan error diagnostic fails the run even
  when a sanitizer was configured to return zero. The two runs can use different
  compilers/platforms; their observed metadata stays attached to each run.

## Scope and limitations

This is reproducible local provenance against accidental stale-source attribution,
not cryptographic remote attestation. Someone who deliberately rewrites both a
receipt and its corresponding log can forge unsigned local evidence. Before/after
checks cannot detect an input changed and restored between snapshots. External
libraries, OS/runtime contents, system headers, process environment not on the
allowlist, and undeclared files outside the input scope are not fully hermetic.

Success means the selected, hashed full suite exited successfully for both modes;
it is not proof that every algorithm has exhaustive coverage, online-judge
acceptance, universal correctness, or race freedom. ASan/UBSan is the sanitizer
scope. LeakSanitizer is not certified; `ASAN_OPTIONS=detect_leaks=0`, when necessary
for the execution environment, is recorded and must be disclosed with the result.

## Bounded regression check

```sh
python3 tests/verification_provenance.py
```

This runs small synthetic suites through the real capture code, tests valid pairing
and stale/changed/failed evidence rejection, verifies environment metadata and
historical-file preservation, Linux stack validation/capping, and the real basic-scope,
knowledge-taxonomy and report Python preflights in a staged copy. It does **not** run the full C++ algorithm suite or produce a
current-source full-suite manifest.

管线自身的负对照测试用 `python3 tests/verification_provenance.py` 在真实仓库单独执行，不嵌入暂存后的算法脚本：暂存区没有 Git 元数据，且故意失败的消毒器日志不能混入成功算法运行的日志。

The README is copied into the staged workspace and bound before/after execution,
including its knowledge-count assertions. Missing or symlinked README inputs are
rejected; editing the origin or staged README invalidates the receipt. The bounded
provenance tests now run basic scope, knowledge-taxonomy and report checks in a real
staged copy. These preflights do not certify a full algorithm-suite pass.

If a required input becomes missing, symlinked or unreadable during execution,
post-state capture records a null map plus an explicit error, and retains a failed
receipt/footer. Such evidence cannot be promoted to success by relabeling status.
