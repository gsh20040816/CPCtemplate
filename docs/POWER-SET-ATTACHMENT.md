# 附件集合变换与大指数多项式快速幂

对应 issue #11 的 5.10–5.11，实际 169–178 页；已查看题意截图、变换公式及指数读入代码。5.12 拆系数浮点 FFT 不在本批实现范围，不能因为已有精确 CRT 卷积就标记该算法完成。

## OR / AND / XOR

169–171 页对应 [P4717](https://www.luogu.com.cn/problem/P4717)，分别求 OR、AND、XOR 卷积。现有 SetConvolution 已提供三种原地正/逆变换及 multiply；长度为正的二次幂，长度 1 合法。

OR 是子集和变换，对每一位的二元组 (u,v) 作 (u,u+v)，逆变换相减；AND 是超集和，对应 (u+v,v)。变换后乘积展开正好把所有 i|j=s 或 i&j=s 的项计入，再做 Möbius 逆变换恢复每个集合的系数。XOR 使用字符 (-1)^popcount(s&i)，字符的乘积对应下标异或；单层变换 (u+v,u-v) 的平方为 2I，所以每层逆变换乘 1/2。

OR/AND 不需要除法，支持合数甚至偶数模数；XOR 需要 2 可逆，当前入口明确要求模数为奇数，用 (mod+1)/2 而非 Fermat 逆元。因此 mod=9 的 XOR 也正确，mod=8 的 XOR 则不接受。模数范围 2..INT_MAX；数组长度和分层循环保持 int 范围。

移除 tests/set_convolution.cpp 对 classic 的依赖；保留直接子集/超集/字符求和、下标对枚举卷积、逆变换、6561 组四项输入穷举、六种模数的 900 随机组、18 位张量恒等式。分层不相交子集卷积也保留独立子掩码参考与 P6097 回归，但它不是附件 5.10 本身的内容。完整程序测试新增 SANITIZE/CPC_SANITIZE 支持及 stderr/超时审计：P4717 50 随机组与 17 位最大规模、P6097 50 随机组与 20 位最大规模，均双模式通过。模板源码未变。

## 大指数幂函数

附件的 Quick_Power 为 exp(k*log(a))，读入十进制指数时仅维护 k mod p，适用 [P5245](https://www.luogu.com.cn/problem/P5245) 的 a[0]=1 约束。原先 FpsFunctions 候选条目没有真正提供幂函数，本批新增独立 FpsPower，并覆盖 [P5273 加强版](https://www.luogu.com.cn/problem/P5273) 的任意首项/前导零和 k=0。

`FpsPower::power(a,exponent,n)` 返回前 n 项，模数固定 p=998244353。exponent 是非空十进制数字 string_view，允许前导零；整数可传 to_string(k)。n=0 返回空；零次幂（含零多项式的零次幂）定义为单位多项式。0<=n<=2^22，输入系数数组长度须在 int 范围；不足 n 项补零，多余项忽略。

若真实 k>0 且 a 的前 n 项全零，结果全零。否则设首个非零项次数为 s、系数为 c，将 a 写作 x^s*c*h，其中 h[0]=1。若 s*k>=n 则返回全零；否则

`a^k = x^(s*k) * c^k * exp(k*log(h)) (mod x^n)`。

指数需要三份信息：

1. k mod p：用于 k*log(h) 的域内乘法；由于 n<p，求导/积分所需的 1..n-1 可逆。等价地，h(x)^p=h(x^p)=1 (mod x^n)，所以单位首项部分只依赖 k mod p。
2. k mod (p-1)：用于非零标量 c 的幂。
3. min(k,n)：用于判定真实零次幂和真实位移。不能用前两份余数判零或移动下标。

判断 s*k>=n 使用除法比较 `cap>(n-1)/s`，先证明乘积小于 n 后才求 s*cap，避免大指数溢出。s=0 时位移为零；s>0 且未提前返回时 cap 就是真实指数。将 h 截到 n-s*k 项，归一化、ln/exp，再左移和乘标量。十进制位数 L，时间 O(L+n log(n+1))，额外空间 O(n)。不支持负数、小数指数。

## 证据与使用程序

- 6558 组长度 0..6、系数 0/1/-1、指数 0..5 全枚举；1600 组独立整数二次卷积二进制幂，包含长/短输入与任意 leading zeros。
- ULLONG_MAX、p-1、p、p+1、p²；十进制 10^100000 的 500000 项二项式闭式；单项式位移恰好 n-1/n；空输入、全零、100001 个零字符指数。
- P5245/P5273/LC 各 100 个完整程序随机输入及一个最大规模闭式。前两题 n=100000、指数 100001 位；LC n=500000、指数 10^18。均普通/ASan/UBSan 通过。
- 固定 Library Checker 提交 e64660561a995c357cdc61ddee1bde68b80528db 的 pow_of_formal_power_series 共 37 组官方生成测试，包括 overflow_killer、M_zero、前导零和 hack；普通/sanitizer 均被官方本地 checker 接受，并确认 checker 拒绝错误输出。
- 三个完整驱动使用相同的输入格式；打印册只收录一份共用主程序 example-120，避免重复抄写同样代码。全部驱动仍保留在 verify 下。

本地报告在 verification/power-set-attachment.json、verification/fps-power-official*.json；未新增在线 AC 或速度排名。8 册 PDF 及相关使用页另外核验。此前已经通过的原实现线上记录不改写成新实现已 AC。
