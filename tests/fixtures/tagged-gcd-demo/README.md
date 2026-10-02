# Custom tagged-GCD API protocol

This is a custom API demonstration, not an online-judge problem. The sample is
custom, with no official-sample or AC claim. Decimal values are unsigned long
long (0 through 18446744073709551615 on the tested toolchain); tags are 0 or 1.

One dataset: `n q`, then n lines `value tag`, then q commands:

- `I k v t`: insert after the first k entries; k=0 and k=size are valid
- `E l r`: erase the valid nonempty 1-based inclusive range [l,r]
- `S k v`: replace the value at valid 1-based k, retaining its tag
- `T k`: toggle the single tag at valid 1-based k
- `Q l r t`: print the selected tag's GCD, or `NONE` if absent

A present all-zero group returns `0`. Every input is valid; signed mathematical
values, invalid-position recovery and reversal are outside this protocol.
Empty construction and deletion to empty are allowed; insert before any further
range/point operation.

Chosen envelope: 0 <= n <= 200000, 0 <= q <= 100000, peak live size <= 300000.
These are protocol choices, not official constraints or measured hard limits.
The exact 300000-node driver case spends all 100000 commands inserting, so is
only a no-output operation/resource smoke. The core harness separately checks
values at that peak. Two other maximum-envelope cases have observable queries.

`tests/tagged_gcd_demo.py` checks 134 datasets for each of the actual direct,
registered-expanded, and generated-printed forms, each with 399572 commands and
83267 query lines. Small and random cases use an independent Python list and
math.gcd; large cases use exact scalar identities. `tagged_gcd_demo_core.cpp`
separately checks build replacement and rebuild-to-empty, 128 deterministic
node-recycling rounds, and 300000 live nodes: 7 builds and 523 query assertions.
It leaves the existing staged historical-baseline tests intact.

Run with `python3 tests/tagged_gcd_demo.py --mode normal` or `--mode sanitizer`.
`--mode both` runs both. Default output is a fresh directory under `build/`;
`--report` selects a report below `build/` or `verification/`. Python -O is rejected.
Sanitizer runs retain compiler-default PIE and ASan quarantine, with LSan off.

Tree paths are expected logarithmic under randomized priorities, with GCD cost
per pull and deleted-node traversal cost for erase. Build makes O(n) GCD calls.
Worst-case tree height and recursive depth can be linear; default fixed seeding
and these finite cases do not establish universal balance or adversarial bounds.
