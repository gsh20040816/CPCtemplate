# Infra 构建与验证

后续定位由 [issue #17](https://github.com/gsh20040816/CPCtemplate/issues/17) 改为Python、C++进阶、Shell、赛场环境四章手册；下文说明当前构建方式。已执行的第三章脚本素材见 [编译与对拍](INFRA-SCRIPTS.md)。已完成第一、三章主体并更名；第二、四章仍需补齐。

`output/pdf/xcpc-infra.pdf` 按 Python、C++ 进阶、Shell、赛场环境四章组织。正文源为 `docs/infra-body.tex`；`tools/infra.py` 生成封面与跨册索引。

GNU配对堆在数据结构册详细介绍，并在infra集中索引。标准库部分整理当前常用容器、排序/查找、optional、回调、位操作与随机数，并专节解释std::move。已按当前源码补充complex的模长/共轭、partial_sum累加类型、tie引用语义、位宽零边界和shuffle复现范围，具体对应关系见[标准库增补审计](INFRA-STL-AUDIT.md)。它不是整个C++标准库或OI Wiki三板块的完整替代品；还需对照实际使用记录继续补齐未登记细项，issue #9保持开放。

## 依赖

除既有XeLaTeX、latexmk、中文字体、Poppler外，跨文件链接审计需要pypdf 6.0.0。首次本地可建立项目工具环境：

```bash
python3 -m venv build/tools-env
build/tools-env/bin/pip install clang-format==23.1.1 pypdf==6.0.0
tools/build_pdf.sh
```

本地验证使用同版本pypdf；GitHub CI已停用。构建器先生成算法各册，随后用xr-hyper读取最终aux，再构建infra；不能先生成infra而引用旧页码。所有PDF放在同一目录，链接采用GoToR命名目的地，不手写页码。

`tools/infra_audit.py` 读取infra实际链接，核对目标文件、命名目的地及目标页的印刷页码。当前生成索引有18项，实际跳转通过与否以每次PDF构建后的审计报告 `verification/infra-links.json` 为准。集合记录在 `docs/infra-links.json`，包含PBDS堆、有序树、rope、GP/CC哈希表及标准库典型使用场景，并直达PBDS句柄删除/modify降键的两份正式题用法；本次新增ComplexFFT、WaveletMatrix和SecondMST入口。原来的字体、溢出、索引与页码检查不放松。

## 示例检查

`tests/infra_examples.cpp` 检查move/copy重载、移动后合法复用、STL区间及PBDS句柄迁移；另以独立算术参考检查65536个位操作输入和64位边界，并检查complex、tie值快照、宽前缀和、NaN比较关系与shuffle排列性质。测试不会故意执行溢出、零参数GCC计零函数或非法排序。`tests/infra_examples.py` 执行Python大整数/取整/模逆失败与列表别名，以及Bash带空格路径、字面美元符号、diff退出值和pipefail例子。

本项目先使用显式 `CXX`，否则运行时检查g++-16是否存在，再回退g++；实际版本以验证收据为准。Linux递归测试只把栈软上限设为请求值与继承的有限硬上限的较小者，不修改硬上限，默认请求524288 KiB；详见 `tools/test_baseline.py`、`tools/run_provenance.py` 和 `tools/test.sh`。不要无条件执行 `ulimit -s unlimited`。

本次聚焦检查的编译命令、实际编译器、输出与输入SHA-256记录在 `verification/infra-contracts-20261002.json`。其中ASan/UBSan与LeakSanitizer分开记录；聚焦示例通过不代表全库回归、PDF链接审计或新OJ AC。全量回归仍按[验证证据约定](VERIFICATION-PROVENANCE.md)生成独立收据。

来源包括C++标准草案的[move定义](https://eel.is/c++draft/forward)、[移动后状态](https://eel.is/c++draft/lib.types.movedfrom)，以及[GCC PBDS说明](https://gcc.gnu.org/onlinedocs/libstdc++/manual/policy_data_structures_using.html)。手册统一以C++23和Python 3.11+为假定环境；算法库已有C++20模板继续保持自己的接口要求。

## 移出印刷正文的标准引用

- [标准草案 move 定义](https://eel.is/c++draft/forward)
- [移动后状态](https://eel.is/c++draft/lib.types.movedfrom)
- [失效规则来源](https://eel.is/c++draft/vector.modifiers)
- [严格弱序与等价关系要求](https://eel.is/c++draft/alg.sorting.general)
- [关联容器要求](https://eel.is/c++draft/associative.reqmts)
- [算法要求](https://eel.is/c++draft/alg.sorting)
- [tuple 创建](https://eel.is/c++draft/tuple.creation)
- [tuple 赋值](https://eel.is/c++draft/tuple.assign)
- [累加定义](https://eel.is/c++draft/accumulate)
- [算术类型转换](https://eel.is/c++draft/expr.arith.conv)
- [partial\_sum 定义](https://eel.is/c++draft/partial.sum)
- [分量接口](https://eel.is/c++draft/complex.members)
- [模长、平方模与共轭](https://eel.is/c++draft/complex.value.ops)
- [bit\_width](https://eel.is/c++draft/bit.pow.two)
- [位计数](https://eel.is/c++draft/bit.count)
- [移位边界](https://eel.is/c++draft/expr.shift)
- [GCC 内建函数](https://gcc.gnu.org/onlinedocs/gcc/Bit-Operation-Builtins.html)
- [shuffle 要求](https://eel.is/c++draft/alg.random.shuffle)
- [分布算法的实现差异](https://eel.is/c++draft/rand.dist.general)

## 本批进度

Python第一章和Shell第三章已纳入印刷稿。C++计时、随机分布、造数据与整数防卡哈希已补入；优化实测、SIMD及第四章环境检查/GDB/交互联调仍未完成。Python同源例子收据见 verification/infra-python-chapter.json；脚本收据见 verification/infra-scripts.json。历史批次JSON中的旧PDF路径和哈希保留为历史证据，不改写成新文件的验证结果。

Python语义来源：[内置类型](https://docs.python.org/3/library/stdtypes.html)、[random](https://docs.python.org/3/library/random.html)、[Decimal](https://docs.python.org/3/library/decimal.html)、[itertools](https://docs.python.org/3/library/itertools.html)。运行时版本见收据，例子不使用3.11之后新增的API。

C++时间与随机工具由 examples/infra 的 clock_demo.cpp、random_tools.hpp、random_demo.cpp、hash_demo.cpp 同源印刷，tests/infra_random.py 在O2和ASan/UBSan下运行；1000种子检查排列、互异值、字符集、树连通性及边数、简单图去重和范围、同环境复现，收据见 verification/infra-random.json。只验证结构和API使用，不将样本当作分布正确性的证明或优化性能证据。

补充来源：[C++随机分布](https://eel.is/c++draft/rand.dist)、[单调时钟](https://eel.is/c++draft/time.clock.steady)、[PBDS哈希参数](https://gcc.gnu.org/onlinedocs/gcc-15.2.0/libstdc%2B%2B/api/a01292_source.html)。随机树为重标号随机递归树，并非所有标号树均匀抽样；简单图枚举所有边再洗牌，仅供小数据对拍。
