# 官方数据的本地验证

`tools/official_cases.py` 接受已生成数据的 Library Checker 固定版本仓库、题目 ID、驱动文件和 JSON 报告路径。它不会提交 OJ，也不把本地用时当作线上排名。

```sh
CXX=g++-16 python3 build/library-checker-reference/generate.py -p range_affine_range_sum
python3 tools/official_cases.py build/library-checker-reference range_affine_range_sum verify/library_checker/range_affine_range_sum.compact.cpp verification/lazy-official-local.json
python3 tools/official_cases.py build/library-checker-reference range_affine_range_sum verify/library_checker/range_affine_range_sum.compact.cpp verification/lazy-official-sanitizer.json --sanitize
```

仓库必须停在待审查的固定 commit，且不能修改已跟踪参考文件。测试生成和参考答案由上游 `generate.py` 完成。脚本检查各输入名字与 `info.toml` 中生成器/次数完全一致，防止只跑部分数据便宣称全过。

每组数据分别运行当前驱动打包文件，再调用该题 checker。报告保存固定版本、元数据、checker 源码和二进制、打包源码、输入、标准答案与输出的 SHA256。另用故意错误的答案验证 checker 返回拒绝状态。失败或超时不会写出通过报告。

macOS 记录每组进程的 resident bytes 和墙钟时间，包含启动开销；这些数值受本机负载、编译器、系统和测试运行顺序影响，不能与 OJ 的 Linux 用时直接比较。Sanitizer 报告必须和普通报告区分。

## 已执行

通用递归懒标记线段树的 `range_affine_range_sum` 驱动，在参考版本 `e64660561a995c357cdc61ddee1bde68b80528db` 的 19 组官方数据上，普通和 ASan/UBSan 都通过官方 checker，包括最大随机数据。普通本轮最大墙钟时间 0.831 秒、最大 resident 74481664 字节。

- [普通报告](../verification/lazy-official-local.json)
- [ASan/UBSan 报告](../verification/lazy-official-sanitizer.json)

范围仅为构造、apply、prod 和此处的模仿射作用。不覆盖没有调用的 set/get、all、左右边界搜索，也不替代非交换字符串与独立扫描测试。线上 AC 与排名仍待补齐。

## SCC 与 2-SAT 驱动

固定参考版本同上。SCC 题要求按拓扑序输出点集，因此驱动将 Tarjan 的逆拓扑分量编号倒序输出；2-SAT 驱动按 DIMACS 正负文字适配现有 TwoSAT，保留其 Kosaraju 编号与取值约定。

- SCC：12 组官方数据，报告 `verification/scc-official-{local,sanitizer}.json`。
- 2-SAT：18 组官方数据，报告 `verification/two-sat-official-{local,sanitizer}.json`。

两项均以官方 checker 检验全部输出。另有独立完整驱动测试：Floyd 可达关系验证分量划分与拓扑边，枚举布尔赋值验证可满足性及输出证书，50 万点链/变量链验证递归规模。测试脚本为 `tests/scc_sat_application.py`。这些证据不代替在线 AC、OJ 性能或所有接口验证。

macOS 官方数据 runner 使用 512 MiB 主线程栈链接选项，记录在报告 flags 中；DFS 没有改成显式开栈。负对照允许 testlib 的 WA=1 或 PE=2，其他退出码仍失败；新版报告记录实际拒绝码和消息。

## 普通模卷积、AND 与 XOR 卷积

`convolution_mod` 的 53 组、`bitwise_and_convolution` 的 13 组和 `bitwise_xor_convolution` 的 13 组固定版本官方数据，均以当前驱动通过普通与 ASan/UBSan 的官方 checker 检查。逐组报告位于 `verification/<题目ID>-official-{local,sanitizer}.json`。NTT 数据包含 FFT killer、符号溢出边界、全零和长短悬殊输入；按位卷积包含长度2^20的最大随机数组。

`tests/lc_convolution_application.py` 另以逐系数学校式乘法和直接枚举 i&j/i^j 提供独立参考；最大长度的全 -1 模数代表使用解析计数（三角形、3 的幂、固定配对数），单点非零数组核对 AND 单位下标和 XOR 置换。驱动读取 NTT 的实际长度，按位卷积读取指数，输出全部系数。

