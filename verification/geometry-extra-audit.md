# Integer closest pair and Minkowski sum audit

The compact and classic implementations are unchanged from commit 9a81caf.
`tests/geometry_extra_audit.cpp` includes the classic header first and tests both APIs.

- Closest pair: independent arbitrary-precision squared-distance enumeration;
  empty/singleton inputs, duplicate points, opposite corners at coordinates
  ±10^12, and 2,000 random clouds with small and large coordinates.
- Minkowski sum: independent arbitrary-precision gift wrapping of all pair sums,
  exact vertex-set comparison, strict cyclic convexity, and comparison of both
  styles. Includes empty hulls, points, segments, parallel edges, and three
  cyclic starting positions for each random case.
- Scale cases: 200,000 shuffled collinear points with known nearest squared
  distance 9, followed by a duplicate with answer 0; a 40,001-vertex parabola
  hull added to itself, checked against exactly twice every input vertex.

Closest pair uses recursive divide and conquer, O(n log n) time and O(n)
auxiliary space. It returns nullopt when fewer than two points exist.

Minkowski inputs must be strict counterclockwise convex hulls (or empty,
point, segment hulls), with no repeated closing vertex. Cyclic rotation is
allowed; clockwise order and redundant collinear boundary points are outside
its contract. Input coordinates and every coordinate sum must be within
±10^12. The output has no repeated closing vertex. Nondegenerate merging
is O(n+m); the point/segment fallback sorts O(n+m) candidates.

These are local oracle and ASan/UBSan checks, not new online acceptance evidence.
