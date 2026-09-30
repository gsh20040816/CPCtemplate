# 模板题使用代码

执行 issue #12：每个模板应有题目链接、最简题意、所需模板名称与使用代码。正文示例只打印现有完整驱动的 main 部分，已粘贴的算法定义和标准头不重复打印。使用代码包含输入读取、模板对象构造、调用和答案输出。

登记文件为 usage-examples.json，生成器 tools/usage_examples.py 输出 usage/*.cpp 和逐模板覆盖表 USAGE-COVERAGE.md / usage-coverage.json。新模板自动进入待补清单，未补项不隐去。具体数量与未完成项以生成的 USAGE-COVERAGE.md 为准；应用题补充与接口演示单独标出，不冒充正式模板题。

示例与完整驱动共用源文件，避免手册另存一份易失配的调用。生成器展开驱动所含模板依赖并计算源码哈希；verification/usage-examples.json 中同一模板的全部示例哈希与两种执行模式均匹配，才记为本地验证。至少一份正式模板题用法时状态为 locally_checked_example；没有正式模板题但有比赛等应用用法时为 locally_checked_application；只有接口演示时为 locally_checked_api。后两者均不计正式模板题覆盖。模板或驱动变化使哈希失配时恢复为 generated_unverified。

验证流程：先运行 python3 tools/usage_examples.py，再运行 python3 tests/usage_examples.py，最后重新运行生成器。测试编译与打印完全相同的 main，执行固定输入输出证书，覆盖索引转换、分量输出、SAT/UNSAT、点双/边双、带权回调及查询格式；普通和 ASan/UBSan 两种模式都运行。完整算法正确性仍由原有算法测试、官方数据和在线记录分别承担。

本地按需执行双模式示例检查，并核对生成覆盖表与哈希证据是否匹配。PDF 构建直接从同一登记表插入示例，保留题目链接及使用条件；不将示例执行通过称为在线 AC。

本地可用 --only 指定新示例以避免重复执行未变的程序；被跳过示例的依赖哈希和双模式记录仍必须有效。GitHub CI 已停用，不再维护。

应用题补充使用 kind=application 标记，正文标题明确区分；一个模板只有应用题示例时，不能计为模板题示例已完成。PAM 的 P3649 是补充，正式模板题示例使用 P5496。

## 登记分类与接口演示

kind 只允许 template、application、api；省略时默认为 template，拼写错误直接拒绝。三者分别表示正式模板题、应用题补充和自定义接口演示，不改变旧示例分类。多类并存且全部执行证据有效时，覆盖状态按 template、application、api 的顺序选择。

所有分类共用 id、symbol、problem、url、summary、driver、requires 字段。api 的 problem 是演示名称，url 是真实实现或协议来源，summary 必须明确自定义协议、输入边界及本地证据范围；正文使用“接口用法演示”“演示约定”“来源”，不得伪装成官方题目。requires 按可直接抄写的依赖顺序列出；also_covers 仅登记 main 中实际直接调用的附加模板，不把所有依赖都算成覆盖。

自定义接口驱动放在 docs/usage-drivers/，不进入 verify/ 的 OJ 驱动候选队列。首次静态后缀示例见 [静态后缀查询接口演示](STATIC-SUFFIX-DEMO.md)；其独立随机与最大演示规模测试仅写 build/ 报告，不生成在线提交或 AC 记录。

需要快速输入的完整用法可以登记 utility_functions（当前为 read），从同一驱动取出函数正文并与main一起打印、编译；这些函数是抄写所需的输入工具，不是算法定义。它与 configuration_functions 分开登记，防止遗漏输入依赖。批量逆元示例用 move(a) 将数组传入按值接口，传入后不再读取a；普通左值调用则保留原数组但产生副本。
