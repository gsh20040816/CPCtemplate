# AC source audit and presence counting checkpoint

Base: `cc77c693cd9780f536d9fd4c7df58981b8968a16`.

Added complete P3808 usage 262, counting input pattern IDs present in the text; duplicate strings count separately. Existing P5357 usage 70 was independently regressed. All 229 algorithm components and 261 existing expanded usage programs remain unchanged; see `ac-source-copy.json`.

Audited five pinned WIDA/kuangbin source interfaces. Two presence-counting rows are now local-tested; three extension rows remain partial. Missing weighted O(text) query, indexed/custom-offset inputs, depth and empty-pattern contracts are explicitly recorded in `docs/AC-SOURCE-AUDIT.md`. No online AC, ranking, original HDU resource acceptance or whole-library rerun is claimed.

Normal and ASan/UBSan runs passed: four core forms each 26,770 cases and 2,692,012 checks; three complete forms per problem each 185 inputs, including maximum legal sizes. Independent longest-suffix transition/failure and literal matching oracles reject five semantic mutants in each mode. Runtime source snapshots and usage proof hashes were checked again after documentation changes.

PDFs rebuilt with the existing fonts. AC now breaks before build(), preserving whole build/count methods. Visually inspected 16 selected physical pages across the total book, strings volume and infra index. All eight PDFs pass structural audits; 1,283 internal reference groups and 16 external jumps resolve correctly. Five unrelated PDFs were semantically compared and restored to original bytes. Total book: 732 pages; strings: 70; infra: 12.

Current library: 229 components and 262 usages; upstream ledger: 616 pending and 32 partial. Broader coverage and online verification remain in progress. GitHub CI was not inspected or maintained.

Machine evidence: `ac-source-{normal,sanitizer,sources,copy,layout,checkpoint}.json`.
