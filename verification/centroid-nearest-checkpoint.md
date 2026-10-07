# CentroidNearest checkpoint — 2026-10-07

Base: d6caf14 (following imported ExactCover bundle and MinimumCover). This batch adds one component and QTREE5 application, not full-library completion.

- Four core forms per mode (header/copied × assert/NDEBUG), each **4579 cases / 7773800 checks**. Every labelled tree through n=6, all active subsets, unit/zero/mixed weights; random weights, copies/rebuilds, equal-distance deletion, legal LLONG_MAX answers and overflowing centroid detours. Three 100000-vertex shapes with recursive DFS and enlarged native stack.
- Three complete QTREE5 forms per mode (original driver / expanded / minimal-standard-header copy), each **184 inputs**, including official sample, 180 BFS-oracle random inputs and chain/star/binary shapes with N=Q=100000. All six semantic mutants rejected; unchecked addition is caught by UBSan in sanitizer mode.
- Both normal and ASan/UBSan passed; LeakSanitizer disabled. No fresh whole-library runtime/sanitizer claim. Source snapshots remained identical during each targeted run, and final core/test/driver/printed-source hashes are checked against these receipts.
- Full copy syntax audit: **237 standard +6 explicit GNU forms pass**; examples229/230 remain rejected on macOS arm64 by their long-double precision guards. This is not a whole-audit pass and no guard was bypassed.
- PDF visual review covered **19 physical pages**. Omnibus and graphs gain four pages; infra updates two graph page references. Original font sets preserved. Other five PDFs restored byte-for-byte only after equal page text, labels, named destination pages, link actions and font sets; small coordinate equality is explicitly not claimed. All eight final logs have no warnings; 1218 dependency reference groups and16 external jumps resolve.
- QTREE5 is competition-derived (official source says modified from ZJOI07), so usage245 is an **application**, not formal standalone-template coverage. kuangbin's original LCT/multiset implementation is replaced by fixed-topology centroid decomposition. Original prose says farthest, but original code and official statement query minimum distance. No online AC or speed-rank claim.

Current inventory: **219 components,245 usages**;161 formal local,46 application-only,12 API-only;641 upstream topics remain pending mapping. Complete objective remains active. GitHub CI was not inspected or maintained.
