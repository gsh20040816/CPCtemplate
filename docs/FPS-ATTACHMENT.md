# 附件多项式求逆、除法、开根与 ln/exp

本批核对 issue #11 附件 5.5–5.9，实际 136–169 页。标题、题意和推导截图已人工查看，接口同时对照提取代码。题目对应求逆、[P4512 带余除法](https://www.luogu.com.cn/problem/P4512)、[P5205 开根](https://www.luogu.com.cn/problem/P5205) 及常数项为 1/0 的 ln/exp；不据此声称附件后面的快速幂、三角函数、多点求值已完成。

## 求逆、对数、指数

现有 FpsInverse 按 `b <- b*(2-a*b)` 倍增。若 `a*b=1-e` 且 e 可被 x^m 整除，则更新后误差为 e²，因此正确项数翻倍。输入常数非零，n>0；不足项补零，只处理所需前缀。固定模数 998244353，n<=2^22 是所有完整卷积不超过 2^23 的统一充分条件。

FpsFunctions 的 ln 使用 `integral(a' * inverse(a))`，exp 使用 `b <- b*(1+a-log(b))`。ln 的常数项须为 1；exp 的常数项须为 0（空输入也表示零）。积分中的 1..a.size() 须可逆，所以 integral 增加 a.size()<mod 的断言。

本批将 ln 先截到 n 项再求导。旧版会对完整输入求导；即使只求一项，长于 NTT 容量的输入也可能导致无关卷积容量断言。现在超出 n 的尾项完全不参与，时间 O(n log(n+1))、额外空间 O(n)，无需 a.size()<=n。输入数组长度仍要求能用 int 表示。现有测试以独立三角系数递推为参考，覆盖随机长/短输入、微积分、空 exp、131072 项和完整驱动 500000 项闭式；新增输入长度 2^23+1、只求一项的回归。没有更换为只做互逆一致性测试。

## 带余除法

新增 `PolynomialDivision::divide(a,b)` 返回 `{q,r}`，满足 a=q*b+r、deg(r)<deg(b)。模数固定 998244353，系数从低次到高次。输入按值传入，先删除高次零；零多项式用空 vector。除数必须非零，允许零被除式、常数除数及 deg(a)<deg(b)。`trim(a)` 可单独使用。

设 A=deg(a)、B=deg(b)、k=A-B+1。反转多项式后有

`rev(a) = rev(b)*rev(q) (mod x^k)`，

因为反转余式的最低次数至少为 k。b 的最高次系数非零，故 rev(b) 可求逆。取乘积前 k 项再反转即得 q；随后 r=a-q*b。商的最高项不会为零，余式显式去高次零。输入各长度<=2^22，所有完整卷积结果长度<=2^23；时间 O(N log(N+1))、空间 O(N)。低次被除式的提前返回也是规范化结果。

[P4512](https://www.luogu.com.cn/problem/P4512) 输入的是次数，输出规定数量的系数，因此驱动对 q、r 补零。[Library Checker](https://judge.yosupo.jp/problem/division_of_polynomials) 输入系数个数，输出规范化后的长度和系数；空商/余式输出长度 0 和空行。两种协议分别给出完整使用程序。

## 一般前导零开根

新增 `FpsSqrt::sqrt(a,n)` 返回 `optional<Poly>`：无解为 nullopt；有解恰好 n 项，n=0 是有值的空向量。只看前 n 项，短输入补零。

若输入前 n 项全零，返回全零。否则令 k 为首个非零项的次数：k 为奇数时不可能是平方；k 为偶数时，首个非零系数必须为二次剩余。通过已有 mod_sqrt 取两个根中较小者 c，令 a=x^k*h，从 c 开始对 h 做 Newton 迭代

`b <- (b+h/b)/2 (mod x^m)`。

旧 b 的常数非零，故除法是逆级数乘法。若 e=b²-h 从 x^s 起，更新后的误差为 e²/(4*b²)，正确项数翻倍。求 h 的根至 n-k 项后左移 k/2，最后补到 n 项；剩余末 k/2 项不影响平方模 x^n，固定取零。返回的是确定选择的一个解，不是所有根，也不声称总只有两个截断根。

n<=2^22，变换中最大的完整卷积长度为 2m-1。时间 O(n log(n+1)) 加一次模开根的期望 O(log mod)，空间 O(n)。[P5205](https://www.luogu.com.cn/problem/P5205) 保证 a[0]=1，结果首项为 1；[Library Checker](https://judge.yosupo.jp/problem/sqrt_of_formal_power_series) 允许任意输入和无解，另给完整程序。

## 本地证据

- 3000 组独立整数长除法，包括高次零、零被除式、常数除数和大小反转；50 万项已知商/余式的稀疏除数构造。
- 2400 组独立二次截断平方，检查选择的符号与自由尾项；6480 个最低次数/剩余性情形；空、短、长输入；20 万项短输入开根与 50 万项 `sqrt((1-x)^-2)=(1-x)^-1`。
- P4512/P5205 各 150 个独立完整输入和一个 10 万规模构造；普通与 ASan/UBSan 均通过。
- 官方 Library Checker 固定提交 e64660561a995c357cdc61ddee1bde68b80528db，每题 35 个生成测试，普通与 sanitizer 共 140 次官方本地 checker 接受，另验证 checker 拒绝错误输出。报告在 `verification/polynomial-division-official*.json`、`verification/fps-sqrt-official*.json`。
- 普通对拍报告 `verification/fps-attachment.json`；新增四份打印使用程序及原 ln/exp 使用程序重测。

以上是本地结果，不是在线 AC 或线上速度排名。OI Wiki 的 [Newton 迭代](https://oi-wiki.org/math/poly/newton/) 与 [初等函数](https://oi-wiki.org/math/poly/elementary-func/) 用于分类和推导核对，不代表这两页的全部内容已覆盖。
