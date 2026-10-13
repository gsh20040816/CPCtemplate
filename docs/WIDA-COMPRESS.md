# WIDA 在线模板：坐标压缩

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `2f1e5e673740c415155d99322b59683e89654ba4`，路径 `01 - 常用在线模板汇总/04 - 串与数据结构/27 - 坐标压缩.cpp`。它使用 `vector`、`sort` 和 `assert`，但没有头文件。单独编译失败。这份编译器的 `<bits/stdc++.h>` 也不提供 `assert`，测试另外包含了 `<cassert>`。

`init` 会再塞入 `numeric_limits<T>::max()`。加入 1、3、5 并去重后，表里是 1、3、5 和 `2147483647`，`size` 是 4。`operator[]` 用 `upper_bound`，结果是「有多少个已存储的值小于等于 x」。所以 1、3、5 的编号是 1、2、3，没出现的 2 和 4 分别得到 1 和 2。`Get` 按下标直接取表。`Get(operator[](1))` 得到 3，`Get(operator[](5))` 得到 `2147483647`，都不是原来的值。`count(INT_MAX)` 为真，因为哨兵在表里。`shift` 设成 1 后，1 的编号变成 2。

`operator<<` 把开括号写到 `cout`，把数值和闭括号写到传入的流。越界的 `Get(2)` 在断言开启时中止。

`python3 tests/wida_compress.py` 在普通 `-O2` 和 ASan/UBSan 下通过这些例子。没有新的在线 AC，也没有新增模板。来源保持 partial。
