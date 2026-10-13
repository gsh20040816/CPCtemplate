# WIDA 在线模板：完整头文件

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `bf2c922a8bca7f3bbf97f1b5be2ca61d222b5c87`，路径 `01 - 常用在线模板汇总/01 - 初始与杂类/01 - 在线头文件.cpp`。它是一份带 `main` 的程序，不是可包含的头。

没有定义 `ONLINE_JUDGE` 时，它包含本机没有的 `<bits/wida.h>`，编译失败。同一段还会把标准输入输出改到 `in.txt` 和 `out.txt`，但编译到不了那里。加上 `-DONLINE_JUDGE` 后，空的 `main` 正常退出，没有输出。

`#define` 写在命名空间里也会泄漏。文件后部把 `int` 定义成 `long long`，把 `endl` 定义成换行字符串。因此 `signed main(int argc, ...)` 的参数变成 `long long`，编译器给出警告。`cmax(x, 4)` 在这之后无法同时推导 `long long` 和 `int`，测试改用 `4LL`。

`N` 是 1000007，`INF` 是 2147483647。`{3,1,2}` 的最小、最大、和是 1、3、6。排序和逆序排序分别得到 `1 2 3` 与 `3 2 1`。`floor` 和 `ceil` 对 `5/2`、`-5/2` 给出 2、-3 和 3、-2。`mypow(2,10,1000)` 是 24。`FOR`、`FOR2`、`FORD`、`Yes`、`pb`、`sz`、`fi` 和 `se` 与字面展开一致。`floor(5,0)` 中止。`mypow(100000,2,...)` 在取模前溢出。

`python3 tests/wida_header.py` 在普通 `-O2` 和 ASan/UBSan 下通过空程序和这些例子。没有新的在线 AC，也没有新增模板。来源保持 partial。
