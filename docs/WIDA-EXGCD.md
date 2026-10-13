# WIDA 在线模板：Exgcd

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `0c03386ef4af4cc3465115665ff30b3e079ab14a`，路径 `01 - 常用在线模板汇总/03 - 数论、几何/19 - Exgcd.cpp`。文件末尾的 `clac` 是带 `[&]` 的 lambda，不能放在全局，单独编译失败。`ceil` 里的 `assert` 也没有包含 `<cassert>`。

`exgcd(35, 15)` 得到 5，并且满足贝祖等式。`exgcd(-4, 6)` 得到正的 2，同样满足等式。自定义 `ceil` 对 `5/2`、`-5/2`、`5/-2`、`-5/-2` 分别给出 3、-2、-2、3。

`clac` 按 `ax+by=c` 打印正整数解。`a,b` 在 1 到 8、`c` 在 1 到 20 的全部组合，与独立扫描一致。`c=0` 有 44 组不一致：特解的 `x` 被乘成 0 后，`(x-1)/p` 截断成 0，`x` 停在 0。例如 `x+2y=0` 打印 `0` 和 `1`，最小正 `x` 应是 2。`clac(0, 5, 10)` 把 `a/d` 当成步长，除数是 0，UBSan 报 division by zero。

测试把 lambda 放进 `main` 后运行。`python3 tests/wida_exgcd.py` 在普通 `-O2` 和 ASan/UBSan 下通过。没有新的在线 AC，也没有新增模板。来源保持 partial。
