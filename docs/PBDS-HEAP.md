# GNU 配对堆

`pheap<T,C=less<T>>` 固定使用pairing_heap_tag。默认大根堆；小根堆用greater。选择它是为了modify、erase、join等接口，不能把其他tag的句柄保证照搬过来。[GCC接口与tag](https://gcc.gnu.org/onlinedocs/gcc-16.1.0/libstdc%2B%2B/api/a12629.html)

push返回point_iterator，保存后交给当前拥有元素的堆。join后源堆为空，源元素句柄交给目标堆；swap后归属随元素交换。split的目标在本模板约定为空；两堆须不同且比较规则一致。删除元素后其句柄失效，副本不能使用原堆句柄。只需普通top/push/pop时使用std::priority_queue即可。

`tests/pbds_heap.cpp` 以四个std::set为独立参考，随机修改、删除、弹出、合并、交换并跟踪句柄归属，另检查split、复制隔离、小根堆及20万次修改。普通和ASan/UBSan通过。模板题完整驱动与线上AC尚待补，不把容器对拍称为线上结果。
