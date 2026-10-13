# WIDA 08 最长公共前缀例题：原稿不完整

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `b36bd5568fc01ca8f1641100df0d5a74634ba274`，字节保存在 tests/fixtures/wida_lcp/main.cpp。文件 1510 字节，注释指向 https://qoj.ac/submission/343378 。该页面直接访问返回 403，题号和完整提交源码未能读取。不能凭文件标题认定现有后缀数组 LCP 或广义 SAM 已经覆盖这道例题。

## 原稿实际做了什么

它没有 `#include`，`main` 声明为返回 `int` 但没有 `return`。程序读入字符串个数和若干由 `operator>>` 读取的小写串，用超根把每条串从状态 1 插入同一台后缀自动机：`nxt[0][*]=1`，`len[0]=-1`。返回状态上的 `f` 只记录唯一字符串编号，第二条不同字符串把它改成 -1。最后把 `lnk` 收成子节点表 `adj`，然后结束。

没有查询、没有输出，也没有沿 `adj` 的 DP。因此它不是最长公共前缀或任何可提交答案的完整算法。`f` 也没有传播到克隆点的全部后缀链接祖先，不能把它当成各串出现次数。

现有 `SuffixAutomaton` 从单串末尾扩展，`GeneralSAM` 先建 Trie 再 BFS。二者都不使用这个超根，也不维护这份唯一编号。不能互相代替。

## 本地证据

`python3 tests/wida_lcp_source.py`：

- `-O2` 下 47 组输入的转移、长度、链接、唯一编号和未使用的链接树，与独立 Python 过程一致，共 43243 项。
- `-O0 -fno-unreachable-traps` 下同一 47 组调用原稿 `main`，标准输出为空且退出码为 0。
- ASan/UBSan `-O1` 同时做了结构对照和原稿 `main`，共 43290 项，无消毒器诊断。
- 默认 `-funreachable-traps` 会在离开这个无返回值的 `main` 时主动陷阱。这是编译器对未定义行为的处理，测试只在观察原稿时关掉该陷阱，不修改原稿。
- 同一份源码在 `-O2` 下执行原稿 `main`，空输入即抛出 `std::length_error`（`vector::_M_realloc_append`）并以 SIGABRT 结束。`-O2` 的结构对照仍然通过，所以失败点在原稿 `main` 的优化结果，不是 Python 对照过程。此项只记录现象，不把它解释成算法公式错误，也不把 `-O0` 通过写成优化构建可用。

证据见 verification/wida-lcp-example.json。来源状态保持 partial。没有新模板、没有用法页、没有在线 AC。QOJ 343378 的题目身份仍待确认。
