# PBDS 配对堆打印用法（189–190）

本批补齐已有 pheap 的两个正式模板题用法，不修改容器别名。它固定使用 pairing_heap_tag，不能把其句柄保证套到其他tag。仍只维护vector/STL版本。issue #9 的infra入口新增直达这两个用法的跨册链接。

## 双端优先队列

[Library Checker Double-Ended Priority Queue](https://judge.yosupo.jp/problem/double_ended_priority_queue) 支持插入、输出并删除一个最小值或最大值。0≤n≤500000、1≤q≤500000、值在[-10⁹,10⁹]；删除前保证多重集合非空。不同出现位置的重复值是不同元素。

用法189使用两个同类型大根堆，分别保存(-x,id)和(x,id)。每次插入都分配新的id并保存两个push返回的point_iterator。删最小或最大时，从对应堆读取id，先用其另一份句柄erase另一个堆中的同一出现，再pop当前堆。两个堆的有效元素始终一一对应，删除后两份句柄均失效。h中留存的失效句柄禁止解引用或再次调用erase；id不复用，因此不会误用。h的vector扩容只移动句柄对象，不移动PBDS的元素结点；reserve(n+q)减少句柄容器扩容。

本题x取负在int范围内。不能把这份符号转换直接用于包含LLONG_MIN的全int64值；那种输入应分别使用less/greater两个比较器。维护两个堆是为了展示任意位置删除句柄，不要求手写新的双端堆。top/pop只在非空时调用。

## 可修改键的最短路

[Library Checker Shortest Path](https://judge.yosupo.jp/problem/shortest_path) 是非负权简单有向图的正式模板题，2≤n≤500000、1≤m≤500000，0起点号，权0至10⁹、s≠t。无解输出-1；否则输出最短距离、边数及一条依序排列的简单路径。

用法190使用小根配对堆。每个堆内顶点保存有效句柄h[u]；改善距离时，已在堆内则modify更新，否则push并保存新的句柄。pop后in[u]=false，后续不能用旧句柄。这里最多每个点在堆中出现一次，避免用堆内重复副本替代modify。距离用long long；本题简单最短路最多n-1条边，所以所有有限距离与下一次加权松弛都在int64内。只在严格变短时更新pre，允许零权边与零权环；输出另验证无重复点。

两份用法展示push/top/pop/erase/modify。join、swap、split、复制和clear的归属或失效约定由已有独立容器回归验证，不能用这两题的通过记录替代这些接口检查。

## 验证范围

固定Library Checker上游commit e64660561a995c357cdc61ddee1bde68b80528db。双端队列的全部18组生成数据、最短路的全部29组，普通与ASan/UBSan共94次完整程序执行，通过官方checker；错误输出负对照被拒绝。official_cases --usage绑定精确打印程序及其指纹，输入集合名字与info.toml逐项一致。它是本地官方数据和checker验证，尚未新增线上AC或全提交速度排名。

tests/pheap_usages.py另执行两种独立参照，每模式1625次进程调用。双端队列以Python有序多重集合验证：空集起始的所有合法长度1至4操作序列396组，重复值/极值随机操作300组，以及n=q=500000全相同元素交替删最小/最大的一组。最短路以Floyd-Warshall检查728组三点0/1权有向图、200张随机图；输出逐边检查真实原边、连接次序、无重复点、终点和总权重。

已有tests/pbds_heap.cpp普通和ASan/UBSan复验：四个std::set参照随机修改、删除、pop、join和swap，跟踪归属；split、复制隔离、clear与20万次修改单独验证。测试算法与DFS策略不改。验证绑定入口为verification/pheap-usage-regressions.json。

当前200算法、190份完整用法：131项正式题本地覆盖、28项仅应用覆盖、41项待补；646条上游主题和完整范围仍未完成。GitHub CI保持停用。

用法189在数据结构9/总册166页；190在数据结构10–11/总册167–168页，按输出阶段明确续页并保留行号。相邻左偏树完整位于数据结构12/总册169页。三册检查12页，原字号不变；全部八册审计和12个跨册跳转通过。其余五册比对后保留原文件，当前所有用法页码见verification/usage-layout.json。
