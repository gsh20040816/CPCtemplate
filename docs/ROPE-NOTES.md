# rope：接口与可持久化队列的范围

`rp<T>` 是 GNU rope 的轻量别名，通用插入、删除、替换、截取和版本隔离使用独立 vector 分支对拍验证。共享大树测试覆盖 20 万元素、1 万个独立修改副本；普通与 ASan/UBSan 日志保存在 verification/rope-*.txt。

## 已验证的在线用法

[Persistent Queue 401871](https://judge.yosupo.jp/submission/401871) 使用定长 rope 加版本化头尾下标：初始分配 Q 个零，复制版本时共享根，入队替换尾部单元，出队读取头部单元并增加下标。沿任意版本链的入队次数不超过 Q，数组容量足够；每次分支保留旧版本内容和下标。

14 个测试全部通过，942 ms、591.26 MiB。在线范围是定长构造、复制赋值、replace 和下标读取，不是通用 rope 的全部操作。提交页复制回的源码与打包文件逐字节一致。

## 必须保留的反例

[直接 push_back/erase 的版本 401870](https://judge.yosupo.jp/submission/401870) 在 half_rot_killer_00 返回 RE，页面内存 1024.00 MiB。其源码归档在 verification/submitted/LC-persistent_queue-401870-failed.cpp，未记入 AC 列表。反复从共享版本追加/删前缀可能触发代价很大的重平衡；不能由常规随机小数据推断性能。

定长版本本地 50 万操作的 half-rotation 构造输出与独立预期序列一致，峰值约 530 MB；全入队链约 1066 MB（macOS 的 resident bytes，不能与 Linux OJ 的 MiB 直接比较）。该做法仍有显著内存成本；不能替代后续专用可持久化队列的性能审计。

本地完整驱动还以独立 Python list 验证随机版本分支，普通与 ASan/UBSan 通过。线上排名仍待核对，不编造分子或分母。
