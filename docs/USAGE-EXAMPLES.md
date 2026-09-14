# 模板题使用代码

执行 issue #12：每个模板应有题目链接、最简题意、所需模板名称与使用代码。正文示例只打印现有完整驱动的 main 部分，已粘贴的算法定义和标准头不重复打印。使用代码包含输入读取、模板对象构造、调用和答案输出。

登记文件为 usage-examples.json，生成器 tools/usage_examples.py 输出 usage/*.cpp 和逐模板覆盖表 USAGE-COVERAGE.md / usage-coverage.json。新模板自动进入待补清单，未补项不隐去。首批 7 份示例覆盖 6 个模板，BiconnectedCore 包含点双和边双两题；其余继续补齐。

示例与完整驱动共用源文件，避免手册另存一份易失配的调用。生成器展开驱动所含模板依赖并计算源码哈希；verification/usage-examples.json 的哈希与两种执行模式均匹配，才记为 locally_checked_example。模板或驱动变化使哈希失配时恢复为未验证。

验证流程：先运行 python3 tools/usage_examples.py，再运行 python3 tests/usage_examples.py，最后重新运行生成器。测试编译与打印完全相同的 main，执行固定输入输出证书，覆盖索引转换、分量输出、SAT/UNSAT、点双/边双、带权回调及查询格式；普通和 ASan/UBSan 两种模式都运行。完整算法正确性仍由原有算法测试、官方数据和在线记录分别承担。

CI 在全库测试后独立执行这组双模式示例检查，并核对生成覆盖表与哈希证据是否已提交。PDF 构建直接从同一登记表插入示例，保留题目链接及使用条件；不将示例执行通过称为在线 AC。
