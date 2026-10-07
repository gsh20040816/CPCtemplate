# SAM construction checkpoint

Base: ad25bb0c9b9d95da344e72328f8bb32a47f704d3. The exact-cover bundle import 765416e512703cf046959b69ecf94e02bb262827 is already an ancestor. Remote main matched base when fetched. No CI work performed.

Added vector OnlineSAM arbitrary-parent extension and GeneralSAM pre-build Trie-edge registration. Existing longest-state handles stay valid; online queries share the accumulated language, without persistence or document-frequency counting. Arbitrary insertion order can be quadratic: 2n+1 operations cause n(n+1)/2 redirects. The direct Trie BFS alternative remains preferred for known input trees.

Normal and ASan/UBSan: four core forms each 39609 cases and 3079185 checks; seven semantic mutants rejected. Three complete program forms each ran usage256/257/258/132 on 101/101/168/168 inputs. Maximum P6139 sets include one million characters and 400000 documents. Previous SAM queries and original GeneralSAM regression both rerun. Six affected complete usages retested; 226 old components and 252 old expanded usages unchanged. This is incremental evidence, not a whole-library rerun or online AC.

Dependency closure, copy order, joint usage references, scope, report provenance and mathematics CSV checks pass. Historical GeneralSAM evidence stays immutable; the report regression now checks current construction run hashes and success in both modes.

Total book and string volume each grow four pages. Reviewed 25 physical pages across those books and infra, including code, TOCs, usages, boundaries and index entries. OnlineSAM extend stays on one page at the existing font size. Eight final LaTeX logs have no audited warnings; 1258 internal reference groups and 16 external jumps resolve. Six unrelated PDFs restored byte-for-byte only after semantic comparison.

Current inventory: 228 components, 258 usages (167 formal-template examples, 49 applications, 12 API examples). Three audited source rows closed as local-tested; two parent/application rows remain partial. Global pending621/partial31. CF204E document-frequency application and TSUBSTR official full driver/contract remain open. Full overall goal remains active.

Detailed source, runtime, copied-code, layout and source-hash evidence is in the adjacent sam-build-*.json reports. Browser unlock and online AC/ranking remain unresolved; no new verdict claimed.
