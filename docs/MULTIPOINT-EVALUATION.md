# 任意点多项式求值

新增 `MultipointEvaluation`，位于 [multipoint_evaluation.hpp](../src/compact/multipoint_evaluation.hpp)。这是 issue #1 的任意点求值缺项，正式使用程序对应 [Library Checker Multipoint Evaluation](https://judge.yosupo.jp/problem/multipoint_evaluation)，登记为 `example-211`。本组件只求值，不提供快速插值；原有 `chirp_z` 继续负责等比点，`Lagrange` 继续负责其已有插值查询接口。

## 接口与约定

```cpp
using P = MultipointEvaluation;
P::Poly x = {0, 1, 2, 1}, f = {1, 2, 3};
P tree(x);
auto a = tree.evaluate(f); // {1, 6, 17, 6}
auto b = tree.evaluate({7}); // 同一批点，全部返回 7
```

- 固定素数模数 `998244353`；`Z=ModInt<998244353>`，`Poly=vector<Z>`，系数按升幂排列
- 构造函数读取点数组并构造乘积树，不保存对调用者数组的引用，不修改点数组
- `evaluate(Poly f) const` 按值接收多项式，返回恰好 `x.size()` 个点值，顺序与输入相同。普通左值调用不修改输入；调用者主动 `move(f)` 则遵循通常的移动语义
- 允许重复点、零点、空点集、空多项式、全零多项式以及高次端零系数。空多项式视为零；空点集返回空数组
- 同一棵树可连续求多个多项式的点值；求值过程不改变树。`n`、`p`、`build`、`eval` 是内部表示及递归辅助，不作为独立调用或修改接口
- 原始输入先构造成 `Z` 归一化；本组件不接受浮点系数，也没有运行时换模数的接口

## 依赖与容量

直接复用 `PolynomialDivision::divide`，取其返回 pair 的余式，不新增或修改逆级数、NTT、模整数及除法实现。抄写链为 `ModInt → NttConvolution → FpsInverse → PolynomialDivision → MultipointEvaluation`。

设 `n=f.size()`、`m=x.size()`。统一充分条件为 `n≤2^22`、`m≤2^22−1`，代码在构造及求值入口检查。长度包括尚未去掉的高次零；不会先删零再绕过长度限制。乘积树根多项式有 `m+1≤2^22` 个系数，所有除数均非零且为首一多项式；任一次带余除法的两个输入都不超过既有除法的 `2^22` 项上限。既有除法通过反转求逆，内部完整卷积长度不超过 NTT 容量 `2^23`。树构造的乘积长度至多 `m+1`。

这些是代数和下标运算的充分容量条件，不是承诺在评测机内存及时间限制内跑到该上界。`4*max(1,m)` 和递归区间下标和在此范围内均可由 `int` 表示；系数乘法沿用 `ModInt` 的 `long long` 运算，`(998244353−1)^2<2^63−1`。本批最大实测点数和系数数均为官方规模 `131072`；未实测所有点数达到 `2^22−1` 的完整树。

## 原理、重复点与复杂度

对半开区间 `[l,r)` 保存 `P[l,r](X)=∏(X−x[i])`。叶子是 `{−x[i],1}`，父节点直接卷积左右孩子，不补虚构点，也不要求点互异。

求值时将当前多项式对本节点乘积取余，再把余式传给左右孩子。如果原多项式次数已经更低，则直接传下去。因为每个孩子的乘积整除父节点的乘积，逐层取余与直接对孩子取余等价。最终对 `X−x[i]` 的余式就是 `f(x[i])`。重复点对应重复因子，仍满足整除关系，不需要计算点差的逆元；不会引入快速插值才有的互异点前提。

零余式直接返回，输出数组预先填零；常数余式可以填满整个对应区间。叶子余式必定为常数或零，递归自然终止。对多项式先去高次零，只改变求值入口的局部副本。

- 构造：`O(m log²(m+1))` 时间，树永久占用 `O(m log(m+1))` 空间
- 每次求值：`O(n log(n+1)+m log²(m+1))` 时间；其中长多项式对根乘积的首次取余不可遗漏
- 含保存的树与求值临时量，总空间 `O(n+m log(m+1)+1)`；除保存的树外，深度优先求值的临时多项式总量为 `O(n+m+1)`
- 递归深度 `O(log(m+1))`。重复调用复用乘积树，但不缓存除数的逆级数；不声称额外的多次查询加速界

## 正式题目与覆盖边界

