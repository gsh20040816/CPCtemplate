# Custom IntegerGeometry3D API demonstration

This is a chosen API protocol and custom sample, not an official online-judge
problem. See `contract.json` for the complete domain and exact output meanings.
No claim of SPOJ TETRAHED acceptance or official full-data execution is made.

`sample.in` / `sample.out` exercise positive and negative orientation, a coplanar
noncollinear triple with a segment-interior point, a singleton segment, an
outside collinear point, and an orientation beyond signed 64-bit range.

Run from repository root:

```
python3 tests/integer_3d_demo.py --mode normal --report build/integer-3d-next/normal.json
python3 tests/integer_3d_demo.py --mode sanitizer --report build/integer-3d-next/sanitizer.json
```

Each mode checks the complete driver, registered expanded program, and actual
generated printed snippet with only the declared IntegerGeometry3D definition.
A separate core program directly exposes diff/cross/dot on point differences.
All four forms run seven datasets / 215,542 queries, including exhaustive ordered
unit and extreme-cube quadruples (4,096 each), seeded random and duplicate cases,
degeneracies and endpoints, translated/scaled permutations, large nearly singular
determinant-one permutations, Q=0 and Q=200000. Maximum-Q expected values cache a
small exact oracle pool; this is finite local correctness evidence, not a general
performance guarantee. Python arbitrary-precision integers supply independent
4x4 permutation determinants, pairwise-minor collinearity and coordinate-box
segment tests, plus primitive cross minors and a polarization-identity dot oracle.

The exact driver printing lambda is additionally extracted into a printer-only
program, testing 0, +/-1, signed int128 minimum/maximum and +/-8e27. Those printer
checks do not widen the point-coordinate domain or promise safe arbitrary Vector
operations. Sanitizers retain compiler-default PIE and ASan-default quarantine;
LeakSanitizer is disabled. No sanitizer failure is retried or suppressed.

The runner is import-safe, rejects Python -O, uses compiler_config, allocates a
fresh build directory, retains failure artifacts, and checks before/after hashes
for transitive source headers, selected registration/catalog, fixture files,
printed snippet, runner/generator/compiler configuration and compiler driver/frontend.
