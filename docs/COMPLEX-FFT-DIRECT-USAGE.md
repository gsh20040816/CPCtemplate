# ComplexFFT 直接变换用法

正式用法 `example-222` 对应 [Luogu P3803 中文题面](https://www.luogu.com.cn/problem/P3803)：两个多项式次数均在0..1000000，整数系数在0..9，按升幂输入和输出。官方样例及精简契约保存在 `tests/fixtures/complex-fft-transform/`。英文自动翻译把最低次数改成1，登记使用中文原题的0。

`verify/luogu/P3803.transform.compact.cpp` 在main中直接构造ComplexFFT、执行两次正变换、逐点相乘和一次已归一化逆变换，再llroundl取整。原 `example-121` / `P3803.fft.compact.cpp` 仍展示convolution_fft包装器；精确整数CRT驱动也不变。新增的是同一问题的底层接口用法，没有新增算法，也不把依赖关系自动算成直接覆盖。

登记后共有207个算法、222份用法：154个组件有正式模板题本地用法，41个仅应用、4个仅接口演示、8个待补。这里“本地用法”不是在线AC。

## 数值前提

最大输出长度2000001，补零长度至多2^21，低于核心上限2^22。两输入的L2范数乘积至多81×1000001=81000081。沿用本库已公开的 [Percival误差分析](https://www.daemonology.net/papers/fft.pdf) 第5.1定理及浮点前提：二进制至少53位、最近舍入、禁用fast-math、单位根绝对误差≤8×2^-53。在这些条件下，本题最坏绝对误差界小于0.000006386，故最近整数舍入安全；不能用随机测试替代这些条件。

`verification/complex-fft-platform.json` 是本次Linux/GCC14的单独记录：普通/ASan+UBSan各用百位独立参考检查2^22网格的全部2097152个单位根，最大误差除以2^-53为0.00165993；探针观察到64位有效二进制尾数、FE_TONEAREST、没有fast-math。还运行了原Decimal误差界检查。报告保留初次LSan因ptrace退出失败的事实，之后完整重新捕获的SAN运行明确关闭LSan；它不是内存泄漏检查证书。

历史 `verification/fft-attachment.json` 仍是原Darwin/53位浮点环境证据，没有改写成Linux新结果。当前平台报告也不保证所有其他编译器/libm/浮点设置都成立。

## 三种可抄写形式与独立参考

运行 `python3 tests/complex_fft_usage.py --mode both`；默认写新的build子目录，可用 `--report-dir` 指定报告目录。导入不执行，拒绝Python -O。测试同时编译直接驱动、依赖展开后的登记程序、从正文用法与核心重组的抄写程序。

每种形式342例：1官方样例、7个零/常数/脉冲/不对称固定例、196个长度1..3且系数0或9的穷举配对、36个补零边界、100个固定种子学校乘法参考例、2个最大次数例。最大例分别用全9三角闭式及五个非零项与周期数组的整数移位累加给出独立精确答案，不使用被测FFT或卷积包装器作参考。

普通与ASan+UBSan共342×3×2=2052次精确输出执行；默认PIE/quarantine，LSan关闭。证据为 `verification/complex-fft-transform-normal.json` 和 `verification/complex-fft-transform-sanitizer.json`，绑定驱动/核心/登记项/正文片段/测试/官方样例及编译器驱动和前端的前后哈希，并记录各输入、期望输出、生成程序和可执行文件哈希。

另外 `tests/usage_examples.py --only example-222` 对4个小用例双模式运行；未改动的前221份程序仍逐一检查原哈希证据匹配。

## 时限及发布范围

本次普通模式最大规模子进程墙钟约1.833–2.029秒，题面限制2秒。这不是在评测机上的计时，也不能据此断言通过或超时；线上时限适配尚未确认，未新增AC记录。sanitizer耗时不用于判断竞赛性能。

PDF实际查看新增用法及相邻页、infra跳转页；字体字号不改。对应报告为 `verification/complex-fft-{visual,layout}.json`。当前修改不计入旧52d81d1整库回执；两个浮点几何核心的AOJ精度限制亦不因本次测试而消失。

本批另重新检查全部222份抄写上下文：216份直接标准上下文通过，6份需已登记的GNU专用头文件；补齐登记头文件后6份全部通过，未解决项0，输入哈希稳定。证据 `verification/runs/20261002-222-copy-context.json`；这是语法/可抄写性检查，不替代运行验证。
