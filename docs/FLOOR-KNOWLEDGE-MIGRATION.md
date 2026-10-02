# 类欧几里德知识的有界迁移

本批把原 mathematics.tex 中连续的“类欧几里德：有符号整除求和”和“类欧几里德的三个求和量”移到 knowledge-floor-sums.tex，固定归属“数学 → 数论 → 类欧几里德算法”（math/number-theory/euclidean.md）。它们不是新算法或新题解：算法208、用法228及分类计数均不变。

已分类知识从19节/8份源变为21节/9份源。历史附录从77节变为75节，其中按既有路由仍有47节落入数学册；其余非数学应用说明与仅总册保留的ACL说明不冒充数学缺项。这里没有宣称全附录或OI源页面全部分类完成。

## 保留与明确修改

以4df4e2b的原文为来源，记录原片段、原文件及未修改剩余正文的哈希。除七处明确替换外，原有推导、公式、边界、来源和历史验证描述逐字保留：

1. 两个节各增加一个独立knowledge标签
2. 给floor_sum补实现节号和页号
3. floor_moments的实现引用补节号，保留页号
4. P5170用法引用明确题名并同时提供节号、页号
5. 明确moments范围及n=0直接返回(0,0,0)，含n−1的高度递推仅在n≥1使用
6. 标量floor_sum交叉核对只用于两接口共同的n≤10^9范围；moments自身的10^9+1上界没有缩小

上面的“两标签”是两次替换，因此共七次文本替换。源证据为 tests/fixtures/floor-knowledge-migration/，一次性提取记录为 verification/floor-knowledge-migration.json。tests/floor_knowledge_migration.py 验证唯一替换、完整保留、相邻顺序、单一归属和节号/页号配对，也防止分类说明继续显示旧计数。

旧文中的“双版本已验证”“线上待补”等叙述保留原批次含义；迁移不将它们变成新的在线AC或当前所有接口的整体证明。当前所选测试范围另行记录，不借用迁移前的完整回归替代。

## 定向验证方法

本批复用既有测试，未新增算法调用包装器：

- number_components.cpp：当前分拆组件的独立边界核对
- floor_sum.cpp：任意精度逐项参考、64位系数端点及大项数闭式
- floor_moments.cpp：三个量的独立参考、空和与10^9+1边界
- floor_moments_large.cpp：反转、补变换和前缀差分；与标量接口的比较仅在共同范围内，区分一致性证据与独立答案
- floor_moments_application.py：当前compact P5170驱动的十万组输入、n+1和输出f/h/g顺序；不把它重命名为两份当前应用驱动

使用既有stage_inputs及固定classic基线1a9fa3e91d7dff58915341040be069611370054c，不从当前已拆分的源码目录臆造历史头文件。普通和ASan/UBSan的定向回执为 verification/floor-knowledge-{normal,sanitizer}.json，包含原/暂存输入指纹、实际命令/日志、编译器驱动/前端前后身份及辅助运行脚本哈希。结果以回执status为准，schema明确为TARGETED子集，不是全库回归。GNU14.2、已有Boost头文件、默认PIE/quarantine、LSan关闭；软栈设置仅限子进程且不改变硬限制。

分类、正文保留和本次迁移检查另运行；无线上提交或CI查询。最新完整回归证明c187091（说明修正b8b1c7b）绑定此前4df4e2b，不能自动覆盖本次文档和测试输入变化。

## PDF与剩余范围

字体和核心实现未改。总册629页、数学册215页；实际检查新归属位置、前后用法/章节、旧附录抽取接合处及infra索引共13个物理页。infra第10物理页的FFT/NTT引用页码随数学册更新，保留新版本；其余5份PDF确认文本、目标与链接注释一致后恢复原字节。视觉和布局记录见 verification/floor-knowledge-{visual,layout}.json。

类欧几里德只覆盖这两套既有接口，不因此支持任意高次矩。其余历史知识仍逐步处理；Matrix Tree材料需要遵从既定图论叶子，不能为了“三层数学”另造分类。既有浮点圆交点精度、FFT条件和线上证据限制保持不变。
