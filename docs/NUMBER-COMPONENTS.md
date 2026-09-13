# 数论基础组件拆分

NumberTheory 原来跨越模幂、判素、Bézout、逆元、CRT、类欧几里德多个页面，现将实现移到独立头文件，旧类只作兼容转发。

| 组件 | 契约与位置 |
| --- | --- |
| Mod64 | uint128模乘与完整uint64模幂；快速幂页面的基础组件 |
| Prime64 | 继承Mod64，七底数确定性64位Miller–Rabin；素数页面 |
| extended_gcd | 非负输入≤2^63，int128系数；Bézout与不定方程页面 |
| mod_inverse | 任意正long long模数；模逆元页面 |
| crt_merge | 逐项广义CRT，失败状态与周期溢出明确；CRT页面 |
| floor_sum | signed64系数、n/m≤10^9、int128结果；类欧几里德页面 |

原NumberTheory::mul/power/prime/exgcd/inverse/crt/floor_sum接口仍可使用。当前模板内部调用已直接使用对应组件；PollardRho仅在判素、模乘处引用Prime64/Mod64，线性方程、批量逆元、Garner、原根等不再需要整块NumberTheory代码。主要调用者仍保持原来的下标、取模及异常约定。

crt_merge的r与m须为不同变量。无解和周期溢出都会先规范化r，但m不变；不能将失败后的状态当作整个系统的解。mod_inverse在模数1返回0，无逆元返回-1。extended_gcd(0,0)返回0并给出(1,0)。floor_sum的负系数使用数学向下取整，不是C++截零除法。

新头文件显式包含cassert，独立编译不能依赖其他头文件偶然带入断言宏。手册分册的通用包含约定也同步。

直接组件测试使用cpp_int模乘及powm参考、试除判素、Bézout大整数证书、逆元/CRT穷举和有符号整除和枚举。现有判素分解、CRT系统、floor_sum、线性方程/同余、批量逆元、Garner、原根、模数准备、高次剩余和代数组合等14组回归在固定历史基线旁运行，普通及ASan/UBSan均通过。

P4777及UVa10006驱动同步使用独立组件，两个驱动测试补齐SANITIZE开关并拒绝消毒器标准错误输出。因数分解驱动也再次检查。日志在verification/number-components-*、number-split-regression-*及对应split-driver-*中。

源码拆分不自动转移历史AC为新入口的线上验证；现有归档与当前源码差异继续由oj-source-audit报告记录。其余四个复合条目与整体验证工作仍未完成。
