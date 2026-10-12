# WIDA 按值平移 Splay 与持久化权值索引

已读取 `hh2048/XCPC` 的固定blob `4d7c728da88ac87eb4bccaadb44a6640fc784b5f`，原路径为 `03 - jiangly模板收集/04 - 数据结构/07A - Splay.cpp`。完整原文保存在 `tests/fixtures/wida_splay_sources/original.inc`，保留上游来源及许可，未作为本库原创代码重新授权。

旧台账把它概括为“序列Splay+主席树”不够准确：Tree按val有序，split以数值阈值分裂；add对整棵树平移；merge要求两树有序且不交叉。不存在按秩区间翻转，不能用SequenceSplay替代。旁边Node独立保存持久化count/sum，按位置插入、查询单版本区间统计，以及查询两个版本之差中不小于阈值的最小位置。权重不是计数，sum也不是用于判断有没有元素的依据。

原文只给函数片段。引用的AtCoder提交页本轮返回403，未取得完整JOI主程序与题目协议，所以不编造“JOI应用已覆盖”或线上AC。当前两个独立vector核心已接入目录、打印手册及完整API用法；JOI完整协议与线上验证仍待补，来源保持partial。

## ShiftSplay

空构造建立节点池，根0表示空树。所有根和节点编号只属于创建它们的同一个对象。`insert(root,value)`通过引用更新根，返回稳定的1-based节点编号；重复值允许，重复值之间不承诺次序。每次插入都伸展新节点，避免把原稿独立insert函数不旋转时的普通BST插入误称为均摊对数操作。

`split(root,key)`消耗一棵树，返回值严格小于key和大于等于key的两棵树根；调用方用返回根替换旧根，不再把旧根当独立树。`merge(left,right)`消耗两个不相交的根，要求左树所有值≤右树所有值，返回合并后的根。它不是任意集合合并：对交错值域请用其他组件。

`add(root,delta)`整体平移，保持内部次序。`value(root,id)`读取所属树中指定节点的当前值，同时通过引用更新该树根；id必须确实属于root代表的树。根会被访问改变，但元素编号不会。节点无删除回收，池大小等于插入数加1；普通对象拷贝独立，重置用新对象赋值。辅助字段与函数供内部实现使用，不能跨对象混用根。

所有实际值、每一次val与lazy的加法中间结果均须在signed64范围内；不承诺自动处理溢出。尤其“最终值合法”不能替代“积累懒标记也合法”的前提。无序合并、错误根/节点归属属于调用方违反约定，不额外做线性检查。

insert、split、merge、value均摊O(log(N+1))，单次最坏O(N)，add为O(1)，空间O(N)。祖先下传为递归，保留赛时栈空间约定；merge寻找最大节点无需提前下传平移，因为平移不交换儿子，最终splay会递归下传整条路径。

独立vector真值检查1393组历史，169946次树结构/排序/父指针/节点身份/实际值证书；查询身份时在原树懒标记尚未被遍历消除前进行，结构遍历使用对象副本。另有完整signed64端点的比较测试，以及20万节点顺序插入后访问最深节点、逐节点核对平移值。普通与ASan/UBSan均通过；Darwin测试提供512MiB栈，没有模拟DFS栈。证据 `verification/shift-splay-core.json`。

## PersistentWeightedIndex

构造 `PersistentWeightedIndex(n)`，位置域[0,n)，n为正int，版本0为空。`add(version,pos,weight)`从任意已有版本分叉，新增一个元素并返回新版本号：该位置count增加1，sum增加weight，weight可为负。旧版本不变，不需要事先分配n个叶子，按需创建路径。

`query(version,l,r)`返回半开位置区间的 `{count,sum}`，空区间合法。`first(before,after,key)`返回两个版本计数差中位置≥key的首个非空位置，无结果为−1。key可小于0或≥n。它要求after-before在每个位置的计数差非负，最常见合法调用是祖先版本与其后代版本。任意两个分叉版本不能直接相减后声称满足该前提；该接口不检查整个值域。first只看count，不用sum为0判断空集。

