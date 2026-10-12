# 斯特林数与斯特林反演

本批处理 issue #18：两类定义、组合意义、递推、边界、生成函数；有/无符号约定；四种快速行列求解；普通幂与升降阶乘转换；两对反演公式、推导及手算/计数应用。正文集中在 `docs/knowledge-stirling.tex`，与四个源代码条目及用法统一排入总册和数学分册的“斯特林数与斯特林反演”，旧附录的重复内容已迁出。

## 接口和限制

- `stirling_first_row<mod,primitive>(n)`：无符号第一类整行，倍增与泰勒平移，O(n log n)。
- `stirling_second_row<mod,primitive>(n,m)`：第二类第n行的0..m前缀，容斥卷积，O(m log m + m log mod)，n支持unsigned long long。
- `stirling_first_column(N,k)`：无符号第一类0..N整列，固定模998244353。
- `stirling_second_column(N,k)`：第二类0..N整列，固定模998244353。

整列使用单位常数项生成函数的快速幂，再乘n!/k!。m=N-k+1，时间O(N+m log m)、空间O(N)；N>=0且N<2^22，k>=0。k>N返回零列；k=0仅零号元素为1。依赖FpsPower→FpsFunctions→FpsInverse→NttConvolution→ModInt。模数与NTT容量及逆元约束见打印条目，整列不能直接改用洛谷列题的167772161。

## 验证

核心与精确抄写版均以递推表核对69158个行列系数、第一/第二类矩阵互逆以及50万规模边界，普通和ASan/UBSan通过。每种列的14组固定上游官方生成数据均经官方checker接受，两种构建均通过，故意错误输出被拒绝。完整用法433/434另验证0列、零规模、有符号输出与只输出k..N的协议。两种原整行洛谷完整驱动也再次通过其原最大规模多项式恒等式回归。

本轮以当前精确抄写核心新提交四份C++20程序，全部实际AC，均匿名提交：

| 算法 | 记录 | 最慢时间 | 峰值内存 |
| --- | --- | --- | --- |
| 第一类整行（输出有符号） | [410002](https://judge.yosupo.jp/submission/410002) | 589 ms | 16.26 MiB |
| 第二类整行 | [410001](https://judge.yosupo.jp/submission/410001) | 392 ms | 14.44 MiB |
| 第一类整列（输出有符号） | [409999](https://judge.yosupo.jp/submission/409999) | 4457 ms | 31.32 MiB |
| 第二类整列 | [410000](https://judge.yosupo.jp/submission/410000) | 4407 ms | 31.32 MiB |

原始页面文本、逐点数据、实际提交源文件及SHA在 `verification/stirling-columns-online.json` 和对应 `verification/submitted/LC-*.cpp`，与原洛谷历史AC分开保存。

性能提醒：两种整列复用通用FPS链；本地同GCC16、C++17/O2，最大规模小k官方输入各交替3次，中位耗时分别约为官方参考6.06倍和4.92倍，均超过80%慢速提醒线。上游参考有名为integral的函数，在C++20与标准concept歧义，故本地公平对照统一C++17；线上提交仍为C++20，均通过10秒时限。此对照不是OJ排名，不宣称最优常数。

反演部分提供两对完整公式与证明、a=(1,2,3,4)→b=(1,2,5,15)→a的手算，以及Bell数/带权块数应用。没有把逐行点积误称为任意序列的O(NlogN)完整变换。

目前320个组件、434份打印完整用法。本issue的四种行列和反演要求单独核验；不据此声称OI-Wiki全部斯特林扩展、全库来源或其他issue已全部覆盖。
