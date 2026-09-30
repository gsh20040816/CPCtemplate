# 静态后缀查询接口演示

这是自定义输入协议的 API 用法演示，不是官方模板题、比赛应用题或 OJ 提交驱动。登记为 `example-205`、`kind=api`，只说明当前 `SuffixLCP` 与 `prefix_lcs` 怎样构造及调用。它不能填补正式模板题、官方数据、在线 AC 或速度排名证据。

- 完整驱动：[static-suffix-demo.cpp](usage-drivers/static-suffix-demo.cpp)
- 实现来源：[suffix_lcp.hpp](../src/compact/suffix_lcp.hpp)，依赖 [string.hpp](../src/compact/string.hpp) 中的 `SuffixArray`
- 抄写顺序：`SuffixArray`、`SuffixLCP`、`prefix_lcs`、演示的 `main`
- 独立测试：[static_suffix_demo.py](../tests/static_suffix_demo.py)

## 输入输出协议

一组输入，首行 `n q`；第二行恰好为 `n` 个小写英文字母。`n=0` 时第二行必须是空行，因此读取字符串前只丢弃首行剩余内容，不能使用会跳过空行的 `cin >> ws`。之后恰有 `q` 行查询。`0≤n,q≤200000` 是本演示选择的界限，不是任何在线题目的限制。

- `0 x y`：输出后缀 `s[x..n)` 与 `s[y..n)` 的最长公共前缀长度，即 `forward.query(x,y)`
- `1 l1 r1 l2 r2`：比较 `s[l1..r1)` 与 `s[l2..r2)`，字典序小于、等于、大于时分别输出 `-1`、`0`、`1`，即 `forward.compare(l1,r1,l2,r2)`
- `2 x y`：输出前缀 `s[0..x)` 与 `s[0..y)` 的最长公共后缀长度，即 `prefix_lcs(reversed,x,y)`；这里 LCS 指 common suffix，不是 common subsequence

所有下标或端点均为 `0..n`；比较区间另须满足 `l1≤r1`、`l2≤r2`。空区间合法；空串比非空串小，两个空串相等。每条查询恰输出一行十进制整数，`q=0` 不输出。输入须满足协议，不提供非法输入的恢复行为。

## 正反构造与边界

`forward` 从原串 `s` 的后缀数组构造，`reversed` 从完整倒序串的后缀数组构造，不能传正向结构冒充倒序结构。`SuffixLCP` 保存所需排名和 RMQ 数据，驱动中临时 `SuffixArray` 析构不影响查询。结构是静态的；改动字符串后应重新构造，每组输入使用新对象。

- `query(x,x)=n-x`；`query(n,y)=query(x,n)=0`
- `prefix_lcs(reversed,x,x)=x`；`x=0` 或 `y=0` 时答案为 `0`
- `x,y` 是前缀长度或右端点，倒序下标为 `n-x,n-y`，不能多减 `1`
- 子串公共前缀长度为 `min(forward.query(l1,l2), r1-l1, r2-l2)`
- 子串公共后缀长度为 `min(prefix_lcs(reversed,r1,r2), r1-l1, r2-l2)`
- 对比两个子串时使用 `compare` 已经处理长度截断；未截断的后缀 LCP 不是任意子串的 LCP

例如 `s="ababb"` 时，`query(0,2)=2`，`compare(0,2,2,4)=0`，`compare(0,2,0,3)=-1`，`prefix_lcs(reversed,2,5)=1`。最后一项也检查了非回文串的反向构造；若误传正向结构会得到错误结果。

正反各一次后缀数组与稀疏表构造，总预处理 `O(n log n)` 时间、`O(n log n)` 空间；三种查询均为 `O(1)`，总查询时间 `O(q)`。答案在 `[-1,n]` 内，用 `int` 足够。演示规模 `n=200000` 下，两张稀疏表本身约 25 MiB，排名、对数表、临时构造数组及运行库另计；sanitizer 还会增加内存开销，不据此宣称适配某个 OJ 的内存限制。

## 本地验证与证据范围

运行：

```sh
python3 tests/static_suffix_demo.py
CPC_SANITIZE=1 python3 tests/static_suffix_demo.py
```

测试通过 `tools/usage_examples.records()` 取得登记中实际展开的完整程序，不另写替代驱动。另按 `requires` 顺序仅粘贴三个命名模板并编译执行，防止头文件过度包含掩盖遗漏依赖。普通与 ASan/UBSan 模式分开运行，sanitizer 关闭 LeakSanitizer（`detect_leaks=0`），因此不声称检查泄漏。

独立参考只直接逐字符扫描公共前后缀，并用 Python 字符串比较判断子串顺序，不复用后缀数组、排名或 RMQ。覆盖空串/空区间、同内容不同位置、前缀顺序、端点 `n`、前缀 `0`、非回文反向构造，枚举短二元串、随机串、二次幂附近长度以及所选 `n=q=200000` 数据。最大规模的重复/周期串查询从固定边界查询池循环，参考答案每个不同查询只直接计算一次；随机串使用大量不同查询。该选择覆盖最大输入量，但不是官方完整数据或所有最大规模查询分布的证明。

报告写入 `build/static-suffix-demo-normal/report.json` 与 `build/static-suffix-demo-sanitizer/report.json`，绑定实际程序、命名依赖副本、输入输出、相关源码与测试文件哈希，记录编译器、模式和范围。执行前后核对源码未变；报告不写入 OJ 证据目录。中央 `tests/usage_examples.py --only example-205` 的固定输入输出检查仍走现有示例证据流程，需先由生成器重建打印片段，再执行并刷新覆盖状态。

生成器的回归检查使用 `build/` 下临时数据，验证 `template > application > api` 优先级、缺证据/哈希失配回退、纯接口不计正式覆盖及非法分类拒绝，不修改正式生成文件。
