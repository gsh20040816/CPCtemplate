# 使用页抄写上下文审计

完整驱动会展开整个本地头文件，不能证明照着手册的 `requires` 清单抄写就能编译。本审计从当前 `src/compact` 中抽取与手册相同的组件区域，只拼接指定组件、标准头和打印的使用代码，不引入完整本地头文件。

## 可复现命令与范围

```sh
python3 tests/copy_prerequisite_order.py
python3 tools/audit_copy_context.py --output-dir build/copy-context-new --jobs 4
```

输出目录必须不存在。工具保留各个候选程序、诊断、编译器和输入前后哈希，最终 JSON 也内嵌程序与诊断，可独立归档。默认使用 g++ 的 C++20 `-fsyntax-only`；这只是语法和抄写依赖检查，不是运行正确性、sanitizer、在线 AC 或复杂度验证。

三阶段分别检查：

1. 按使用页清单原顺序直接拼接
2. 仅按已登记的组件依赖图补全和排序，不猜测新辅助函数
3. 对仍需 GNU 扩展的示例，加入条目正文已经明确要求的 `ext/...` 头文件

普通前置环境为 `bits/stdc++.h`、`cassert` 和 `using namespace std`。GNU rope 的断言兼容顺序为扩展头在前、cassert 在后。所有非标准头都属于已有条目契约，不当作算法组件或额外模板覆盖。

## 2026-10-02 修正

修正前的 216 份用法中，直接清单编译通过 198 份；已有依赖图闭包通过 210 份，其余 6 份在加入正文声明的 GNU 头文件后通过。由于登记规范明确承诺 `requires` 可按顺序直接抄写，不能让读者自己从依赖图推导缺项。因此修复了 12 份使用页清单：

- example-3、128：TwoSAT 补 SCC
- example-47：DiscreteLog 补 Mod64、extended_gcd、mod_inverse
- example-106：euler_power 补 Prime64、PollardRho，并前移 Mod64
- example-136：minkowski_sum 补 polygon_contains
- example-167：bridge_augmentation 补 bridge_component_forest
- example-176、178、179：将 XorBasis 移到 XorWalk 与线性基交相关组件之前
- example-191：divisor_sum_power 补 Mod64
- example-192：carmichael 补 Mod64
- example-194：CompositeRoots 将扩展欧几里得和逆元移到 DiscreteLog 之前

前后完整清单和登记文件哈希见 `verification/copy-context-prerequisite-fixes.json`。这些修正没有改动核心算法、驱动或 216 份展开程序；它们修复的是使用说明中的抄写前提。

GNU 头契约对应 example-66（rope）、67（order-statistics tree）、68/69（hash table）、189/190（priority queue）。轻量检查 `tests/copy_prerequisite_order.py` 已接入常规测试，并含缺依赖、逆序和重复组件的负对照。完整编译审计单独运行，不把它重复加入每次运行测试。

修正后冻结复验：直接清单和依赖闭包两阶段均为 210/216；余下 6 份按上述 GNU 头契约全部通过，未解决项为 0，输入、编译器及候选程序哈希检查通过。长组件名称只在显示用下划线后允许换行，链接标签与字号不变。

修正前完整诊断见 `verification/copy-context-before-fix.json`。最终冻结复验记录见 `verification/copy-context-audit.json`；该记录只对其输入哈希对应版本有效。修正前证据单独保留，不用后来的通过结果覆盖旧失败诊断。
