# Open-issue rescan after 18fb1881

Read #1 #2 #3 #5 #7 #9 #11 #12 #13 #14 #15 #16 #19 on 2026-10-13. No newer human instruction arrived after the replies below. A start is unfinished only when a later comment does not close it.

| Issue | Last human instruction answered | Last start | Later close |
| --- | --- | --- | --- |
| #1 | Issue body: template ranks, STL style, composable templates, pbds/rope. pbds, gp_hash_table and rope were added in b7f3aba, 0d15bc3, e3b62a8. | 2026-10-12 09:39 incircle | 57a1118, then 待确认 ranks at 2026-10-13 07:21 |
| #2 | 2026-09-30: remove qpow, sort, and the basic Fenwick problem | none still open | 2026-10-02 08:05, commit 8b09b35 |
| #3 | Issue body: learn copyable ACL structure and list gaps | 2026-10-04 07:37 SA-IS | ef3e79e, then local timing 31c9515c at 2026-10-13 07:55 |
| #5 | Issue body: classify by the fixed OI Wiki navigation | 2026-10-13 07:49 application notes | f5c65254, then wavelet 待确认 at 07:50 |
| #7 | Same classification request. Recent batch starts were posted on #5; completions were posted here through 07:50 | 2026-10-04 01:35 knowledge notes | later completions through f5c65254 and the same wavelet 待确认 |
| #9 | pbds priority_queue and infra page jumps | 2026-10-02 08:06 infra STL notes | c3cc49d at 11:55 |
| #11 | Attached algorithm PDF, audited in place | 2026-10-13 07:06 geometry printout | 93c67afa, then coverage sync 25b80b22 at 07:21 |
| #12 | A usage program beside each template | 2026-10-13 07:17 maintainL/maintainR | 8d1466dc at 07:19 |
| #13 | Human reply 2026-09-30 08:12: mark both page and section | 2026-09-30 08:11 | 1dbf3fc at 2026-10-02 08:27 |
| #14 | Checklist; every box is checked | 2026-10-12 04:27 Mo and circle union | 6efd7d2 at 04:42 |
| #15 | Checklist; every box is checked. Two adjacent starts on 2026-10-11 03:34 and 03:46 were closed by 629f71a and 0bf0dd6 | 2026-10-11 04:19 Tutte | 450aa4a and the LOJ3163 AC note at 05:09 |
| #16 | Record submitted times and a SOTA floor | 2026-10-12 16:41 NTT/Newton timing | c372253, then 待确认 ranks at 2026-10-13 07:21 |
| #19 | Dinic scaling comments | 2026-10-12 13:48 | 7b0c631 at 14:04 |

## 待确认

- #1 and #16: public OJ rank totals and the floor(pass-count/100) SOTA. Pages that 403 or have no public total stay 待核验. No rank was invented.
- #5 and #7: the wavelet-matrix section remains in `docs/mathematics.tex`. Pinned navigation bc070e827180 has no wavelet leaf, and `ds/dividing.md` is a different structure.
- #3: SA-IS has a local timing only (`docs/SAIS.md`, `tests/sais_timing.cpp`). Its online AC, and the ACL review's other unsent submissions (lazy segment tree, slope, exact integer convolution, dynamic mod), were not submitted in this run.

`python3 tests/knowledge_taxonomy.py` passed at 102 classified sections. `python3 tests/acl_review_consistency.py` passed after the timing note. No carray template was added.
