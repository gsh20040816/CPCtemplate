# 线性筛与模逆元：两份直接应用

本批复用已有组件，不改核心。P2158 和 P1082 都是历史比赛应用，不计正式模板题覆盖，也不声明新的线上 AC 或速度排名。

## LinearSieve：P2158 仪仗队

[官方题面](https://www.luogu.com.cn/problem/P2158)范围为 1≤N≤40000，样例 4→9。按角落原点的模型，坐标落在 [0,N−1]²，原点本身不计；射线上最近的非零整点恰好满足 gcd(x,y)=1。N=1 时没有其他点，输出 0；这是边界推导，不冒充官方样例。

令 M=N−1≥1，两条坐标轴各有一个可见点，正坐标对角线上只有 (1,1)。固定最大正坐标 q≥2，一侧有 φ(q) 个互素点，另一侧对称。因此总数为 3+2∑[q=2..M]φ(q)=1+2∑[q=1..M]φ(q)，其中 φ(1)=1。

example-218 构造 LinearSieve(N−1)，直接累加 phi，用 long long 保存答案。预处理与累加 O(N)，空间 O(N)。本例不独立验证 prime、lp、mu 等其余成员，也不因为整个 number_theory.hpp 被展开就算作其他组件覆盖。

`tests/totient_lattice_application.py` 用逐格 gcd 统计检查 N=1..100，再用埃氏倍数更新与逐数试除两种独立方法核对 φ(1..40000)。每种模式的登记、完整展开和最小抄写程序各运行 215 组输入，另一个专用程序逐项输出 40000 个 phi 值。最大 N=40000 的答案为 972659433。

普通与 ASan/UBSan 合计 1290 次应用执行、2 次单独 phi 输出执行；两模式合计 80000 个 phi 值分别与参考核对。记录见 `verification/totient-lattice-{normal,sanitizer}.json`。

## mod_inverse：P1082 同余方程

[官方题面](https://www.luogu.com.cn/problem/P1082)给定 2≤a,b≤2×10⁹，保证 ax≡1 (mod b) 有解，求最小正解；样例 3 10→7。有解等价于 gcd(a,b)=1，b≥2 保证归一化逆元不为 0，所以已有 mod_inverse(a,b) 的 [0,b−1] 代表恰好就是最小正解。

example-219 先抄 extended_gcd，再抄 mod_inverse 和 main。模数允许合数，不能擅自改为 a^(b−2)；a 可能大于 b，由接口归一化。extended_gcd 只作依赖，不额外登记直接调用覆盖。一般接口还处理不可逆、负输入和模数 1，这些不在本题保证范围，不与官方域用例混为一谈。

`tests/mod_inverse_application.py` 对 [2,40]² 的全部 900 个互素对逐个枚举正解，其余使用 Python 任意精度逆元并核查乘积余数，包括合数、a>b、余数为 1、最大边界、相邻 Fibonacci 数与固定种子随机输入。每种形态、每种模式 1408 组，完整驱动、精确登记和最小抄写共 8448 次执行通过。

记录见 `verification/mod-inverse-application-{normal,sanitizer}.json`。两套最终测试都使用编译器默认 PIE、默认 ASan quarantine；仅因运行环境的 ptrace 限制关闭 LSan，不声明泄漏检查。初步 scratch 测试不替代最终三形态、固定源码的证据。最终报告保留源码、编译器、登记和夹具前后指纹。
