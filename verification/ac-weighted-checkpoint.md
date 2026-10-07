# Weighted and dynamic AC checkpoint

Base: `f4e1d028f50e445e95ffcdb26c9459dd30f8e394`.

Added `ACWeighted`: owned static AC, signed terminal weights propagated over failure links, O(text) aggregate queries. Added `DynamicAC`: binary grouping of signed update records, rebuilding on carries; complete online CF710F application. Usage263 is an API demonstration; usage264 is a competition application, not a noncontest template problem.

Pinned WIDA06A is now local-tested. Nonempty weighted matching agrees with the source; empty patterns deliberately count all boundaries, and subtracting `sum[0]` reproduces the original scan-only behavior. WIDA06B/06C indexed input/depth gaps remain partial. See `docs/AC-WEIGHTED.md` for complexity, overflow, ownership and update-history space contracts.

Normal and ASan/UBSan: header/copied forms, each with assert/NDEBUG, each 25,285 cases and 462,270 checks. Independent literal occurrence and suffix-state weight oracles. Six semantic mutants rejected by the oracle in each mode. Three complete forms each pass160 API inputs and126 legal CF710F inputs, including both official examples and maximum operation/total-length cases. Incremental pipe testing withholds later input until answers arrive; a missing-flush mutant is rejected. This verifies local online behavior, not an online judge verdict.

All229 prior components and262 prior expanded usages are unchanged; new runtime source/probe/driver/snippet hashes match both completed runner snapshots. No full-library rerun, official resource acceptance or new online AC/ranking claim.

Both new structs fit whole pages without reducing fonts. Reviewed17 selected physical pages; all eight PDFs pass structural audits,1297 internal reference groups and16 external jumps resolve. Restored five unrelated PDFs after semantic equivalence checks. Total736 pages (+4), strings74 (+4), infra12 (updated suffix-array reference).

Current231 components/264 usages:167 components with locally checked formal examples,51 with applications only,13 with API examples only. Source ledger616 pending/31 partial. Broader requirements remain in progress. CI was not inspected or maintained.

Machine evidence: `ac-weighted-{normal,sanitizer,sources,copy,layout,checkpoint}.json`.
