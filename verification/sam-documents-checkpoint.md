# Document-frequency SAM and tree-substring applications

Base: 4147a69531004711a506e2eb7f4fff6457c142f0. Added vector SAMDocuments; existing228 components remain byte-identical. No CI inspection or maintenance.

The index counts distinct input document positions per endpos state, treats repeated documents separately, and defines empty-string frequency as document count including empty documents. It reuses Fenwick to deduplicate suffix-tree subtree markers and preserves recursive DFS. Threshold suffix lengths support CF204E interval totals. Constructor/query preconditions, reference lifetime, integer bounds and complexity are documented.

Official CF204E statement checked. Its complete application and a separate frequency-query API are usages259/260. CodeChef public problem API supplied TSUBSTR's formerly unavailable full statement; official editorial and tester source cross-checked. Usage261 handles vertex1's letter, arbitrary tree edge order, merged label paths, custom alphabets, LLONG_MAX ranks and the empty output line. TSUBSTR and CF204E remain contest applications, not non-contest template mappings.

Normal and ASan/UBSan each passed header/copied x assert/NDEBUG:9816 cases,3075111 checks per core form, seven semantic mutants rejected. Three complete forms each passed731 CF204E inputs,182 API inputs and207 TSUBSTR inputs. Five TSUBSTR driver mutants rejected by exact output. Deep native recursion,250000 tree vertices,50000 queries,100000 documents, repeated strings, clones and64-bit totals included. Core probes also compose SAMDocuments weights with SAMLex. Existing258 expanded usage programs unchanged; only3 new usages retested. No full-library rerun, online AC/rank or original judge resource acceptance claimed.

Integration checks passed: dependency closure, copy order, joint references, basic scope, source-backed report and math CSV. Candidate generation now supplies CodeChef URLs. All261 usage source hashes match local evidence; historical evidence remains immutable.

Reviewed35 physical PDF pages including new algorithms/drivers, both TOCs, complete cross-category dependency appendix, indices and infra. Methods stay intact at original font size. Total book731 pages (+7); strings69 (+17, including required dependency appendix and extra TOC page). Eight logs pass warning audit,1281 internal reference groups and16 external jumps resolve. Six unrelated PDFs restored byte-for-byte after page text/labels/destinations/link actions/font-set comparison.

Current inventory229 components/261 usages; component usage categories167 formal-example,50 application,12 API. Two kuangbin SAM source rows now local-tested, using prior constructor/query coverage plus both full applications. Global ledger621 pending/29 partial. Overall goal, remaining source mappings, recent contest/OI math coverage and online verification remain incomplete.

Detailed provenance is in sam-documents-*.json and tsubstr-*.json. Runtime implementation/probe/driver/snippet hashes checked against final success snapshots. Later TSUBSTR registration and documentation changes are explicitly separated from earlier document-frequency runs.
