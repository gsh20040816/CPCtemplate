# 已归档提交的运行时间

对应 [issue #16](https://github.com/gsh20040816/CPCtemplate/issues/16)。本表合并中央登记与批次线上回执，并逐项绑定提交源码哈希；覆盖已归档记录，不声称已遍历整个账号的所有历史提交。退役 classic 只作为历史记录保留，不重新维护第二套码风。

旧 `time_ms` 字段的含义不一致，原样列入“原始登记”，不能直接与单点或总计比较。只有逐测试点列表或明确字段支持的值才进入相应列；显示为秒的舍入总时长不转换为精确毫秒。等待评测和拒绝提交不算 AC。

已审查的候选及差距见 [P4980 核查](RUNTIME-P4980.md)。候选未满足排名覆盖核验条件，仍不计入正式 SOTA。

基准全部待核验：需记录同题、语言/优化、计时口径、测评时间、全体通过提交数量与所选名次，并检查基准源码；排除打表等取巧提交。若改用同算法基准，须说明原因。按用户去重的最快榜不是全体通过提交排名。基准未知时不计算倍数，也不据此宣布性能达标。

当前 113 项，111 条 AC；46 项有明确最慢单点，0 项已完成 SOTA 核验。

| 题目/记录 | 状态、码风 | 原始登记 | 最慢单点 ms | 逐点合计 ms | 明确登记总计 ms | SOTA |
|---|---|---|---:|---:|---:|---|
| CF321E（无记录） | submission_rejected | — | — | — | — | 待核验 |
| [Library Checker associative_array](https://judge.yosupo.jp/submission/401867) | Accepted, compact | time_ms=309 | — | — | — | 待核验 |
| [Library Checker ordered_set](https://judge.yosupo.jp/submission/401869) | Accepted, compact | time_ms=605 | — | — | — | 待核验 |
| [Library Checker persistent_queue](https://judge.yosupo.jp/submission/401871) | Accepted, compact | time_ms=942 | — | — | — | 待核验 |
| [Library Checker point_set_range_composite](https://judge.yosupo.jp/submission/402090) | Accepted, compact | time_ms=247 | — | — | — | 待核验 |
| [Library Checker predecessor_problem](https://judge.yosupo.jp/submission/402089) | Accepted, compact | time_ms=383 | — | — | — | 待核验 |
| [Luogu P1429](https://www.luogu.com.cn/record/297602650) | Accepted, compact | time_display=350ms | 75 | — | — | 待核验 |
| [Luogu P1429](https://www.luogu.com.cn/record/297603238) | Accepted, classic | time_display=346ms | 75 | — | — | 待核验 |
| [Luogu P1446](https://www.luogu.com.cn/record/302212973) | Accepted, compact | time_ms=5 | 5 | 55 | 55 | 待核验 |
| [Luogu P1484](https://www.luogu.com.cn/record/302209955) | Accepted, compact | time_ms=27 | 27 | 124 | 124 | 待核验 |
| [Luogu P1495](https://www.luogu.com.cn/record/297521594) | Accepted, compact | time_ms=44 | — | — | — | 待核验 |
| [Luogu P1495](https://www.luogu.com.cn/record/297521658) | Accepted, classic | time_ms=44 | — | — | — | 待核验 |
| [Luogu P1742](https://www.luogu.com.cn/record/297608403) | Accepted, compact | time_display=177ms | 52 | — | — | 待核验 |
| [Luogu P1742](https://www.luogu.com.cn/record/297608801) | Accepted, classic | time_display=192ms | 49 | — | — | 待核验 |
| [Luogu P1903](https://www.luogu.com.cn/record/297653743) | Accepted, compact | time_ms=546 | — | — | — | 待核验 |
| [Luogu P2147](https://www.luogu.com.cn/record/301882512) | Accepted, compact | time_ms=202 | 202 | 1100 | 1100 | 待核验 |
| [Luogu P2365](https://www.luogu.com.cn/record/302209623) | Accepted, compact | time_ms=4 | 4 | 44 | 44 | 待核验 |
| [Luogu P2731](https://www.luogu.com.cn/record/299974727) | Accepted, compact | time_ms=5 | — | — | 38 | 待核验 |
| [Luogu P2921](https://www.luogu.com.cn/record/299973954) | Accepted, compact | time_ms=25 | — | — | 155 | 待核验 |
| [Luogu P3199](https://www.luogu.com.cn/record/302334598) | Accepted, compact | displayed_total_time=10.48s; max_case_time_display=1.92s | — | — | — | 待核验 |
| [Luogu P3367](https://www.luogu.com.cn/record/297668102) | Accepted, compact | time_ms=196 | — | — | — | 待核验 |
| [Luogu P3369](https://www.luogu.com.cn/record/297515150) | Accepted, compact | time_ms=243 | — | — | — | 待核验 |
| [Luogu P3369](https://www.luogu.com.cn/record/297520192) | Accepted, compact | time_ms=240 | — | — | — | 待核验 |
| [Luogu P3369](https://www.luogu.com.cn/record/297520197) | Accepted, classic | time_ms=246 | — | — | — | 待核验 |
| [Luogu P3369](https://www.luogu.com.cn/record/297520203) | Accepted, classic | time_ms=275 | — | — | — | 待核验 |
| [Luogu P3373](https://www.luogu.com.cn/record/297518952) | Accepted, compact | time_ms=1180 | — | — | — | 待核验 |
| [Luogu P3376](https://www.luogu.com.cn/record/297501480) | Accepted, compact | time_ms=76 | — | — | — | 待核验 |
| [Luogu P3376](https://www.luogu.com.cn/record/297502364) | Accepted, classic | time_ms=79 | — | — | — | 待核验 |
| [Luogu P3379](https://www.luogu.com.cn/record/297521009) | Accepted, compact | time_ms=2330 | — | — | — | 待核验 |
| [Luogu P3384](https://www.luogu.com.cn/record/297520172) | Accepted, compact | time_ms=1330 | — | — | — | 待核验 |
| [Luogu P3384](https://www.luogu.com.cn/record/297520179) | Accepted, classic | time_ms=1440 | — | — | — | 待核验 |
| [Luogu P3391](https://www.luogu.com.cn/record/297520211) | Accepted, compact | time_ms=613 | — | — | — | 待核验 |
| [Luogu P3391](https://www.luogu.com.cn/record/297520217) | Accepted, classic | time_ms=592 | — | — | — | 待核验 |
| [Luogu P3398](https://www.luogu.com.cn/record/299972443) | Accepted, compact | time_ms=134 | — | — | 516 | 待核验 |
| [Luogu P3690](https://www.luogu.com.cn/record/297512741) | Accepted, compact | time_ms=755 | — | — | — | 待核验 |
| [Luogu P3690](https://www.luogu.com.cn/record/297513273) | Accepted, classic | time_ms=814 | — | — | — | 待核验 |
| [Luogu P3806](https://www.luogu.com.cn/record/297519137) | Accepted, compact | time_ms=107 | — | — | — | 待核验 |
| [Luogu P3806](https://www.luogu.com.cn/record/297519170) | Accepted, classic | time_ms=109 | — | — | — | 待核验 |
| [Luogu P3807](https://www.luogu.com.cn/record/297556209) | Accepted, compact | time_ms=301 | — | — | — | 待核验 |
| [Luogu P3807](https://www.luogu.com.cn/record/297556596) | Accepted, classic | time_ms=286 | — | — | — | 待核验 |
| [Luogu P3811](https://www.luogu.com.cn/record/297563298) | Accepted, compact | time_ms=387 | 221 | — | — | 待核验 |
| [Luogu P3811](https://www.luogu.com.cn/record/297563503) | Accepted, classic | time_ms=385 | 219 | — | — | 待核验 |
| [Luogu P3834](https://www.luogu.com.cn/record/297520290) | Accepted, compact | time_ms=2895 | — | — | — | 待核验 |
| [Luogu P3834](https://www.luogu.com.cn/record/297520299) | Accepted, classic | time_ms=2905 | — | — | — | 待核验 |
| [Luogu P3919](https://www.luogu.com.cn/record/297520221) | Accepted, compact | time_ms=3130 | — | — | — | 待核验 |
| [Luogu P3919](https://www.luogu.com.cn/record/297520224) | Accepted, classic | time_ms=5180 | — | — | — | 待核验 |
| [Luogu P4174](https://www.luogu.com.cn/record/297520300) | Accepted, compact | time_ms=212 | — | — | — | 待核验 |
| [Luogu P4174](https://www.luogu.com.cn/record/297520304) | Accepted, classic | time_ms=196 | — | — | — | 待核验 |
| [Luogu P4195](https://www.luogu.com.cn/record/297520101) | Accepted, compact | time_ms=2080 | — | — | — | 待核验 |
| [Luogu P4195](https://www.luogu.com.cn/record/297520104) | Accepted, classic | time_ms=2320 | — | — | — | 待核验 |
| [Luogu P4245](https://www.luogu.com.cn/record/301858590) | Accepted, compact | time_ms=254 | 254 | 2052 | 2050 | 待核验 |
| [Luogu P4717](https://www.luogu.com.cn/record/297630491) | Accepted, compact | time_display=425ms | 84 | — | — | 待核验 |
| [Luogu P4717](https://www.luogu.com.cn/record/297630911) | Accepted, classic | time_display=420ms | 81 | — | — | 待核验 |
| [Luogu P4718](https://www.luogu.com.cn/record/297569299) | Accepted, compact | time_display=5.19s; max_case_time_display=2.11s | — | — | — | 待核验 |
| [Luogu P4718](https://www.luogu.com.cn/record/297569935) | Accepted, classic | time_display=5.21s; max_case_time_display=2.12s | — | — | — | 待核验 |
| [Luogu P4720](https://www.luogu.com.cn/record/297520142) | Accepted, compact | time_ms=61 | — | — | — | 待核验 |
| [Luogu P4720](https://www.luogu.com.cn/record/297520151) | Accepted, classic | time_ms=55 | — | — | — | 待核验 |
| [Luogu P4723](https://www.luogu.com.cn/record/297628790) | Accepted, compact | time_display=4.53s | 907 | — | — | 待核验 |
| [Luogu P4723](https://www.luogu.com.cn/record/297629192) | Accepted, classic | time_display=4.52s | 905 | — | — | 待核验 |
| [Luogu P4767](https://www.luogu.com.cn/record/302210674) | Accepted, compact | time_ms=41 | 41 | 169 | 169 | 待核验 |
| [Luogu P4777](https://www.luogu.com.cn/record/297521102) | Accepted, compact | time_ms=142 | — | — | — | 待核验 |
| [Luogu P4777](https://www.luogu.com.cn/record/297521173) | Accepted, classic | time_ms=141 | — | — | — | 待核验 |
| [Luogu P4781](https://www.luogu.com.cn/record/297520159) | Accepted, compact | time_ms=304 | — | — | — | 待核验 |
| [Luogu P4781](https://www.luogu.com.cn/record/297520164) | Accepted, classic | time_ms=100 | — | — | — | 待核验 |
| [Luogu P4897](https://www.luogu.com.cn/record/297591576) | Accepted, compact | time_display=2.46s | 252 | — | — | 待核验 |
| [Luogu P4897](https://www.luogu.com.cn/record/297592933) | Accepted, classic | time_display=1.80s | 185 | — | — | 待核验 |
| [Luogu P4980](https://www.luogu.com.cn/record/302212651) | Accepted, compact | time_ms=120 | 120 | 679 | 679 | 待核验 |
| [Luogu P5236](https://www.luogu.com.cn/record/302334786) | Accepted, compact | time_ms=202 | 12 | 202 | — | 待核验 |
| [Luogu P5395](https://www.luogu.com.cn/record/297626422) | Accepted, compact | time_display=1.04s | 202 | — | — | 待核验 |
| [Luogu P5395](https://www.luogu.com.cn/record/297626660) | Accepted, classic | time_display=1.03s | 203 | — | — | 待核验 |
| [Luogu P5408](https://www.luogu.com.cn/record/297627360) | Accepted, compact | time_display=1.53s | 310 | — | — | 待核验 |
| [Luogu P5408](https://www.luogu.com.cn/record/297627676) | Accepted, classic | time_display=1.54s | 311 | — | — | 待核验 |
| [Luogu P5431](https://www.luogu.com.cn/record/297561197) | Accepted, compact | time_ms=806 | 386 | — | — | 待核验 |
| [Luogu P5431](https://www.luogu.com.cn/record/297561804) | Accepted, classic | time_ms=803 | 384 | — | — | 待核验 |
| [Luogu P5491](https://www.luogu.com.cn/record/297520354) | Accepted, compact | time_ms=148 | — | — | — | 待核验 |
| [Luogu P5496](https://www.luogu.com.cn/record/297518043) | Accepted, compact | time_ms=422 | — | — | — | 待核验 |
| [Luogu P5668](https://www.luogu.com.cn/record/300024458) | Accepted, compact | time_ms=172 | 172 | 372 | 372 | 待核验 |
| [Luogu P5903](https://www.luogu.com.cn/record/302333606) | Accepted, compact | displayed_total_time=7.13s; max_case_time_display=1.51s | — | — | — | 待核验 |
| [Luogu P6091](https://www.luogu.com.cn/record/297558740) | Accepted, compact | time_ms=2793 | — | — | — | 待核验 |
| [Luogu P6091](https://www.luogu.com.cn/record/297559082) | Accepted, classic | time_ms=2796 | — | — | — | 待核验 |
| [Luogu P6097](https://www.luogu.com.cn/record/297631186) | Accepted, compact | time_display=4.93s; max_case_time_display=2.70s | 2700 | — | — | 待核验 |
| [Luogu P6097](https://www.luogu.com.cn/record/297631585) | Accepted, classic | time_display=4.93s; max_case_time_display=2.69s | 2690 | — | — | 待核验 |
| [Luogu P6114](https://www.luogu.com.cn/record/302332529) | Accepted, compact | displayed_total_time=251ms; max_case_time_display=38ms | 38 | 251 | 251 | 待核验 |
| [Luogu P6136](https://www.luogu.com.cn/record/297800993) | Accepted, compact | time_ms=1130 | — | — | — | 待核验 |
| [Luogu P6175](https://www.luogu.com.cn/record/302333056) | Accepted, compact | displayed_total_time=68ms; max_case_time_display=8ms | 8 | 68 | 68 | 待核验 |
| [Luogu P6178](https://www.luogu.com.cn/record/297619886) | Accepted, compact | time_display=517ms | 64 | — | — | 待核验 |
| [Luogu P6178](https://www.luogu.com.cn/record/297620263) | Accepted, classic | time_display=512ms | 62 | — | — | 待核验 |
| [Luogu P6577](https://www.luogu.com.cn/record/297520123) | Accepted, compact | time_ms=2010 | — | — | — | 待核验 |
| [Luogu P6577](https://www.luogu.com.cn/record/297520132) | Accepted, classic | time_ms=1860 | — | — | — | 待核验 |
| [Luogu P8435](https://www.luogu.com.cn/record/297517446) | Accepted, compact | time_ms=4770 | — | — | — | 待核验 |
| [Luogu P8435](https://www.luogu.com.cn/record/297517662) | Accepted, classic | time_ms=4950 | — | — | — | 待核验 |
| [Luogu P8436](https://www.luogu.com.cn/record/297519028) | Accepted, compact | time_ms=5040 | — | — | — | 待核验 |
| [Luogu P8436](https://www.luogu.com.cn/record/297519083) | Accepted, classic | time_ms=5430 | — | — | — | 待核验 |
| [Luogu U367189](https://www.luogu.com.cn/record/302334160) | Accepted, compact | — | 63 | 392 | 392 | 待核验 |
| [P2617](https://www.luogu.com.cn/record/301886868) | Accepted | displayed_total_time=1.99s | 191 | 1994 | — | 待核验 |
| [P2865](https://www.luogu.com.cn/record/302207967) | Accepted | — | 30 | 79 | — | 待核验 |
| [P2901](https://www.luogu.com.cn/record/302208192) | Accepted | — | 11 | 59 | — | 待核验 |
| [P3370](https://www.luogu.com.cn/record/302216358) | Accepted, compact | displayed_total_time=1.90s | 464 | 1896 | — | 待核验 |
| [P4768](https://www.luogu.com.cn/record/302331476) | Accepted, compact | displayed_total_time=13.72s; max_case_time_display=2.01s | — | — | — | 待核验 |
| [P5043](https://www.luogu.com.cn/record/301887481) | Accepted | displayed_total_time=42ms | 5 | 42 | — | 待核验 |
| [P5906](https://www.luogu.com.cn/record/301884220) | Accepted | displayed_total_time=7.46s | 762 | 7456 | — | 待核验 |
| [QOJ 8235](https://qoj.ac/submission/2939493) | Accepted, compact | time_display=666ms | 666 | — | — | 待核验 |
| [QOJ 8235](https://qoj.ac/submission/2939551) | Accepted, classic | time_display=588ms | 588 | — | — | 待核验 |
| [QOJ 8236](https://qoj.ac/submission/2940150) | Accepted, compact | time_ms=324 | — | — | — | 待核验 |
| [QOJ 8236](https://qoj.ac/submission/2940191) | Accepted, classic | time_ms=294 | — | — | — | 待核验 |
| [QOJ 8237](https://qoj.ac/submission/2939916) | Accepted, compact | time_display=162ms | 162 | — | — | 待核验 |
| [QOJ 8237](https://qoj.ac/submission/2939975) | Accepted, classic | time_display=158ms | 158 | — | — | 待核验 |
| [QOJ 8240](https://qoj.ac/submission/2939235) | Accepted, compact | time_display=789ms | 789 | — | — | 待核验 |
| [QOJ 8240](https://qoj.ac/submission/2939291) | Accepted, classic | time_display=752ms | 752 | — | — | 待核验 |
| [QOJ 906](https://qoj.ac/submission/2940638) | Accepted, compact | time_ms=203 | — | — | — | 待核验 |
| [QOJ 906](https://qoj.ac/submission/3061625) | Accepted, compact | time_ms=226 | — | — | — | 待核验 |
| [QOJ 999](https://qoj.ac/submission/3061643) | Accepted, compact | time_ms=87 | — | — | — | 待核验 |
| [SP10707](https://www.luogu.com.cn/record/301884426) | Waiting | — | — | — | — | 待核验 |

逐条证据路径、源码哈希、编译语言与原始计时字段见 [机器可读清单](../verification/online-runtimes.json)。本表可由 `python3 tools/online_runtimes.py` 重建。
