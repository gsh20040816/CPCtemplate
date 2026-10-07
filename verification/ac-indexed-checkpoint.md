# AC indexed inputs and depth checkpoint

Base: `efe47951841f8fa4d4d2c8cae265ab3d8a34e7e0`.

Extended the existing AhoCorasick core with explicit-offset string/vector<int> insertion and counting, initialized Trie depths and empty-pattern support. Original one-argument string calls remain. Root count deliberately changes from text length to text length+1; subtract1 for the former scan-count meaning. Nonempty counts remain unchanged. WIDA06B/06C now local-tested; source root numbering and06B's uninitialized depth/ignored offset are explicitly adapted, not copied.

Normal and ASan/UBSan: four indexed core forms each17,560 cases/1,282,271 checks, four semantic mutants rejected; integer extreme offsets, empty cases, independent prefix/longest-suffix oracle and million-node chain. Three complete forms of each new API usage265/266 each160 inputs. The new minimal-copy harness initially omitted iomanip; it was corrected after other live runners finished and fully rerun in both modes.

Regressed original AC: four forms each26,770 cases/2,692,012 checks, five mutants, P5357/P3808 each185 inputs per full form. Regressed weighted/dynamic AC: four forms each25,285 cases/462,270 checks, six mutants, API160 andCF710F126 inputs per full form plus incremental flush testing and missing-flush negative control. Shortest-suffix helper passed ordinary and sanitizer tests. Relevant runtime source hashes match final reports.

All20 affected prior expanded usage programs plus2 new programs reran ordinary/sanitizer cases and refreshed proof hashes.244 prior programs and230 other components are unchanged. This is scoped incremental verification, not a whole-library rerun or new online AC/rank.

After fixing a newly exposed short-function page split,24 selected physical pages were inspected. Original fonts retained;1301 internal reference groups and16 external jumps resolve. Five unrelated PDFs semantically compared and restored. Total739 pages (+3), strings77 (+3), infra12 with updated links.

Current231 components/266 usages; source ledger616 pending/29 partial. Broader original requirements remain active. No GitHub CI inspection or maintenance.

Evidence: `ac-indexed-{normal,sanitizer,regression-source-normal,regression-source-sanitizer,regression-weighted-normal,regression-weighted-sanitizer,sources,copy,layout,checkpoint}.json`.