每次add新建O(log n)节点，单次query/first为O(log n)，查询不创建节点。元素总数、节点池及版本数须可用int编号；所有节点sum累加和查询合并的中间值须适配signed64。内部根与辅助递归函数不作为可写用户接口。可以通过两次query相减获取区间版本差，但减法本身也需防溢出。

独立位置数组保存每个历史分支的count/sum，500组各150次分叉插入，60万次历史区间和合法祖先版本差后继核验；含负权、重复位置、空区间和阈值越界。另验证INT_MAX位置域及LLONG_MIN单权、20万前缀版本的解析计数与权值和。普通与ASan/UBSan均通过。证据 `verification/persistent-weighted-index-core.json`。

## 完整用法与打印验证

用法430管理同一Splay节点池中的多棵树：槽0初始为空，插入输出稳定节点ID，split保留左侧并创建右侧新槽，merge清空被消耗槽，查询始终更新所属槽的根。用法431展示任意历史版本分叉、区间count/sum与合法祖先版本差的first。它们是明确标注的API演示，不是虚构OJ题目。

`tests/wida_splay_integration.py` 为每份完整程序生成80组各约200次操作的独立历史，用树槽中的元素列表、每个持久化版本的元素列表求真值；普通和ASan/UBSan检查实际打印展开后的程序。`tests/wida_splay_copy.py` 从手册的同一提取逻辑取得代码，在标准头文件上下文中重跑全部核心真值与压力测试，两个构建均通过。对应证据 `verification/wida-splay-integration.json`、`verification/wida-splay-copy.json`。固定示例另经 `tests/usage_examples.py` 检查。

catalog、依赖、OI导航和数据结构分册已整合，计数318组件、432份完整用法。函数边界明确分页，完整用法单页，不通过缩小字号或合并多条语句解决断页。

## 剩余范围

原稿逐函数运行对照已完成：固定原文不改函数体，补标准头文件和i64别名，60000次Splay结构/值证书、500000次持久化查询对照，普通及ASan/UBSan通过。原稿insert后由调用方splay、add仅传非空根、merge满足有序约束；原稿int字段保持范围内。证据verification/wida-splay-source.json。这不包含完整JOI主程序。JOI完整应用要在取得实际题面与调用协议后单独判断，不能从片段猜测。静态矩形求和已有正式模板题入口；线上判定、速度排名仍待核实，来源条目保持partial；本次不声称全库已完成。

## 静态矩形求和正式入口

用法432对接Library Checker rectangle_sum：按x排序，按y离散化建立持久化前缀版本，查询[l,r)×[d,u)用两个版本区间权值和相减。重复坐标、零权、落在1e9上界而不被右开区间包含的点均保留正确语义；最大和2e14使用signed64。预处理O(NlogN)、单次查询O(logN)、空间O(NlogN)。

240组扫描真值协议加20万重复点的最大和边界，普通及ASan/UBSan通过；固定版本Library Checker生成的14组官方数据经原官方checker全部接受，故意错误输出被拒绝。仅是本地官方数据通过，不是线上AC。证据verification/rectangle-sum.json、verification/rectangle-sum-official.json。

复现：在build/library-checker-reference固定提交e64660561a995c357cdc61ddee1bde68b80528db，设置CXX=/opt/homebrew/bin/g++-16运行其generate.py及data_structure/rectangle_sum/info.toml，再运行tests/rectangle_sum.py和tests/rectangle_sum_official.py。原始生成数据由上游hash.json核对，检查器报告记录逐组输入、答案、输出与展开源码摘要。

性能提醒（本地，不是OJ排名）：与官方离线Fenwick扫描解法同编译器C++20/O2、三组最大随机数据分别交替运行3次，持久化版本中位数用时约为参考的2.36–2.40倍，超过80%慢速提醒线。证据verification/rectangle-sum-performance.json。纯静态矩形求和优先考虑离线扫描；本入口保留作持久化历史版本组件的正式协议验证，其O(NlogN)空间也高于离线Fenwick。
