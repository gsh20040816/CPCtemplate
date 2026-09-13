# GNU 容器的位置与选型

按用户 issue #8，PBDS 有序树和 GNU rope 统一放在数据结构的平衡树板块；这条明确指示覆盖默认 OI Wiki 导航归属。平衡树条目给出 gp_hash_table / cc_hash_table 的自动页码，哈希表也给出返回有序树的页码，不手工写死页数。

| 需要做什么 | 选择与约束 |
| --- | --- |
| 排名、第k小、有序前驱后继 | ost；重复值用(value,id)，比较器必须为严格弱序 |
| 整数键的普通查改 | 可先使用已有验证的gp_map；只读查询用find，避免operator[]扩张表 |
| 插入/删除其他键后仍保留找到的元素引用 | 可考虑cc_map；不包括被删除元素、clear、销毁，也不保证遍历次序 |
| 序列插删、截取、分支快照 | rp；普通下标数组优先vector，需要区间聚合/懒标记使用序列Treap |

GCC将gp_hash_table归为探测表、cc_hash_table归为碰撞链接表，并区分点迭代器与遍历迭代器的失效保证。上表是结合接口需求的选型建议，不是固定速度排序；节点分配、缓存、负载和操作分布会影响结果。[GCC设计说明](https://gcc.gnu.org/onlinedocs/libstdc++/manual/policy_data_structures_design.html)

rope的准确名称是__gnu_cxx::rope，并非std::rope。`<ext/rope>`属于GNU扩展。[GCC rope源码](https://github.com/gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/ext/rope)

手册补充了rope复制版本、插入、删除、替换和截取示例。它不是区间聚合树，长期保留版本也不能按单个序列的空间估计；既有队列AC与直接push/erase失败案例仍保留在[ROPE-NOTES.md](ROPE-NOTES.md)，没有隐藏不利结果。

cc_map与gp_map共用hash64，限定不超过64位整数键。cc_map新增独立std::map对拍、百万稀疏键和点引用稳定性检查；手册示例另行编译运行。关联数组cc驱动以Python字典及固定版本官方checker验证。普通与ASan/UBSan报告分别存于verification/cc-*及verification/gnu-examples-*。已有GP在线AC仅覆盖GP，不能转移为CC的在线AC。
