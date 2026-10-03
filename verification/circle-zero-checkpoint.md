# Floating circle no-tolerance checkpoint

Two existing functions now accept explicit eps=0. Their old positive-epsilon paths are preserved, including the documented default near-tangent incompatibility. New complete floating AOJ usages 229/230 do not call the integer geometry helpers. The bounded integral-domain guarantee requires binary long double with at least 64 significant bits, normal nearest rounding and no unsafe optimization. It is not arbitrary-real robust geometry.

Final dedicated normal and ASan/UBSan reports each cover 3508 line and 3766 circle cases in complete-header and minimal-header forms. The corpus includes non-AOJ point-circle/no-intersection/degenerate extensions, explicitly separated from valid complete-program inputs. Core measured maximum absolute error is below 1.443e-15. Per mode, each of direct/expanded/copied program forms executes 156 D inputs with 1155 queries and 155 E inputs; maximum printed-coordinate error is below 5e-13. Ten numeric/kind/count/order/tangent-duplication negative controls pass. Fast-math, 53-bit long-double compile probes, and non-nearest rounding are rejected. The Python harness refuses optimized execution.

The parent independently checked current source maps, compiler/frontend, actual input/output/diagnostic files and compiled binaries. Source-bound reports are circle-zero-normal.json and circle-zero-sanitizer.json. The old default-contract diagnostic still returns its expected incompatibility result, with no falsely upgraded pass.

Both new actual printed programs passed canonical execution in both modes. Existing 228 program hashes remain unchanged; this is not a fresh runtime run of all 230. A fresh all 230 copied-context syntax audit passed 224 standard contexts plus 6 explicitly GNU-dependent contexts, zero unresolved. Syntax evidence does not certify runtime behavior.

Official public AOJ D/E data: 12+25 cases per mode, 74 executions total, passed the local numeric comparator. Independent validation reran their recorded binaries and matched input, expected-output and actual-output hashes. This is neither the official checker nor online AC.

Targeted compatibility tests real_components, integer_components, circle_precision and property passed both modes. The latter two used the normal pinned historical-baseline staging. No new complete tools/test.sh run, CI query or LeakSanitizer certification is claimed.

PDFs: 14 actual pages inspected, existing fonts retained, two complete main programs and coherent circle-function continuation. Six unaffected PDF files retain their prior bytes after page text, destination and annotation equality checks. 1152 dependency name/page/section groups and 16 cross-volume links resolve. Coverage is 208 components, 230 uses: 156 formal-template, 43 application-only, 8 API-only, 1 pending (Mod64). The 24 mapped knowledge sections remain a separate count; the new geometry explanation is not counted as an additional algorithm.

Reproduce dedicated tests from repository root with CXX set to GNU C++ 14, ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 and UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1:

- python3 tests/circle_zero_mode.py
- python3 tests/circle_zero_mode.py --sanitizer
- python3 tests/usage_examples.py --only example-229 example-230
- python3 tools/audit_copy_context.py --compiler /usr/bin/x86_64-linux-gnu-g++-14 --output-dir build/circle-zero-copy-fresh --jobs 4

Fresh runs use new output directories; do not overwrite earlier evidence or transfer this checkpoint to altered sources. General floating classification and remaining knowledge/online evidence gaps remain open.
