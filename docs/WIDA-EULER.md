# WIDA 在线模板：欧拉筛

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `844e97ecb9184a0341139803268cdbba85bcf6a3`，路径 `01 - 常用在线模板汇总/03 - 数论、几何/18 - 欧拉筛.cpp`。这是一段 lambda，不是完整程序。它依赖外部的 `prime`，并且使用 `vector`，单独编译失败。

贴进函数后，`euler_Prime(1)` 不产生素数。`euler_Prime(30)` 得到的素数与试除一致。`v[i]` 记最小质因子，乘积用 `prime[j] > n / i` 停住，避免 `i * prime[j]` 越过 `n`。再调用 `euler_Prime(10)` 不会清空旧表，而是又追加 4 个素数，表长变成 14。

`python3 tests/wida_euler.py` 在普通 `-O2` 和 ASan/UBSan 下输出 `0`、`1`、`14`。没有新的在线 AC，也没有新增模板。来源保持 partial。
