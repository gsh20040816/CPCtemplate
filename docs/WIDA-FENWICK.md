# WIDA 在线模板：一维树状数组

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `864bd2178ce95e18ebfdf34d0eab893e2e7d4dc0`，路径 `01 - 常用在线模板汇总/04 - 串与数据结构/25 - Fenwick 1D.cpp`。它使用 `vector`，但没有头文件，单独编译失败。下标从 1 开始。

点加和区间求和与普通数组一致。`ask(1, r)` 在左端是 1 时会调用 `ask(0)`，循环条件把 0 当成结束，结果是 0。三参数 `add(x, y, k)` 执行的是 `add(x, k)` 和 `add(y, -k)`，不是 `add(y + 1, -k)`。`add(2, 5, 3)` 之后，下标 2、3、4 的前缀是 3，下标 5 和 6 是 0。所以右端点本身不包含在加法区间里。

`add(0, k)` 里 `x += x & -x` 仍是 0，会停不下来，这轮没有调用。两次把 `2000000000` 加到同一位置，UBSan 报 signed integer overflow。默认构造没有初始化 `n`，也没有调用。

`python3 tests/wida_fenwick.py` 在普通 `-O2` 和 ASan/UBSan 下通过点加和区间求和，并记录了半开加法和溢出。没有新的在线 AC，也没有新增模板。来源保持 partial。
