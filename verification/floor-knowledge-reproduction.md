# Reproduce the targeted floor-knowledge checks

`floor-knowledge-check.py` in this directory is a byte-for-byte copy of the helper used by the two receipts. Its SHA-256 is `c44ce2ce3e2269fab39aaab925697cafe03cf1de5db32d4f3c327ee20bff2aa8`.

From the repository root, restore its recorded location and run either mode:

```sh
cp verification/floor-knowledge-check.py build/floor-knowledge-check.py
python3 build/floor-knowledge-check.py --mode normal --root "$PWD" --boost-include /path/to/boost/include
python3 build/floor-knowledge-check.py --mode sanitizer --root "$PWD" --boost-include /path/to/boost/include
```

The original environment used GNU 14.2 and `build/deps/boost-1.83/usr/include`. The fixed baseline commit must be present in the Git object database. Exact source, compiler driver/frontend and Boost fingerprints are recorded in each receipt; a different environment produces its own new evidence, not an identical historical run.

This helper runs four existing C++ tests and the compact P5170 application test in a baseline-staged workspace. Its schema is `cpc-targeted-floor-knowledge-v1`, deliberately distinct from a full-suite receipt. Per-command output is embedded in the JSON as well as retained in the recorded logs. No online AC, CI, full-suite or LeakSanitizer result is implied.
