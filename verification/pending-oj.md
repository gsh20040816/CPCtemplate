# 待在线评测

以下提交驱动尚无本库的新 AC 记录；列表由当前 verify/ 与 oj.json 对照生成。

- `verify/library_checker/intersection_intersection.classic.cpp`
- `verify/library_checker/intersection_intersection.compact.cpp`
- `verify/library_checker/intersection_zassenhaus.classic.cpp`
- `verify/library_checker/intersection_zassenhaus.compact.cpp`
- `verify/luogu/CF1100F.classic.cpp`
- `verify/luogu/CF1100F.compact.cpp`
- `verify/luogu/CF118E.classic.cpp`
- `verify/luogu/CF118E.compact.cpp`
- `verify/luogu/CF600E.classic.cpp`
- `verify/luogu/CF600E.compact.cpp`
- `verify/luogu/P1117.classic.cpp`
- `verify/luogu/P1117.compact.cpp`
- `verify/luogu/P1972.classic.cpp`
- `verify/luogu/P1972.compact.cpp`
- `verify/luogu/P2495.classic.cpp`
- `verify/luogu/P2495.compact.cpp`
- `verify/luogu/P2617.classic.cpp`
- `verify/luogu/P2617.compact.cpp`
- `verify/luogu/P2633.classic.cpp`
- `verify/luogu/P2633.compact.cpp`
- `verify/luogu/P2731.classic.cpp`
- `verify/luogu/P2731.compact.cpp`
- `verify/luogu/P2860.classic.cpp`
- `verify/luogu/P2860.compact.cpp`
- `verify/luogu/P3373.classic.cpp`
- `verify/luogu/P3379.euler.classic.cpp`
- `verify/luogu/P3379.euler.compact.cpp`
- `verify/luogu/P3379.lifting.classic.cpp`
- `verify/luogu/P3379.lifting.compact.cpp`
- `verify/luogu/P3379.offline.classic.cpp`
- `verify/luogu/P3379.offline.compact.cpp`
- `verify/luogu/P3386.classic.cpp`
- `verify/luogu/P3386.compact.cpp`
- `verify/luogu/P3398.classic.cpp`
- `verify/luogu/P3398.compact.cpp`
- `verify/luogu/P3649.classic.cpp`
- `verify/luogu/P3649.compact.cpp`
- `verify/luogu/P3809.classic.cpp`
- `verify/luogu/P3809.compact.cpp`
- `verify/luogu/P3812.classic.cpp`
- `verify/luogu/P3812.compact.cpp`
- `verify/luogu/P4151.classic.cpp`
- `verify/luogu/P4151.compact.cpp`
- `verify/luogu/P4779.classic.cpp`
- `verify/luogu/P4779.compact.cpp`
- `verify/luogu/P4782.classic.cpp`
- `verify/luogu/P4782.compact.cpp`
- `verify/luogu/P5491.classic.cpp`
- `verify/luogu/P5496.classic.cpp`
- `verify/luogu/P6113.classic.cpp`
- `verify/luogu/P6113.compact.cpp`
- `verify/luogu/P7771.classic.cpp`
- `verify/luogu/P7771.compact.cpp`
- `verify/poj/1330.classic.cpp`
- `verify/poj/1330.compact.cpp`
- `verify/poj/1330.lifting.classic.cpp`
- `verify/poj/1330.lifting.compact.cpp`
- `verify/poj/1470.classic.cpp`
- `verify/poj/1470.compact.cpp`
- `verify/poj/1637.classic.cpp`
- `verify/poj/1637.compact.cpp`
- `verify/poj/2117.classic.cpp`
- `verify/poj/2117.compact.cpp`
- `verify/poj/2337.classic.cpp`
- `verify/poj/2337.compact.cpp`
- `verify/poj/2942.classic.cpp`
- `verify/poj/2942.compact.cpp`
- `verify/sgu/101.classic.cpp`
- `verify/sgu/101.compact.cpp`
- `verify/uva/796.classic.cpp`
- `verify/uva/796.compact.cpp`

