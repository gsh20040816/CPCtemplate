# 双连通共享核心与森林视图

按 issue #7 将 Biconnected 的复合正文拆为 BiconnectedCore、block_cut_forest、bridge_component_forest。

核心一次 lowlink DFS 产生点双 blocks、割点 cut 与桥 bridge，再递归染色得到边双 bel/cnt。点双和边双同属固定 OI Wiki 的双连通分量页，在核心说明中分别列结果约定。圆方森林独立归入圆方树页，桥森林作为边双缩点视图留在双连通页，不重复 DFS。

旧 Biconnected 是不打印的兼容入口。奇环顶点、删点连通性、边双压缩和补桥直接依赖新核心/森林；P8435、P8436、P2860、POJ2942 驱动同步适配。旧提交快照不变，当前源码变化不产生新在线 AC。

核心与森林构造体经过文本等价核对。原有点/边删除参考、子集点双、桥森林证书、奇环枚举、边压缩、最少补桥、20 万点递归链等回归在普通及 ASan/UBSan 模式通过。旧接口另测重边、桥、自环、孤立点、重复 run 和空图。P8435/P8436 完整输出适配有双模式证书测试，P2860/POJ2942 的完整程序参考测试仅记普通模式，详见 verification/bcc-components.json。

当前映射已无 composite 条目；这不代表 #7 的所有附加说明/相关应用核对、#1/#11 的完整来源覆盖或在线验证完成。
