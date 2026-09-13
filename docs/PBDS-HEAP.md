# GNU 配对堆

`pheap<T,C=less<T>>` 固定使用pairing_heap_tag。默认大根堆；小根堆用greater。选择它是为了modify、erase、join等接口，不能把其他tag的句柄保证照搬过来。[GCC接口与tag](https://gcc.gnu.org/onlinedocs/gcc-16.1.0/libstdc%2B%2B/api/a12629.html)

push返回point_iterator，保存后交给当前拥有元素的堆。join后源堆为空，源元素句柄交给目标堆；swap后归属随元素交换。split的目标在本模板约定为空；两堆须不同且比较规则一致。删除元素后其句柄失效，副本不能使用原堆句柄。只需普通top/push/pop时使用std::priority_queue即可。

`tests/pbds_heap.cpp` 以四个std::set为独立参考，随机修改、删除、弹出、合并、交换并跟踪句柄归属，另检查split、复制隔离、小根堆及20万次修改。普通和ASan/UBSan通过。新增 Library Checker shortest_path 完整驱动：用 modify 降低键值并输出路径，29 组固定版本官方数据在普通及 ASan/UBSan 模式通过，另以 160 张图的 Floyd-Warshall 距离及简单路径证书核验。报告见 verification/pheap-shortest-path-official*.json；官方本地检查不是线上 AC。该驱动不覆盖 join/split，它们由上述容器测试独立检查。线上 AC 与排名仍待核验。
