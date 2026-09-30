# 整除反演与对称计数

本批以 `75ae0b3` 为基线，补全数学分册中原先过短的整除反演与群作用计数说明。目标是把题意、合法对象、公式、现有接口和数值边界接起来；不新增通用群框架，也不以知识页冒充新算法或线上 AC。

## 内容

- `knowledge-mobius.tex`：区分约数和与倍数和；从 GCD 权值推到卷积后的系数；数组不同下标对、GCD 恰为 k 的矩形、有序与无序、零坐标修正；整除分块与预筛/杜教筛的资源选择
- `knowledge-orbits.tex`：等价关系与不变约束；项链旋转、手链奇偶反射、长度 1/2 的退化作用；指定颜色库存的循环系数与 DP；群阶不可逆时提升模数后整数除法
- 文档中的矩形调用和完整 C++ 染色示例由测试直接抽取编译，避免说明与实际可抄代码失配
- 总册和数学分册引用同一知识源；其他分册不重复收录这些内容

## 范围与 issue 对应

本批落实 [#1](https://github.com/gsh20040816/CPCtemplate/issues/1) 的赛时可组合性，以及 [#12](https://github.com/gsh20040816/CPCtemplate/issues/12) 的说明与可调用示例。沿用 [#13](https://github.com/gsh20040816/CPCtemplate/issues/13) 的模板章节和页码引用，不改分类层级。

[#2](https://github.com/gsh20040816/CPCtemplate/issues/2#issuecomment-5907178580) 已批准的基础条目收录清理留作单独一批。本批不宣称完成 OI Wiki 全页审计、全量来源覆盖、正式模板题覆盖或速度排名，不关闭这些较大范围的 issues。

## 复现检查

- `python3 tests/math_knowledge_mobius.py`
- `SANITIZE=1 python3 tests/math_knowledge_mobius.py`
- `python3 tests/math_knowledge_orbits.py`
- `python3 tests/math_knowledge_orbits.py --sanitize`
- `python3 tools/book.py && python3 tools/volumes.py`
- `python3 tests/math_knowledge_integration.py`
- `python3 tests/template_dependencies.py`
- `bash tools/build_pdf.sh`
- `python3 tools/dependency_pdf_audit.py`

实际执行结果与内容指纹记录在 `verification/math-counting-tests.json`；PDF 检查范围记录在 `verification/math-counting-layout.json`。普通模式、ASan/UBSan 与在线评测是不同证据。本批只验证新知识例子及其所调用的当前接口，不替代全库算法回归。ASan 运行关闭不兼容当前环境的 LeakSanitizer，不据此宣称无内存泄漏。


## 本批实际结果

反演测试通过 20,561 个当前 C++ 接口用例与 18,874 个独立公式/模型用例；对称计数的实际文档代码通过 988 个 C++ 用例，包含 128 个宽整数用例。两者普通和 ASan/UBSan 模式均通过。对称计数另枚举每种对称模式下 97,738 个带标号染色，检查 448 组库存轨道、3,120 个二色 DP 和 36 个反射循环案例。

既有组合、概率/博弈知识测试回归通过；15 个知识节仅在总册及数学分册各收录一次，模板章节/页码引用可解析。新内容的 14 个 PDF 引用目标已经逐一核对实际页码与链接目标。

八份 PDF 最终编译日志无警告，13 处跨册链接核验通过。总册印刷页 492–495、503–508，数学分册印刷页 136–139、147–152，共 20 个新增或相邻页面已逐页渲染检查；无截断、遮挡、缺字或断裂公式。完整 38 行对称计数示例保留在同一页，接受前页留白，避免将 else 分支拆到下一页。其余六份分册逐页文字与具名目标页核对不变，保留原 PDF 字节。
