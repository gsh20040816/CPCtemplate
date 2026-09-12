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
| `PBDSOrderedTree` | [Luogu P3369](https://www.luogu.com.cn/problem/P3369) | operations<=100000; \|x\|<=10000000 | 待实现 | 待核验 |
| `PBDSOrderedTree` | [Luogu P6136](https://www.luogu.com.cn/problem/P6136) | n<=100000; m<=1000000; values<2^30 | 待实现 | 待核验 |
| `GPHashTable` | [Library Checker associative_array](https://judge.yosupo.jp/problem/associative_array) | Q<=1000000; 0<=key,value<=10^18; 5s | 待实现 | 待核验 |
| `RopePersistentQueue` | [Library Checker persistent_queue](https://judge.yosupo.jp/problem/persistent_queue) | Q<=500000; -1<=t_i<i; 0<=x<=10^9; 5s | 待实现 | 待核验 |
| `dsu` | [Luogu P3367](https://www.luogu.com.cn/problem/P3367) | N<=200000; M<=1000000; 1-based task vertices | 待编写驱动/提交 | 待核验 |

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

### Luogu P3369 / PBDSOrderedTree

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Planned extc++ order-statistics tree target. Preserve duplicate values through unique secondary IDs and a strict comparator; less_equal is not a valid workaround. Erase exactly one key, convert zero-based find_by_order to the problem kth convention. Existing Treap/Splay AC does not validate PBDS.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

### Luogu P6136 / PBDSOrderedTree

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Read an initial multiset, XOR each operand with the last query answer before executing it, and print XOR of all query answers. All operations are legal. Cannot simply reuse P3369 input/output or sort operations offline; require separate maximum-scale performance evidence.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

### Library Checker associative_array / GPHashTable

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Planned gp_hash_table target: assignment 0 k v, lookup 1 k, absent keys return zero. Use 64-bit keys/values; lookup should use find if unintended insertion is undesirable. Official tests include unordered_map killers and sparse-key families. Hash collision performance requires explicit testing, not average-case assumptions alone.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/associative_array/info.toml)

### Library Checker persistent_queue / RopePersistentQueue

Standalone, explicitly designated standard template; reuse in template-practice contests is distinguished from regional-contest applications.

Candidate rope composition: version -1 is empty; copy version t, append or remove/print its first element, creating version i. Pop is guaranteed nonempty. Installed GCC rope exposes copy construction, push_back, indexing and erase, but worst-case time/memory and version isolation are not yet tested. This target does not verify arbitrary rope editing or reversal.

Implementation is not present. This is a reviewed target only; performance, driver, AC and ranking remain unverified.

原始题面与参数：[来源 1](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/task.md)，[来源 2](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/data_structure/persistent_queue/info.toml)

### Luogu P3367 / dsu

Explicit standard DSU template. Retained by user exception in issue #2 comment 5646284816.

Construct dsu(n); subtract one from task vertices; merge/same provide the required operations. size/groups are covered by independent local tests, not by this task output. Linking direction follows the supplied user version without union-by-size.

P3367 complete driver and maximum constraints passed locally with ASan/UBSan; online submission/ranking pending. Local dsu tests additionally cover empty groups, root direction, sizes and 500000-node unbalanced path.

## 榜单口径

QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。
