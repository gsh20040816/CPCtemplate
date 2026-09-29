# 函数图与可持久化区间用法（171–175）

五份完整用法只打印需要的组件声明和 main；统一 vector 风格，不改变算法核心。

| 用法 | 题目 | 实际使用接口 | 性质 |
|---|---|---|---|
| 171 | [CSES1750](https://cses.fi/problemset/task/1750) | FunctionalGraph.advance | 直接跳转题 |
| 172 | [CSES1160](https://cses.fi/problemset/task/1160) | FunctionalGraph.steps | 直接最少步数题 |
| 173 | [P2921](https://www.luogu.com.cn/problem/P2921) | depth/component/cycles | USACO2008DEC应用 |
| 174 | [SP11470](https://www.luogu.com.cn/problem/SP11470) | PersistentRange.add/query | 保守记为应用，未确认非比赛来源 |
| 175 | [QOJ8240](https://qoj.ac/problem/8240) | PersistentRange.add/splice/query | ICPC2023杭州K应用 |

函数图的输入点号统一减1，只有跳转返回点号加1；最少步数的0和不可达的-1原样输出。P2921统计首次重复前访问的不同顶点，包括起点，等于入环距离加环长；它不调用advance/steps。入度剥离使用队列，不是用栈模拟DFS。

SP11470仅在树里维护相对初始数组的增量，每次查询加回原数组前缀和，省去逐点初始化。题目逻辑时间会回退并被新修改覆盖，模板版本ID却只追加，所以必须通过ver[t]映射。B之后的新C从ver[t]分支，覆盖下一逻辑时间槽，不能直接拿t充当树版本ID。EOF多组输入重新初始化所有状态。只验证add/query，不覆盖splice。

杭州K版本按左端点编号，树坐标是右端点。下一个同色位置p之前贡献加1，从p起拼接version[p+1]的后缀；查询时必须先用上次答案解码两端点。已有容量估算用递归统计可能克隆的节点数，reserve避免扩容时的峰值。此应用只查询单点，任意区间和及带懒标记的拼接依靠核心接口测试补充。

## 本地证据

运行`python3 tests/version_function_usages.py`及`CPC_SANITIZE=1 python3 tests/version_function_usages.py`，两模式均通过：

- 跳转、最少步数、访问数各389次完整程序调用：至四点全部288个后继映射、100随机映射和各自题面最大规模。独立参照逐个访问到首次重复。跳转另外覆盖2^63和ULLONG_MAX，这是模板扩展范围，不是CSES题面要求。
- 历史区间303次：300随机完整数组快照、1个EOF多组输入、2个n=m=100000实例。覆盖回退后覆盖逻辑时间、正负初值/增量、历史查询，以及99998次点修改造成节点数组扩容。
- 卡牌357次：253个长度至7的二值数组、100随机数组、4个n=q=300000实例。小数据独立逐张模拟去重规则；大数据含全同、全异、周期和稀疏重复。询问真实异或编码后再交给程序。

`tests/functional_graph.cpp`和`tests/persistent_range.cpp`的核心回归也通过普通及ASan/UBSan。函数图穷举至五点映射，含重建、别名输入、空图、50万点长链/环/自环；持久化区间核验分支快照、所有区间、带符号懒标记拼接、查询不分配节点、对数分配界和INT_MAX稀疏域。旧classic参照仅提取到临时目录，未恢复到仓库；独立暴力仍是正确性参照。

实际打印的用法171–175精确展开后执行，普通及ASan/UBSan均通过；此前170份用法的执行指纹仍有效。报告入口为`verification/version-function-regressions.json`和`verification/usage-examples.json`。

## 线上证据与缺口

P2921新增[299973954 AC](https://www.luogu.com.cn/record/299973954)：2026-09-29 23:54:13 UTC+8，GSH_gsh，C++20 O2，10点全AC，最慢单点25ms、页面累计155ms、峰值10.36MB。归档`verification/submitted/P2921.compact.cpp`与本次测试程序逐字节一致。只覆盖分解字段，不能扩大为advance/steps线上验证。

QOJ8240沿用[2939235 AC](https://qoj.ac/submission/2939235)，当前程序与历史快照格式归一化一致，非逐字节相同；本批没有重新提交该题。CSES两题仍无线上AC。SP11470提交被洛谷拒绝：第三方登录暂不能使用Remote Judge，需重新登录；未产生记录，不能记为评测失败或AC。各题全提交速度排名仍未完成。

GitHub CI保持停用；本地测试和线上结果分开记载。全库仍有未覆盖项，不宣称全部模板完成。

## 排版与当前覆盖

用法171位于图论53/总册314页；172、173在图论54/总册315页，同页放置两份完整短main。174在数据结构82/总册235页，175在数据结构84/总册237页；两份较长main完整同页，题意在前页。树上路径第k小按insert、lca方法边界分成数据结构85–87/总册238–240页，避免DFS函数头被截在页尾；不改算法、不缩字号。

可持久化说明在数据结构108–109/总册491–492页，函数图说明在图论147/总册495页。八本PDF最终构建无警告，十个跨册链接有效。数学、字符串、几何、杂项及infra的页面内容、注释和命名目的地页与旧版一致，保留原始PDF字节；仅提交数据结构、图论与总册的内容变化。布局记录见`verification/version-function-usage-layout.json`；全部175份用法页码及指纹见`verification/usage-layout.json`。

当前200项算法、175份用法：120项有正式题本地用法，26项仅有应用用法，54项仍缺完整用法。646条上游目录记录尚需去重映射；89份历史AC快照不等于89个当前算法均被完整线上覆盖。继续保留全量补充和验证任务。
