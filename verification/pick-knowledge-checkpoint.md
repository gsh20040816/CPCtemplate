# Pick theorem and lattice-polygon usage checkpoint

Migrated only the two Pick/gcd formula lines and Pick index from the mixed legacy numerical/geometry section. A byte-hashed fixture from1c1146887ef154ac17a8ad0cf627018cfa4bf0c2 guards the exact remainder; its source path and commit are asserted. The old mixed section, sorting/precision/integration/search guidance and70 legacy sections remain. A new explicit knowledge-pick label is owned by geometry/pick.md, not the mathematics volume.

The proof explains boundary gcd without duplicated endpoints, unimodular normalization of empty-including-boundary lattice triangles, conforming integer refinement and Euler counting. A shared-edge insertion refines both adjacent triangles. The hole extension is limited to one connected region with pairwise disjoint, nontouching, nonnested removed regions strictly inside the outer boundary. Boundary and interior conventions, the +h correction, noninteger/self-intersecting/degenerate exclusions and integer widths are explicit. Existing IntegerPlane and polygon_area2 are unchanged.

## Final source-bound verification

Normal and ASan/UBSan receipts bind the same1,385 source files, unchanged before/after. No new full-suite result is claimed by these targeted reports.

-1,428 simple polygons in four bulk forms per mode, header/minimal-copy × assertions/NDEBUG. The bulk harness wraps the exact registered main body in a query loop; it is not misrepresented as the original single-case formal protocol
- Independent expected counts enumerate bounding-box lattice points and classify boundary via exact cross/bounds checks, interior via Fraction ray parity. The oracle does not use gcd, Pick or polygon_contains. Small3×3-grid simple cycles through five vertices, reversed/cyclic forms, concave L/U shapes, collinear boundary vertices and unimodular/translated cases are covered
- Five analytic large/domain cases include clockwise and counterclockwise squares at1e9 and1e12 plus a100,000-vertex square boundary with distinct collinear vertices. The1e12 cases exercise the library contract and counts exceeding signed64; they are not official CSES inputs
-64 distinct selected formal-domain cases per mode run through three unchanged complete program forms: direct driver, printed expansion and minimal copy. All include the official sample, both1e9-square orientations and the maximum-size boundary; output has exactly interior then boundary counts
-48 hole-region cases compare a Python formula model to independent enumeration, with translated/reversed rings and one/two holes. Fixture-domain checks reject nested and touching holes. These are Python mathematical checks, not a new C++ holes API or sanitizer coverage of Python
- Domain counterexamples include primitive-edge triangles with interior points, a zero-area bow-tie, collinear degeneracy and a self-crossing polygon whose formula still returns nonnegative integral29/24. Scalar parity/nonnegativity is not a simplicity validator
- Seven NDEBUG mutants are independently rejected in each mode: missing orientation normalization, confusing area with doubled area, duplicated endpoints, omitted Euler correction, wrong boundary sign, narrowed area and narrowed output. All exit without sanitizer diagnostics; rejection is by output checks
- Central example238 passes normal and ASan/UBSan; prior237 usage records/program fingerprints are unchanged. No rerun of every old application is claimed
- Fresh238-program copy audit:232 standard-header successes plus six documented GNU-header successes, stable inputs and zero unresolved. Syntax/copyability is separate from runtime correctness

ASan/UBSan cover the compiled single-ring combination and existing area routine. LSan is disabled. CSES2193’s official simple-polygon domain is n≤100000 and coordinates within±1e9; the sample is6 8. No new online AC, leaderboard position, official hidden tests or unqualified upstream-page completion is claimed. OI Wiki’s returned pinned text is hashed, explicitly not an independently reproduced Git blob; its broad nonsimple wording is not copied as an unrestricted contract.

## Printed artifacts and counts

Actual final file pages inspected: total book564,577,578,631 and geometry25,38,39,66. The32-line complete usage stays together; theorem proof and hole/domain/width conditions have a deliberate two-page break. The old mixed section no longer repeats Pick but retains its other advice. Font sets remain unchanged; six unrelated PDFs retain their original bytes after full text, destination-property and annotation equivalence. Eight final logs have no warnings, page anchors are contiguous,1,198 dependency groups and16 infra jumps resolve.

Counts:213 components/238 uses;159 formal-template,43 application-only,11 API-only, no missing direct use. This batch adds an application, not a new algorithm or formal-template component. Classified knowledge is30 sections across17 sources: mathematics26, graph3, geometry1;70 legacy sections remain. Redundant stale counts were removed from the free-text scope note so the structured registration stays authoritative.

The historical section fixture intentionally retains its original terminal blank separator. Git’s blank-at-EOF warning for that one byte-preservation fixture is expected; whitespace validation excludes that exact fixture only. Its recorded SHA256 and exact reconstructed section remain checked, while all other staged files pass the standard whitespace check.
