# WIDA 04 旧版一般图最大匹配

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `0b1d98571f5b3578d31fc0745eef3d51fa0a5d6b`，路径 `03 - jiangly模板收集/02 - 图与网络/04 - 一般图最大匹配（Graph 带花树算法）【久远】.cpp`。文件里有两个都叫 `Graph` 的类型，不能当作一个翻译单元编译。

后面的 `findMatching()` 先贪心占边，再从每个未匹配点增广。无自环的小图上，匹配合法，基数等于穷举最大匹配，也等于现有 0-based `Blossom`。自环 `addEdge(0, 0)` 会被贪心写成 `match[0] = 0`。这不是简单匹配。库实现会忽略自环，基数仍是 0。

前面的 `findMatching(m, init)` 只从编号小于 `m` 的未匹配点增广。空初始匹配时，完全落在 `[m, n)` 里的一条边不会被配上。它不是整张图的最大匹配。

`python3 tests/wida_blossom.py` 在普通 `-O2` 和 ASan/UBSan 下核对了无自环图、自环和左侧限制。QOJ 与 Codeforces 提交页面没有打开，没有新的在线 AC。来源保持 partial。
