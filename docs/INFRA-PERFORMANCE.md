# Infra O2基线与优化选项实测

Issue #17 第二章。`python3 tests/infra_performance.py` 重建并运行；原始样本、命令、源文件与输入SHA-256在 `verification/infra-performance.json`。印刷表格直接取该收据的中位数，不把旧样本与新源码混用。

## 环境与测量范围

Apple M5、macOS arm64、Homebrew GCC16.2.0、libstdc++、C++23。数据路径和绝对命令见收据。默认 `-O2 -Wall -Wextra`，不带检查器；单线程。每个候选9个新进程，不取最快一次。主基准变体按固定种子打乱顺序，I/O和重复分配交替顺序；优化选项单独交错运行。未隔离其他宿主负载，也没有固定频率或绑核，因此小差异不能解释成稳定收益。

- 数组：4194304个int，值i%1009；计时使用steady_clock，结果整数和以独立周期求和公式核对。
- grow/reserve从空vector开始，测预留/扩容、填充与求和；析构发生在计时之后。
- copy/reference/move先在计时外填好相同数组，再测函数调用。consume按值接收，计入参数复制或移动、求和与参数析构；read_values按const引用借用。noinline用于维持基准的调用边界，不是给赛时代码的建议。三者所有权语义不同，不能忽略接口要求强行替换。
- row/column先在计时外构造2048×2048的行主序连续数组；两个独立循环仅改变访问顺序。早期试验在内层判断字符串模式，产生明显干扰，已删除；最终收据只对应修正后的代码。
- 重复分配：2048轮，每轮4096个i xor round，全部元素参与校验。fresh每轮swap空vector释放容量再追加；reuse使用clear保留容量。二者初始容量均为0。
- I/O：同一文件的100万个非负十进制整数i%1009，计时包括读取、解析与求和。default保留流默认同步/绑定；fast在I/O前关闭。两选项一起改变，不能将所有收益分别归因于其中一个。
- O2/O3/O2+funroll-loops单独比较相同按行求和代码；本轮数值接近，没有证据声称O3/展开稳定占优。数组主表的row与此表的O2属于不同交错测量组。

这是本机微基准，不是OJ结果，未在Linux或x86上重现，也不作为AVX指令性能证据。所有输入/源文件都可由已登记脚本重建。

## 浮点与pragma范围

`fast_math.cpp`在输入10000000000000000与1时，O2/O3结果0，Ofast结果1；展示重排可改变数值，不能把Ofast当作对几何和数值模板的无条件建议。

`pragma_scope.cpp`实际验证push/O3+unroll/pop及求和。`pragma_include.cpp`引用短头文件 `pragma_header.hpp`：在include前切Ofast得到H/L/R=1/1/0，在include后切得到0/1/0；R定义在pop后。三个函数noinline以避免测试被调用者合并。说明的是函数定义范围，不是跨所有头文件/模板实例化的统一保证；头文件自己的属性和pragma可改变结果。

本轮只介绍target作用与CPU要求，未在当前arm64宿主运行AVX2/AVX512；SIMD条目保持未完成。性能示例属于工具手册，不新增算法组件或OJ验证记录。

## 依据与收据

- [GCC优化选项](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [GCC函数级选项pragma](https://gcc.gnu.org/onlinedocs/gcc/Function-Specific-Option-Pragmas.html)
- [实际执行收据](../verification/infra-performance.json)

来源引用保留在开发文档，印刷稿保留结论、例子、条件和实测环境。