## 已解决的提交异常

- P8436、P3806 曾在旧页面的文件及文本提交入口返回 `The route object cannot be resolved`。2026-09-12 在新标签页重新提交后，两套版本均 AC；具体记录在 oj.json。错误原因尚未确定。
- P6113 动态版之前因 10 秒请求超时未生成记录，可在新标签页重试。
- P3834 动态版验证码已由用户当次授权处理，记录 297520290 已 AC；传统版随后以 297520299 获得 AC。

OJ 只验证驱动实际调用的接口。点分治 P3806 只核验距离存在性，完整计数与零权等扩展仍由本地独立测试提供证据。

- `verify/luogu/P2495.classic.cpp` 与 `verify/luogu/P2495.compact.cpp`：已对实际打包程序做枚举删边验证，在线评测待完成。
- 2026-09-12 曾因 Mac 锁定暂停 UI；之后已可读取，但在准备 P3384 文件时工具报告用户改变了 Firefox 状态，已暂停输入，未提交。

- P3919 双风格已 AC：动态版 297520221，传统版 297520224；P3834 双风格打包程序已检查区间第 k 小，动态版已 AC（297520290），传统版已 AC（297520299）。两类模板分别验证，不混用版本语义。

- P3384 双风格已 AC：动态版 297520172，传统版 297520179，验证递归 HLD + 仿射线段树的路径/子树加法及求和；传统 HLD 的接口为 Heavy_Light_Decomposition<N> + Init(n)。

- P3386 双风格驱动已完成本地检查。Hopcroft–Karp 匹配与最小点覆盖由独立穷举测试验证，尚未在线提交。

- P4779、P4782 双风格驱动已按官方题面核对输入输出，对四份实际打包程序分别完成 100 组独立随机检查；尚未在线提交。P4779 使用 Bellman–Ford 距离参照，P4782 枚举赋值并核验输出方案。接口级完整边界检查见 tests/graph_contracts.cpp。

- P6577 双风格现已 AC：动态版 297520123，传统版 297520132。此前提交曾返回 `The route object cannot be resolved`；2026-09-12 再次从新标签页提交成功，原因未确认。可选匹配、无解与完整 int64 边权仍由独立子集 DP 检查，不能由完美匹配题的 AC 代替。

- P4720 双风格已在线 AC：动态版 297520142，传统版 297520151。题面范围为 1≤k≤n≤10^18、2≤mod≤10^6；模数 1、越界 k、uint64 最大值与重复初始化仍由 tests/exlucas.cpp 验证。

- P4781 双风格已 AC：动态版 297520159，传统版 297520164。连续横坐标模式与整数幂和应用另外由 tests/interpolation.cpp 验证，不计入 P4781 的 OJ 覆盖范围。

- P4195 双风格已于 2026-09-12 在线 AC：动态版 297520101，传统版 297520104。此前 P6577 的路由错误本次未出现；未确认错误原因。算法支持有符号输入及模数至 10^12 的扩展边界，由 tests/discrete_log.cpp 独立验证，不能由题面 10^9 范围的 AC 外推。

- P3834 动态版验证码已处理，记录 297520290 获得 100 分 AC；传统版记录 297520299 同样获得 100 分 AC。两份打包程序的排序切片对拍见 verification/persistent-kth-driver-tests.txt。

- P4174 最大权闭合子图双风格已 AC：动态版 297520300，传统版 297520304。OJ 验证最优权值；返回选点集合、极端负权及一般依赖环仍由本地证书检查覆盖。
- P5491 动态版验证码经用户当次授权处理，记录 297520354 获得 100 分 AC；传统版尚未提交。

- P3379 离线 LCA 动态版提交出现验证码，已请求当次确认，尚无评测记录；传统版未提交。
