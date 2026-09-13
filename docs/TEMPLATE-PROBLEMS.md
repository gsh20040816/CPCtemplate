# 已核对的模板题入口

本表仅收录已经阅读题面与适配约定的映射。AC、接口覆盖与速度榜分别记录；空白项不表示完成。完整候选和上游缺项见 [候选清单](template-problems.json)，执行依据为 [issue #1](ISSUE-1.md)。

| 算法 | 模板题 | 边界 | 当前 AC | 速度榜 |
|---|---|---|---|---|
| `ModifiedMo` | [Luogu P1903](https://www.luogu.com.cn/problem/P1903) | n,m<=133333; colors<=1000000 | [记录](https://www.luogu.com.cn/record/297653743) | 待核验 |
| `TarjanSCC` | [QOJ 906](https://qoj.ac/problem/906) | 1<=N,M<=500000; directed multigraph; 0-based vertices | [记录](https://qoj.ac/submission/2940638) | 94 out of 143（CCF_NOI 当前可见的满分提交，按用时并列） |
| `berlekamp_massey` | [QOJ 547](https://qoj.ac/problem/547) | 0<=n<=10000; modulus 998244353 | 待编写驱动/提交 | 待核验 |
| `prefix_function` | [QOJ 464](https://qoj.ac/problem/464) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待编写驱动/提交 | 待核验 |
| `z_function` | [QOJ 786](https://qoj.ac/problem/786) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待编写驱动/提交 | 待核验 |
| `manacher` | [QOJ 787](https://qoj.ac/problem/787) | \|S\|<=1000000; 1s | 待编写驱动/提交 | 待核验 |
| `TwoSAT` | [QOJ 997](https://qoj.ac/problem/997) | 1<=n<=100000; 1<=m<=500000; 1-based variables | 待编写驱动/提交 | 待核验 |
| `NttConvolution::multiply` | [QOJ 618](https://qoj.ac/problem/618) | degrees n,m in [1,1000000]; modulus 998244353; 1s | 待编写驱动/提交 | 待核验 |
| `Polynomial::multiply` | [QOJ 618](https://qoj.ac/problem/618) | degrees n,m<=1000000; modulus 998244353; 1s | 待编写驱动/提交 | 待核验 |
| `Polynomial::inverse` | [QOJ 619](https://qoj.ac/problem/619) | 1<=n<=1000000; modulus 998244353; a[0]!=0; 1.5s | 待编写驱动/提交 | 待核验 |
| `Polynomial::log` | [QOJ 620](https://qoj.ac/problem/620) | 1<=n<=1000000; modulus 998244353; a[0]=1; 1.5s | 待编写驱动/提交 | 待核验 |
| `Polynomial::exp` | [QOJ 621](https://qoj.ac/problem/621) | 1<=n<=1000000; modulus 998244353; a[0]=0; 2.5s | 待编写驱动/提交 | 待核验 |
| `GeneralMultipointEvaluation` | [QOJ 622](https://qoj.ac/problem/622) | 1<=n,m<=1000000; output mod 998244353; 10s | 待实现 | 待核验 |
| `SuffixArray::sa` | [QOJ 956](https://qoj.ac/problem/956) | 1<=n<=1000000; ASCII letters/digits; 3s; 128MB | 待编写驱动/提交 | 待核验 |
| `PalindromicTree::add/occurrences` | [QOJ 801](https://qoj.ac/problem/801) | lowercase string length<=1000000; 1s; 2048MB | 待编写驱动/提交 | 待核验 |
| `SuffixAutomaton::extend/counts` | [Luogu P3804](https://www.luogu.com.cn/problem/P3804) | 1<=\|S\|<=1000000; lowercase | 待编写驱动/提交 | 待核验 |
| `OrderedTreap` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | 1<=operations<=100000; \|x\|<=10000000 | [记录](https://www.luogu.com.cn/record/297515150) | 待核验 |
| `OrderedSplay` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | 1<=operations<=100000; \|x\|<=10000000 | [记录](https://www.luogu.com.cn/record/297520192) | 待核验 |
| `SequenceTreap` | [Luogu P3391](https://www.luogu.com.cn/problem/P3391) | 1<=n,m<=100000; 1<=l<=r<=n | [记录](https://www.luogu.com.cn/record/297520211) | 待核验 |
| `ost` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | operations<=100000; \|x\|<=10000000 | 待编写驱动/提交 | 待核验 |
| `ost` | [Luogu P6136](https://www.luogu.com.cn/problem/P6136) | n<=100000; m<=1000000; values<2^30 | [记录](https://www.luogu.com.cn/record/297800993) | 待核验 |
| `gp_map` | [Library Checker associative_array](https://judge.yosupo.jp/problem/associative_array) | Q<=1000000; 0<=key,value<=10^18; 5s | [记录](https://judge.yosupo.jp/submission/401867) | 956 out of 7334（All AC submissions, all users including anonymous, all languages, Dedup user unchecked. Not all verdicts and not per-user best.） |
| `rp` | [Library Checker persistent_queue](https://judge.yosupo.jp/problem/persistent_queue) | Q<=500000; -1<=t_i<i; 0<=x<=10^9; 5s | [记录](https://judge.yosupo.jp/submission/401871) | 待核验 |
| `dsu` | [Luogu P3367](https://www.luogu.com.cn/problem/P3367) | N<=200000; M<=1000000; 1-based task vertices | [记录](https://www.luogu.com.cn/record/297668102) | 待核验 |
| `Lowlink::add/run/bridge` | [QOJ 995](https://qoj.ac/problem/995) | n<=100000; m<=500000; 1s; 1-based | 待编写驱动/提交 | 待核验 |
| `Lowlink::add/run/cut` | [QOJ 996](https://qoj.ac/problem/996) | n<=20000; m<=100000; 0.5s; 1-based | 待编写驱动/提交 | 待核验 |
| `Dinic::add/flow` | [Luogu P3376](https://www.luogu.com.cn/problem/P3376) | n<=200; m<=5000; 0<=capacity<2^31 | [记录](https://www.luogu.com.cn/record/297501480) | 待核验 |
| `MinCostFlow::slope` | [Luogu P3381](https://www.luogu.com.cn/problem/P3381) | n<=5000; m<=50000; capacity,cost<=1000; result<=2^31-1 | 待编写驱动/提交 | 待核验 |
| `Biconnected::add/run/blocks` | [Luogu P8435](https://www.luogu.com.cn/problem/P8435) | n<=500000; m<=2000000 | [记录](https://www.luogu.com.cn/record/297517446) | 待核验 |
| `Biconnected::add/run/bel` | [Luogu P8436](https://www.luogu.com.cn/problem/P8436) | n<=500000; m<=2000000; multigraph | [记录](https://www.luogu.com.cn/record/297519028) | 待核验 |
| `BipartiteMatching::add/solve` | [Luogu P3386](https://www.luogu.com.cn/problem/P3386) | 1<=n,m<=500; edges<=50000; parallel edges allowed | 待编写驱动/提交 | 待核验 |
| `WeightedMatching::add/solve/r` | [Luogu P6577](https://www.luogu.com.cn/problem/P6577) | n<=500; m<=n^2; -19980731<=weight<=19980731 | [记录](https://www.luogu.com.cn/record/297520123) | 待核验 |
| `OfflineLCA::add/add_query/run/answer` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S; queries may have equal endpoints | [记录](https://www.luogu.com.cn/record/297521009) | 待核验 |
| `EulerLCA::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `LiftingLCA::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `HLD::add/build/lca` | [Luogu P3379](https://www.luogu.com.cn/problem/P3379) | N,M<=500000; root S | 待编写驱动/提交 | 待核验 |
| `HLD + AffineSegTree` | [Luogu P3384](https://www.luogu.com.cn/problem/P3384) | n,m<=100000; 1<=P<=2^30; int inputs | [记录](https://www.luogu.com.cn/record/297520172) | 待核验 |
| `CentroidPairs::add/build/count_exact` | [Luogu P3806](https://www.luogu.com.cn/problem/P3806) | n<=10000; m<=100; 1<=k<=10^7; 1<=edge_weight<=10000 | [记录](https://www.luogu.com.cn/record/297519137) | 待核验 |
| `PersistentKth::kth` | [Luogu P3834](https://www.luogu.com.cn/problem/P3834) | n,m<=200000; 0<=a[i]<=10^9; valid l,r,k | [记录](https://www.luogu.com.cn/record/297520290) | 待核验 |
| `ost` | [Library Checker ordered_set](https://judge.yosupo.jp/problem/ordered_set) | 0<=N<=500000; 1<=Q<=500000; sorted distinct initial keys; 0<=keys<=10^9; kth query x>=1 | [记录](https://judge.yosupo.jp/submission/401869) | 628 out of 1095（All AC submissions, all users and languages, Dedup user unchecked. Not non-AC verdicts or per-user best.） |
| `segtree` | [Library Checker point_set_range_composite](https://judge.yosupo.jp/problem/point_set_range_composite) | N,Q<=500000; 0<=l<r<=N; coefficients mod998244353 with nonzero slopes | [记录](https://judge.yosupo.jp/submission/402090) | 454 out of 2914（All AC submissions, all users/languages, dedup disabled; excludes non-AC verdicts.） |
| `segtree` | [Library Checker predecessor_problem](https://judge.yosupo.jp/problem/predecessor_problem) | 1<=N<=10000000;1<=Q<=1000000;0<=k<N;initial binary membership string | [记录](https://judge.yosupo.jp/submission/402089) | 687 out of 2582（All users and languages, AC only, user dedup disabled; not all verdicts.） |
| `lazy_segtree` | [Library Checker range_affine_range_sum](https://judge.yosupo.jp/problem/range_affine_range_sum) | N,Q<=500000; coefficients modulo998244353; nonzero multipliers;0<=l<r<=N | 待编写驱动/提交 | 待核验 |
| `mint` | [Luogu P5431](https://www.luogu.com.cn/problem/P5431) | n<=5000000;2<=k<p<=10^9;prime p;1<=a_i<p | 待编写驱动/提交 | 待核验 |
| `convolution_i64` | [Luogu P3803](https://www.luogu.com.cn/problem/P3803) | Degrees n,m<=1000000; coefficients 0..9; exact integer output. | 待编写驱动/提交 | 待核验 |
| `TarjanSCC` | [Library Checker Strongly Connected Components](https://judge.yosupo.jp/problem/scc) | 1<=N,M<=500000; vertices 0..N-1; loops and parallel edges allowed. | 待编写驱动/提交 | 待核验 |
| `TwoSAT` | [Library Checker 2 Sat](https://judge.yosupo.jp/problem/two_sat) | 1<=N,M<=500000; signed DIMACS literals in +/-1..N. | 待编写驱动/提交 | 待核验 |

## 适配与证据范围

### Luogu P1903 / ModifiedMo

Official title explicitly labels this as a modifiable-Mo template. Historical source is national-team training / bzoj2120; retained here as a standalone standard-template candidate, not a regional-contest application.



Check fastest-submission leaderboard availability and denominator. This AC does not complete issue #1.

### QOJ 906 / TarjanSCC

Library Checker standard SCC task, reused in template practice contests.

Shift input vertices +1; emit component IDs in reverse order because Tarjan IDs are reverse topological. add/run/bel are covered; dag is not called.

Global full-score count is 578, but linked visible list contains 143 records. Global rank is unresolved; displayed best-per-user table position 66 is not an all-submission rank. dag remains outside this AC scope.

### QOJ 547 / berlekamp_massey

Direct shortest finite-prefix recurrence template; template practice use.

Output returned coefficient count and positive recurrence coefficients. n=0 needs an empty line. Does not test recurrence_nth.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 464 / prefix_function

Direct prefix-function template; template practice use.

Print prefix_function output in order. This task does not test kmp_match.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 786 / z_function

Direct Z-function template; template practice use.

Problem requires z[0]=0; current library deliberately returns |S|. Driver must replace the first output with 0; do not change the generic contract silently.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 787 / manacher

Direct longest-palindrome template; template practice use.

Take maximum of 2*odd[i]-1 and 2*even[i]. The scalar answer does not independently verify every radius.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 997 / TwoSAT

Direct Boolean clause assignment template; template practice use.

add(a,b,c,d) encodes the given disjunction; solve then ans[1..n]. Print Yes/No, unlike Luogu POSSIBLE/IMPOSSIBLE.

Driver/AC and full-score submission speed-rank audit pending. This is a reviewed task mapping, not a completed verification.

### QOJ 618 / NttConvolution

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Read n+1 and m+1 coefficients, not n and m. multiply returns n+m+1 coefficients. Transform size is at most 2^21, within the 998244353 capacity. This fixed-modulus task cannot certify all template moduli or primitive roots.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 618 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Same degree-based input adapter, using Polynomial::multiply. Record this implementation separately from NttConvolution and do not transfer AC or speed evidence between the two.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 619 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Here n is coefficient count and truncation order. Call inverse(a,n), print exactly n coefficients. Verify the complete driver and largest non-power-of-two truncation; multiplication AC alone does not prove inverse.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 620 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call log(a,n), preserving n coefficients including constant zero. Constant-one restriction is essential. Derivative/integral/inverse are dependencies, but only the composed logarithm behavior is directly observed.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 621 / Polynomial

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call exp(a,n), preserving n coefficients with constant one. Do not confuse coefficient count with polynomial degree or ordinary floating-point exponential.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 622 / GeneralMultipointEvaluation

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Input has n coefficients followed by m arbitrary nonnegative evaluation points. Distinctness is not promised. General product/remainder-tree evaluation is absent; Chirp Z only handles geometric points and cannot replace this task. Coefficient and point upper bounds are not explicitly stated on the fetched page, so parser bounds need further audit.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

### QOJ 956 / SuffixArray

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Print each sa index plus one. Library sa is zero-based and orders unsigned bytes. This task outputs suffix order only, not the lcp array or range-LCP queries.

Driver, online evidence and fastest-ranking scope still require verification.

### QOJ 801 / PalindromicTree

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Call add(ch) with each lowercase character, obtain occurrences(), then maximize occ[u]*len[u]*len[u] over real nodes u>=2. Promote before multiplication: n^3<=10^18 fits signed 64-bit. This is length squared, unlike common length-times-occurrence tasks. distinct and incremental total are not directly validated.

Driver, online evidence and fastest-ranking scope still require verification.

### Luogu P3804 / SuffixAutomaton

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Use extend and counts; maximize cnt[u]*a[u].len only where cnt[u]>1, otherwise output zero. Use 64-bit multiplication. distinct is not tested. The QOJ217 candidate was not reviewed because the fetch returned HTTP 429; no equivalence to it is claimed.

Driver, online evidence and fastest-ranking scope still require verification.

### Luogu P3369 / OrderedTreap

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Multiset semantics: erase one copy, rank is number of values <x plus one, kth is one-based, predecessor/successor are strict. x need not already exist for rank/neighbor queries. kth and neighbors have guaranteed answers.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3369 / OrderedSplay

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Multiset semantics: erase one copy, rank is number of values <x plus one, kth is one-based, predecessor/successor are strict. x need not already exist for rank/neighbor queries. kth and neighbors have guaranteed answers.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3391 / SequenceTreap

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Initialize values 1..n using zero-based insertion positions; reverse uses the library one-based closed [l,r] interval; output values(). This does not validate range addition or general erase. A plain rope has no lazy reversal API, so it must not inherit this efficiency claim.

Existing vector AC retained with its archived scope; leaderboard ranking remains unverified.

### Luogu P3369 / ost

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Use pair<int,int> with unique positive ID; deletion erases only one equal key, absent deletion ignored. Strict ranks use {x,0}; predecessor lower_bound then prev; successor upper_bound({x,INT_MAX}); kth converted from 1-based.

Separate PBDS multiset driver now passes independent sorted-list oracle and ASan/UBSan. P6136 also checks 100000 initial duplicates and 1000000 online operations. Online AC and ranking still pending.

### Luogu P6136 / ost

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Read an initial multiset, XOR each operand with the last query answer before executing it, and print XOR of all query answers. All operations are legal. Cannot simply reuse P3369 input/output or sort operations offline; require separate maximum-scale performance evidence.

Fastest-submission ranking availability and scope remain to audit. P3369 driver has separate pending online evidence.

### Library Checker associative_array / gp_map

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

uint64_t keys and values; assignment uses operator[], lookup uses find and returns zero without insertion. Official online tests include hash-killer and sparse-key families.

PBDS ordered trees and rope remain separate work. This AC validates assignment/find only; erase/insert/copy/clear have local evidence.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/info.toml)

### Library Checker persistent_queue / rp

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Version -1 becomes index 0. Preallocate Q zero cells; copy root and head/tail per version. Push is replace at tail; pop reads head then increments it. This avoids repeated rope concat/erase rebalancing in direct queue implementation.

Ranking pending. General insert/erase/substr have local evidence only; significant version-memory overhead remains.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/info.toml)

### Luogu P3367 / dsu

Explicit standard DSU template. Retained by user exception in issue #2 comment 5646284816.

Construct dsu(n); subtract one from task vertices; merge/same provide the required operations. size/groups are covered by independent local tests, not by this task output. Linking direction follows the supplied user version without union-by-size.

P3367 final source AC: 20 tests, slowest 196ms. size/groups remain independently local-tested; leaderboard ranking pending.

### QOJ 995 / Lowlink

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

保存每条边原始有序端点；add 返回输入顺序边号，run 后按边号扫描 bridge。只输出标记为桥的原端点，不排序端点或按 DFS 发现顺序输出。题目允许重边与自环；该输出不验证 cut 和 delta。

完整驱动、在线验证及速度榜口径仍待核验。

### QOJ 996 / Lowlink

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

run 后扫描 cut[1..n]，先输出数量，再按顶点编号递增输出。必须遍历全部连通分量；根节点割点条件不同。该题不输出桥或删点后的分量增量。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3376 / Dinic

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

读入 n,m,s,t 与有向边，按容量加入后调用 flow(s,t)，使用库约定的不同源汇。总流量可能超过 32 位，需要 long long；不可达或零容量网络输出 0。默认最大流结果不单独验证 limit、used 或 cut。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3381 / MinCostFlow

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

输出 flow(s,t) 返回的流量、费用，顺序不可反。原始费用非负，且题目不允许自环；不能用此题证明负费用边、负环处理或超大费用范围。库费用累加为 int128，驱动打印须与题目数值界兼容。 新驱动输出 slope 最后一个折点，仅验证终点，不覆盖中间曲线。

完整 slope 终点驱动已通过独立边流枚举，线上和排名待核验。中间折点以独立曲线测试验证。

### Luogu P8435 / Biconnected

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

输出 run 后的 blocks。题目采用“无割点”定义，要包括孤立点及自环场景；库将自环保留在边表但不加入 DFS 邻接表，孤立顶点输出单点块。不同块可能共享割点，不能当作互不相交的顶点分区。此输出不验证圆方树接口。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P8436 / Biconnected

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

按 run 后的 bel[1..n] 分组并输出 cnt 组，点号和分量号均为 1-based；支持重边、自环、孤立点和多个连通分量。不能误用点双 blocks；本题不单独输出桥森林。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3386 / BipartiteMatching

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

左右点集分别按 1..n 和 1..m 编号，add 后 solve 返回匹配边数，不要把两侧编号混在一个区间。题目只要求数量，不检查 cover 或完整匹配方案；存在重边。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P6577 / WeightedMatching

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

构造两侧均为 n 的实例，调用 solve(false)；题目保证完美匹配。权值允许负数，缺边不能当成零权边。第二行要求右点到左点的配对，输出 r[1..n]。此题不验证允许不匹配的分支或矩形点集。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3379 / OfflineLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

先登记全部 add_query，再 run(S)，按登记顺序输出 answer。点号 1-based；不能把固定根 1 当作题目给定根 S。原离线驱动已有对应记录。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3379 / EulerLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

按无权树加入边，以 S 建立 Euler 序，再逐条输出 lca(a,b)。该题不验证加权距离、边距离或其它 RMQ 包装接口；不能挪用 OfflineLCA 的 AC。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3379 / LiftingLCA

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

默认单位边权即可，以 S build 后调用 lca。相同端点应返回自身。题目不验证祖先跳转、路径最大边或换根查询；须使用本实现自己的驱动与记录。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3379 / HLD

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

以 S 剖分，输出 lca(a,b)。无需接线段树；该题不检查 path 回调、边权路径的 LCA 排除或子树区间。

完整驱动、在线验证及速度榜口径仍待核验。

### Luogu P3384 / HLD + AffineSegTree

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

以给定根 R 构建 HLD，把初始点权放到 dfn 位置，线段树使用同一模数 P。path 的闭区间直接调用 update(l,r,1,z)；子树区间为 [dfn[u],dfn[u]+siz[u]-1]。这是点权而非边权，包含路径两端。该组合不证明通用乘法更新或在线换根。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3806 / CentroidPairs

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

静态树 build 后以 count_exact(k)>0 输出 AYE/NAY。题目只观察存在性，不能据此验证所有点对计数值；零权、负查询值等扩展需保留本地证据。多个查询复用同一分解。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Luogu P3834 / PersistentKth

标准算法模板题；作为独立模板入口核对，不用区域赛应用代替该接口的验证。

构造时传入不含占位元素的原数组；kth(l,r,k) 接收 1-based 闭区间和 1-based 名次。内部比较 root[r] 与 root[l-1] 的频次数，并还原离散值。该题不支持在线修改或任意版本拼接，不能给其它可持久化接口背书。

保留已有 vector 提交的归档验证范围；该模板题的速度榜仍待核验。

### Library Checker ordered_set / ost

Official standalone ordered set template task.

Convert 1-based kth to find_by_order(x-1). Inclusive count uses order_of_key(x)+presence, avoiding x+1 overflow. Predecessor is <=x via upper_bound, successor is >=x via lower_bound; missing outputs -1. Duplicates ignored.

Duplicate-key adapters require separate online tests.

### Library Checker point_set_range_composite / segtree

Official standalone generic segment-tree composition template.

0-based point set and half-open prod. op(f,g)=g after f. Evaluate returned affine function at x. This driver does not invoke either boundary-search API.

all() and empty-range output remain local evidence. Boundary searches verified separately by predecessor_problem.

### Library Checker predecessor_problem / segtree

Official standalone dynamic predecessor template task.

Store 0/1 counts; set for insert/erase, get for membership. max_right(k,sum==0) finds inclusive successor, N becomes -1. min_left(k+1,sum==0)-1 finds inclusive predecessor, zero result becomes -1. No overflow of sum at N limit.

prod/all not invoked. Noncommutative boundary order locally verified separately.

### Library Checker range_affine_range_sum / lazy_segtree

Official standalone range-affine/range-sum template.

Node {sum,len}; tag {mul,add}. composition(f,g)=f after g, mapping multiplies sum and adds add*len. Driver calls construction/apply/prod only.

19 official generated cases pass local checker in normal and sanitizer builds; online submit/ranking still pending. Other interfaces retain separate local evidence.

### Luogu P5431 / mint

Official batch inverse template with runtime prime modulus.

mint sets runtime modulus then combines batch_units. Return sum k^i/a_i for i starting at1; fast unsigned reader. Input guarantees units, so nonunit branch is only locally tested.

Online submission pending; existing long-long P5431 AC does not cover this new driver.

### Luogu P3803 / convolution_i64

Standalone polynomial multiplication template.

Read n+1 and m+1 signed64 coefficients; output exact convolution. Maximum coefficient 81*(1000001).

Online result and performance pending; negative and signed64 extremes covered by local cpp_int oracle only.

### Library Checker Strongly Connected Components / TarjanSCC

Official standalone template task.

Shift vertices +1 on input and -1 on output. Tarjan IDs are reverse topological; print component groups from cnt down to1. Output partition and order checked independently by reachability.

Online submission and all-AC ranking pending; local independent driver oracle and official checker evidence are separate from prior OJ AC.

### Library Checker 2 Sat / TwoSAT

Official standalone template task.

Read p cnf N M; each a b 0 maps to add(abs(a),a>0,abs(b),b>0). Output SAT/UNSAT and signed assignment in variable order. Current TwoSAT uses its existing Kosaraju SCC numbering convention.

Online submission and all-AC ranking pending; local independent driver oracle and official checker evidence are separate from prior OJ AC.

## 榜单口径

QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。
