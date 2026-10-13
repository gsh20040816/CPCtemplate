# WIDA 08 树链剖分

原稿是 hh2048/XCPC 树 `cfdb12db6792eb2303798541fb5c760ed2bc618b` 的 blob `3f383ecf74fcc60cfc60c86cfcbd4670149e32b5`，路径 `03 - jiangly模板收集/02 - 图与网络/08 - 树链剖分（HLD）.cpp`。

点号从 0 开始。`addEdge` 加无向边。`work(root)` 把父边从邻接表删掉，重儿子换到 `adj[u][0]`，然后做欧拉序。只调用一次时，`lca`、`dist`、`jump`、`isAncester`、`rootedParent`、`rootedSize` 和 `rootedLca` 与按父节点爬升的结果一致。`jump(u, k)` 在 `k` 大于深度时返回 -1。`isAncester` 是原稿里的拼写。`rootedParent(root, x)` 是把树换根到 `root` 后 `x` 的父节点；根的父节点返回它自己。`rootedLca(a, b, c)` 是三个普通 LCA 的异或，等于把根换成 `c` 后 `a` 和 `b` 的 LCA。

`work` 不把欧拉序计数 `cur` 清零，邻接表里的父边也已经删掉。对同一对象再调用 `work` 会写出 `seq` 的范围。ASan 在四个点的树上第二次调用时报告 heap-buffer-overflow。因此不能换根重跑。

现有 `HLD` 从 1 编号，不提供这些换根查询，不能把两份接口当成同一个模板。

`python3 tests/wida_hld.py` 在普通 `-O2` 和 ASan/UBSan 下各做 29864 项检查，另有一次第二次 `work` 的溢出记录。Codeforces 提交页面没有打开，没有新的在线 AC。来源保持 partial。