三项仅覆盖模998244353。不能据此声称其他模数、OR 分支、空输入或整数精确卷积获得官方验证。线上 AC 与排名仍待完成。

## 拆分后的线性代数组件

`system_of_linear_equations`、`matrix_det`、`matrix_product` 三项分别映射 GaussMod、det_prime、ModMatrix::multiply。题面按固定参考版本核对：方程组输出的是零空间维数、特解和零空间基，不能把系数矩阵的秩作为第一行；矩阵乘法输入为 N×M 与 M×K。

报告路径为 `verification/<题目ID>-official-{local,sanitizer}.json`，分别覆盖27、25、22组官方数据。报告中的打包源码SHA256须与最终格式化后的驱动匹配。本轮执行超时阈值为120秒，只用于本地正确性检查；不是官方5秒/10秒时间限制的判定。运行中同时有编译和其他测试，本地墙钟时间及resident bytes不作为线上排名。

独立完整驱动检查在 `tests/lc_algebra_application.py`：使用排列展开的全部子式求小矩阵秩，以增广矩阵秩判断是否有解，验证特解及基向量方程，并验证基的独立性与个数；行列式用排列展开，矩形乘法用整数内积。大规模包含500阶三角行列式、500变量单位系数系统，以及1024阶全负一模数代表的解析乘积。普通和ASan/UBSan分开保留日志。

这些题仅覆盖模998244353、非空维度；matrix_product没有调用power。其他素数、合数模矩阵幂、空系统等契约仍依据组件独立测试，线上AC和排名继续待补。

## FPS 求逆、对数与指数

固定版本的 `inv_of_formal_power_series` 有25组、`log_of_formal_power_series` 有25组、`exp_of_formal_power_series` 有26组官方数据。报告在 `verification/<题目ID>-official-{local,sanitizer}.json`，分别核对最终打包源码及全部输入/输出哈希。调用前提为非零、1、0常数项；三题均只覆盖模998244353、输入与输出长度相等且1≤N≤500000。

独立完整驱动验证在 `tests/lc_fps_application.py`，使用Python整数逐系数递推，最大规模采用1/(2-x)、log(1-x)、exp(x)的解析系数，另验证262145项常数输入。没有通过inverse的乘法恒等式或log/exp互相抵消作为唯一参考。普通与ASan/UBSan日志分别保存。

本地执行超时阈值120秒，不能视为官方10秒限制下已AC。官方生成器涵盖近262144长度、低次数输入、最大随机以及零系数等情况。独立接口仍有更广的输入/输出长度约定，不能从这三题推断全部契约均已线上验证；线上AC与全AC提交排名待补。

## cc_hash_table 关联数组

`associative_array.cc.compact.cpp` 使用cc_map，20组固定版本官方数据在普通与ASan/UBSan下均通过checker。报告为 `verification/cc-associative-official-{local,sanitizer}.json`。独立Python字典驱动核对不存在的键、写入零和1e18端点；容器本身另有std::map随机操作、百万稀疏键、复制/清空和点引用稳定性检查。官方驱动只调用operator[]与find，不验证其他接口；原gp_map线上AC不转移为cc_map的线上AC。

## 判素与整除和

`primality_test` 的12组和 `sum_of_floor_of_linear` 的11组固定版本官方数据，均通过普通与ASan/UBSan官方checker。报告位于 `verification/<题目ID>-official-{local,sanitizer}.json`，已核对最终驱动打包哈希。

独立驱动测试 `tests/lc_number_application.py` 每项包含十万查询。判素参考为筛表、试除确认因子的乘积和Proth证书：N=3·2^k+1，若a^((N-1)/2)=-1 mod N，则每个素因子的减一都含因子2^k；测试中2^k>sqrt(N)，故不存在不超过sqrt(N)的素因子。此判据没有调用Miller–Rabin。整除和采用小参数逐项枚举，以及A=B=M-1时按完整模数块计数的闭式参考。

判素官方题只到10^18，不验证0或更大uint64输入。整除和官方题只有0≤A,B<M和N≥1，因此每项≤i，结果≤N(N-1)/2，驱动的long long输出转换有明确上界；负系数、N=0仍保留组件独立证据。线上AC、限时表现和全AC提交排名仍待完成。
