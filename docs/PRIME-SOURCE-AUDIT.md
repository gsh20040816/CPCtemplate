# kuangbin 素数章节来源核对

§2.1 的三个子项均由既有 `LinearSieve` 和 `segmented_primes` 覆盖。本次补齐完整原片段对照，把父项从 pending 改为 local-tested；没有新增基础模板，也没有新的线上 AC。

原稿印刷25–27页（物理27–29页）已逐页目视核对。固定 PDF SHA256 为 `f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad`。三个完整片段分别为17、16、58行，保存在 `tests/fixtures/prime_sources/`。仅移除行号和排版缩进、恢复减号及字符串空格、拼回两处折行，算法未修补。

## 接口对应

- §2.1.1 原 `notprime[x]` 为 false 表示素数，范围为 `0 <= x < 1000010`。对应 `LinearSieve(1000009)`；判素数须写 `x >= 2 && sieve.lp[x] == x`，不能漏掉0、1保护。
- §2.1.2 原 `prime[0]` 存数量，`prime[1..prime[0]]` 是递增素数列表，范围为 `x <= 10000`。对应 `LinearSieve(10000).prime` 的0-based vector。原数组其余位置混合了筛法标记，不能当普通布尔表读取。
- §2.1.3 原闭区间筛与 EOF 主程序对应 `segmented_primes(l,r)` 和 `verify/poj/2689.compact.cpp`。原稿对 L<2 调整到2，新接口直接忽略0、1。原稿要求1≤L<U≤INT_MAX、U−L≤1000000；这些是原文约定，不是本轮重新获取的官方限制。

相邻素数最近、最远距离相同，两个程序都保留最先出现的一对。少于两个素数时输出固定句子；有答案时空格、逗号、句点与原稿一致。原程序没有显式 return0，因此测试保留其全局 main，不能把它改名为普通函数再依赖隐式返回。

## 本地证据

`python3 tests/prime_source_audit.py` 与 `--sanitize` 均通过。

完整百万范围布尔表用独立试除逐值检查，并核对当前最小质因子表的判素数结果和完整递增列表；全量执行两轮，检验原初始化函数的重复调用。10000范围列表核对数量、顺序和全部元素。当前 header、NDEBUG、实际抄写组件三种形式均运行这些检查，另含 n=0、1、2、3、4、97、10000。

区间程序用独立32位确定性 Miller–Rabin（底数2、7、61）生成210组完整预期输出，含上下端素数、无相邻素数、并列答案、低端百万跨度和终点INT_MAX的百万跨度。完整原程序和当前 header、NDEBUG、展开、抄写四种形式均匹配逐字输出。所有形式通过普通构建及 ASan/UBSan。

报告见 `verification/prime-source-normal.json` 和 `verification/prime-source-sanitizer.json`，含来源与当前被测代码哈希。本批不修改算法，不重申全库正确性或线上资源通过；历史 `phi`、`mu` 等测试仍是独立证据。§2.2 合数分解不是该父项的子项，尚未因本次核对而更改状态。