[官方题面源码](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/polynomial/multipoint_evaluation/task.md)与 [verifier](https://raw.githubusercontent.com/yosupo06/library-checker-problems/master/polynomial/multipoint_evaluation/verifier.cpp)规定 `1≤n,m≤131072`，系数与点在 `0..998244352`，最高次系数非零；没有互异点要求。完整驱动 [multipoint_evaluation.compact.cpp](../verify/library_checker/multipoint_evaluation.compact.cpp) 按系数个数读取，输出恰好 `m` 个标准模数代表及一个结尾换行。空输入等扩展契约由核心测试负责，不冒充官方合法输入。

`docs/template-problem-reviews.json` 已有 QOJ 622 的历史审题记录，但系数和点的读取上界尚待重新核对；本批没有给该题新增驱动或线上证据。附件 §5.1 实际第 130 页只给出一般公式及朴素/快速插值复杂度说明，没有完整快速实现。新增求值组件不表示该页提到的快速插值已补齐，也不扩张其他附件主题的覆盖。

## 本地独立验证

`tests/multipoint_evaluation.cpp` 包含：

- 9,452 次小规模独立整数 Horner 核对：二元系数枚举、随机长短数组、重复及全相等点、0/1/−1、空/零/常数多项式、高次零、二次幂邻近与奇数长度，以及由既有 `Z` 构造器归一化的 signed64 输入
- 1,800 组小树构造；非空树的根乘积另用整数二次乘法构造核对。每棵树保存所有节点的副本，在五次连续求值后逐系数核对未被改变，同时核对调用者输入未被修改
- `n=m=131072` 的稠密全一及交替系数，以有限几何和公式和独立整数模幂核对全部点值，包含特殊点和重复点
- 官方最大 `m=131072` 的全相等横坐标，以及 17 项对 131072 点、131072 项对 17/1/0 点的非对称输入
- `65537` 项与 `65535` 点的稀疏高次多项式，用单项式模幂求和核对；补到 131072 项高次零后结果必须不变
- 同一翻译单元包含并调用除法、FPS 与 `chirp_z`，各自用整数参考或明确系数结果核对，不把组件互相调用的相等结果作为唯一正确性依据

执行命令：

```sh
mkdir -p build/multipoint-evaluation
g++ -std=c++20 -O2 -Wall -Wextra -Wshadow tests/multipoint_evaluation.cpp -o build/multipoint-evaluation/core-normal
build/multipoint-evaluation/core-normal
g++ -std=c++20 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer tests/multipoint_evaluation.cpp -o build/multipoint-evaluation/core-sanitizer
for stage in small dense repeated sparse composition; do
    ASAN_OPTIONS=detect_leaks=0:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 build/multipoint-evaluation/core-sanitizer "$stage"
done
```

双模式结果分别登记在 `verification/multipoint-evaluation-core-normal.json` 与 `verification/multipoint-evaluation-core-sanitizer.json`，绑定测试、完整依赖、驱动及二进制哈希。上述核心测试与完整驱动、精确打印程序、固定版本官方数据的报告分开，不把本地检查或本机用时称为在线 AC、官方限时通过或速度排名。关闭泄漏检查时不声称做过泄漏验证。

首个合并 sanitizer 进程被 `SIGKILL` 终止，没有 ASan/UBSan 诊断，原因未确认；`verification/multipoint-evaluation-core-sanitizer-incomplete.json` 保留该次不完整执行，不作为通过证据。后续以相同语料按上面五个阶段分进程执行，限制单次测试进程的存活范围；核心与驱动未因该次终止而改写。

独立完整驱动测试由 `tests/multipoint_evaluation_application.py` 负责：普通与 ASan/UBSan 下，独立驱动和精确打印的 `example-211` 各执行 422 组完整输入输出检查。固定官方参考版本 `e64660561a995c357cdc61ddee1bde68b80528db` 的全部 11 组数据，同样在独立驱动与精确打印程序的两个模式下通过官方 checker；错误输出负对照被拒绝，输入及参考答案哈希与固定清单核对一致。

对应证据为 `verification/multipoint-application-{normal,sanitizer,usage-normal,usage-sanitizer}.json` 与 `verification/multipoint-official-{normal,sanitizer,usage-normal,usage-sanitizer}.json`。这些只证明列明程序在这些本地语料上的结果，线上 AC、QOJ 622 的解析器边界、官方机器上的限时表现及速度排名仍待完成。


## 完整程序、官方数据与最终版面

`tests/multipoint_evaluation_application.py` 以独立整数 Horner 和最大规模闭式输入检查完整驱动及精确打印文本。每种程序、每种模式各 422 组，包括独立变化的 n/m、重复点和六组最大规模结构输入。四份 `verification/multipoint-application*.json` 绑定实际程序和测试脚本哈希。

固定 Library Checker 上游 `e64660561a995c357cdc61ddee1bde68b80528db` 的全部 11 组生成数据已由官方 checker 接受；原驱动和精确打印文本均执行普通与 ASan/UBSan。全部 22 份输入/答案文件与上游 hash.json 一致，错误输出负对照被 checker 拒绝。见 `verification/multipoint-official-provenance.json`、`multipoint-official*.json`。这里是本地官方数据及 checker 结果，不是线上 AC、OJ 限时或速度排名。

中央精确使用示例检查也通过。当前本库为 205 算法、211 份用法；本条属于正式模板题用法，快速插值仍未实现，不能将整个 OI Wiki 联合页面记为完全覆盖。QOJ 622 的待确认输入边界与提交仍保持独立。

本批数学册及总册重建，新核心在 build/eval 方法边界分两页、行号续接，完整 main 独立同页；前后相邻内容共 10 页实际渲染检查，原字号不变。其他六册经文本、注释和命名目的地比对后保留原 PDF 字节。八册最终日志无警告，1034 组依赖名称/页码/章节及 16 处跨册跳转通过；详情 `verification/multipoint-layout.json`。未重新执行整个仓库全量双模式回归，不扩大历史收据范围。
