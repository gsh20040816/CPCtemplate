# Reproduce the targeted partition checks

The helper is an exact copy of the script used by both receipts. SHA-256: `79a3f96ad19e8eb646a102f88e73c1c26e79a06d6415fa79077a6aec073946a2`.

From the repository root:

```sh
mkdir -p build
cp verification/partition-knowledge-check.py build/partition-knowledge-check.py
python3 build/partition-knowledge-check.py --mode normal --root "$PWD" --boost-include /path/to/boost/include
python3 build/partition-knowledge-check.py --mode sanitizer --root "$PWD" --boost-include /path/to/boost/include
```

The recorded environment used GNU14.2 and build/deps/boost-1.83/usr/include. The fixed classic baseline commit must be available in Git. Exact source, staged baseline, compiler driver/frontend, Boost, helper, generated files and logs are fingerprinted in each receipt. Different inputs or environments create new evidence, not identical historical runs.

The three selected tests are partitions.cpp, partition_recurrence_applications.py and partition_knowledge.py. The unchanged application script additionally covers P5487 and compiles two independent reference programs with plain -O2 even in sanitizer mode; the receipt preserves that distinction. It does not imply a full-suite, online-judge, CI or LeakSanitizer result. Per-command output is embedded in JSON, with aggregate logs retained alongside it.
