# 已核对的模板题入口

本表仅收录已经阅读题面与适配约定的映射。AC、接口覆盖与速度榜分别记录；空白项不表示完成。完整候选和上游缺项见 [候选清单](template-problems.json)，执行依据为 [issue #1](ISSUE-1.md)。

| 算法 | 模板题 | 边界 | 当前 AC | 速度榜 |
|---|---|---|---|---|
| `ModifiedMo` | [Luogu P1903](https://www.luogu.com.cn/problem/P1903) | n,m<=133333; colors<=1000000 | [记录](https://www.luogu.com.cn/record/297653743) | 待核验 |
| `TarjanSCC` | [QOJ 906](https://qoj.ac/problem/906) | 1<=N,M<=500000; directed multigraph; 0-based vertices | [记录](https://qoj.ac/submission/2940638) | 94 out of 143（CCF_NOI 当前可见的满分提交，按用时并列） |
| `berlekamp_massey` | [QOJ 547](https://qoj.ac/problem/547) | 0<=n<=10000; modulus 998244353 | 待提交 | 待核验 |
| `prefix_function` | [QOJ 464](https://qoj.ac/problem/464) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待提交 | 待核验 |
| `z_function` | [QOJ 786](https://qoj.ac/problem/786) | 1<=\|S\|<=2000000; lowercase; 0.5s | 待提交 | 待核验 |
| `manacher` | [QOJ 787](https://qoj.ac/problem/787) | \|S\|<=1000000; 1s | 待提交 | 待核验 |
| `TwoSAT` | [QOJ 997](https://qoj.ac/problem/997) | 1<=n<=100000; 1<=m<=500000; 1-based variables | 待提交 | 待核验 |

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

## 榜单口径

QOJ statistics 的“最快”表会合并同一用户的提交，不能把榜单行号配上全体满分提交数。已核对同一用户三条 AC 的反例，详见 ranking-audits.json。用户要求的所有提交速度排名需另行枚举或找到可靠筛选接口；没有核验前保持待查。读取时间、相邻排名与并列用时范围必须随排名一起保存。
