# 配套知识的 OI Wiki 分类

本表给三十五份知识源文件中的 **102 个带标签节** 登记显式分类。LTE、Lagrange反演、有限状态递推与广义容斥是新增知识正文，另有两节类欧几里德与两节矩阵树及一节整数分拆内容从旧附录迁移，矩阵树补充统一证明、分拆补充限制转换；另迁移一节模运算条件，补非单位元、升模整除与降幂阈值；另补一节Catalan与投票反射建模，并迁移一次不定方程、补矩形约束计数，新增数值积分与曼哈顿最小生成树证明，迁出Pick公式并补几何剖分证明，新增Prüfer计数与Legendre／Kummer赋值解释；本批另新增斯特林定义与反演两节；其余15节保留原主题，静态ModInt扩展时同步更新模概率节的接口前提，并把组合数扩表的求逆实现说明同步为扩展欧几里得；分类本身不新增算法、模板覆盖或 OJ 验证记录。

## 固定来源与范围

- 官方导航使用与算法分类相同的固定版本：[bc070e827180](https://github.com/OI-wiki/OI-wiki/blob/bc070e827180fbd75c2e27a16c1212f1d671d949/mkdocs.yml)
- 本地来源为 [`references/oi-wiki-mkdocs.yml`](references/oi-wiki-mkdocs.yml)，SHA256：`de5d096840edf7d9e28e8b79fa25ccbb53ce2621d888bc0d09380fbb07c26806`
- 路径、完整大中小分类名和先后顺序取自 [`oi-taxonomy.json`](oi-taxonomy.json) 的 `navigation`，不另造 OI Wiki 叶子
- 分类数据为 [`knowledge-taxonomy.json`](knowledge-taxonomy.json)；源文件仍为 `knowledge-combinatorics.tex`、`knowledge-probability-games.tex`、`knowledge-mobius.tex`、`knowledge-orbits.tex`、`knowledge-lte.tex`、`knowledge-lagrange.tex`、`knowledge-state-recurrence.tex`、`knowledge-inclusion.tex`、`knowledge-floor-sums.tex`、`knowledge-matrix-tree.tex`、`knowledge-partitions.tex`、`knowledge-modular-conditions.tex`、`knowledge-ballot.tex`、`knowledge-diophantine.tex`、`knowledge-integration.tex`、`knowledge-manhattan-mst.tex`、`knowledge-pick.tex`
- 杜教筛、64 位判素、单个欧拉函数、线性筛和区间筛已迁入 `knowledge-sieve-notes.tex`。矩形 GCD、幂的约数和、批量逆元、线性逆元、线性同余、扩展 CRT 与 Garner 已迁入 `knowledge-arithmetic-notes.tex`。二次剩余、原根、Carmichael、Lucas、扩展 Lucas 和阶乘表已迁入 `knowledge-residues.tex`。组合计数、生成函数与递推、线性代数与生成树、模线性方程组、数值边界和线性递推已迁入 `knowledge-model-notes.tex`。素数模、素数幂模、合数模高次剩余和自动准备原根已迁入 `knowledge-higher-residues.tex`。任意正模数行列式、参数化 NTT、Bostan–Mori、集合变换和 Taylor 平移已迁入 `knowledge-poly-notes.tex`。带余除法、开根、ln/exp、大指数幂、集合逆变换和浮点 FFT 已迁入 `knowledge-poly-funcs.tex`。可持久化区间拼接和杭州 2023 K 已迁入 `knowledge-persistent-notes.tex`。树路径交和点集直径已迁入 `knowledge-tree-notes.tex`。带修莫队已迁入 `knowledge-mo-notes.tex`。莫队二次离线已迁入 `knowledge-mo-secondary.tex`。函数图、杭州 2023 H 和杭州 2023 G 已迁入 `knowledge-functional-notes.tex`。SCC、并查集、ACL 约定、动态树路径乘积、Treap 和替罪羊树已迁入 `knowledge-structure-notes.tex`。线段树扫描、K-D 树、CDQ 卷积、SPFA 费用流和 2-SAT 已迁入 `knowledge-query-notes.tex`。回文、后缀、单位边流、树上用法、模 2 消元、严格次小生成树和闭合集已迁入 `knowledge-application-notes.tex`。压位小波矩阵仍留在 `mathematics.tex`：固定导航没有小波矩阵页，不能改记成划分树。`mathematics.tex` 的其余历史知识节尚未逐项分类，继续保留在附录；这些历史内容还混有其他分册的应用说明。本次不声称完成全部数学知识重排或 issue #5/#7 的全部范围
- 导航来源是固定的 OI Wiki 官方仓库，不声称已核验 `oi-wiki.com` 与该导航相同，也不要求实时网站提供相同路径

## 数据与生成约定

`entries` 每项用 `label` 唯一标识现有整节；`source` 是相对仓库根目录的源文件；`path` 是唯一主归属叶子；`additional` 只说明跨页关联，不产生第二份正文。`relation` 为 `direct`（直接主题）、`application`（该主题的应用）或 `composite`（横跨多个主题），`note` 说明归类依据和边界。

`page_break_before` 可选布尔值只控制知识节前换页，并在分类标题之前执行，避免标题落在上一页。标题只用于显示，既不用于分类，也不用于定位。读取源文件后以节内的精确标签配对；大、中、小标题与排序从固定导航路径查询。多个知识节可以属于同一叶子；同叶子内按清单顺序保留。跨主题的整节不拆散、不重复，并保留其公式、列表、例子、代码、标签与交叉引用。

总册和对应所属分册使用同一份分类数据，把知识节并入对应叶子。生成历史附录时仅跳过这些已登记源文件的原有输入，避免重复；原始 `mathematics.tex` 与已登记知识源文件继续保留。知识不是算法目录条目，不能加入算法覆盖或评测统计。

## 逐节归属

| 标签 / 源文件 | 唯一主归属（固定导航完整层级） | 关系与说明 |
| --- | --- | --- |
| `knowledge-counting-model`<br>`docs/knowledge-combinatorics.tex` | 数学 → 组合数学 → 排列组合<br>`math/combinatorics/combination.md` | composite：以可区分对象、容器与次序为主的计数建模；同时说明 OGF/EGF 的选型，不代表覆盖所有排列组合或生成函数内容。<br>关联：数学 → 多项式与生成函数 → 符号化方法；数学 → 多项式与生成函数 → 普通生成函数；数学 → 多项式与生成函数 → 指数生成函数 |
| `knowledge-binomial-choice`<br>`docs/knowledge-combinatorics.tex` | 数学 → 组合数学 → 排列组合<br>`math/combinatorics/combination.md` | composite：组合数实现选型与资源边界为主；Lucas、扩展 Lucas 和模逆元条件另列关联页，不将选型说明计作新增实现。<br>关联：数学 → 数论 → 卢卡斯定理；数学 → 数论 → 模逆元 |
| `knowledge-generating-examples`<br>`docs/knowledge-combinatorics.tex` | 数学 → 多项式与生成函数 → 符号化方法<br>`math/poly/symbolic-method.md` | composite：三个例子按组合对象构造生成函数，涵盖 OGF 乘积、OGF 序列求逆和 EGF 集合指数；整节保留一次，不能归成仅 OGF 或仅 EGF。<br>关联：数学 → 多项式与生成函数 → 普通生成函数；数学 → 多项式与生成函数 → 指数生成函数；数学 → 多项式与生成函数 → 多项式初等函数；数学 → 多项式与生成函数 → 多项式牛顿迭代 |
| `knowledge-expectation`<br>`docs/knowledge-probability-games.tex` | 数学 → 概率论 → 随机变量的数字特征<br>`math/probability/exp-var.md` | direct：指示变量、期望线性性、尾和与方差条件；主归随机变量的数字特征，仅登记现有知识内容。 |
| `knowledge-probability-dp`<br>`docs/knowledge-probability-games.tex` | 数学 → 概率论 → 随机变量的数字特征<br>`math/probability/exp-var.md` | application：期望的第一步分析与吸收状态应用；条件概率和高斯消元为关联工具，有限性条件仍保留在原文。<br>关联：数学 → 概率论 → 条件概率与独立性；数学 → 数值算法 → 高斯消元 |
| `knowledge-mod-probability`<br>`docs/knowledge-probability-games.tex` | 数学 → 概率论 → 随机变量的数字特征<br>`math/probability/exp-var.md` | composite：以概率与期望的有理数模表示为主线；跨越模逆元、模线性系统的可解性，固定导航没有独立模概率叶子，不自造分类。<br>关联：数学 → 数论 → 模算术简介；数学 → 数论 → 模逆元；数学 → 数值算法 → 高斯消元 |
| `knowledge-sg`<br>`docs/knowledge-probability-games.tex` | 数学 → 博弈论 → 公平组合游戏<br>`math/game-theory/impartial-game.md` | direct：有限无偏正常玩法的 SG 定义、不交和与异或策略；保留全部适用前提，不扩展为通用博弈算法覆盖。 |
| `knowledge-subtraction-game`<br>`docs/knowledge-probability-games.tex` | 数学 → 博弈论 → 公平组合游戏<br>`math/game-theory/impartial-game.md` | application：减法游戏是公平组合游戏的具体应用；反常、有环与有偏情形仅为误用边界，有偏游戏关联页不表示已完成其理论或实现。<br>关联：数学 → 博弈论 → 非公平组合游戏 |
| `knowledge-mobius-model`<br>`docs/knowledge-mobius.tex` | 数学 → 数论 → 莫比乌斯反演<br>`math/number-theory/mobius.md` | composite：莫比乌斯反演的约数、倍数方向及 GCD 加权建模为主；卷积恒等式对应狄利克雷卷积关联页。<br>关联：数学 → 数论 → 狄利克雷卷积 |
| `knowledge-gcd-domains`<br>`docs/knowledge-mobius.tex` | 数学 → 数论 → 莫比乌斯反演<br>`math/number-theory/mobius.md` | application：互质矩形与 GCD 计数是反演应用；缩放、容斥、对称性及欧拉函数化简随原节保留。<br>关联：数学 → 数论 → 最大公约数；数学 → 数论 → 欧拉函数；数学 → 组合数学 → 容斥原理 |
| `knowledge-quotient-choice`<br>`docs/knowledge-mobius.tex` | 数学 → 数论 → 数论分块<br>`math/number-theory/sqrt-decomposition.md` | composite：双商整除分块为主；预筛与杜教筛是前缀和来源的选型，不能把外层分块复杂度当作整体复杂度。<br>关联：数学 → 数论 → 筛法；数学 → 数论 → 狄利克雷双曲线法 & 杜教筛 |
| `knowledge-orbits-model`<br>`docs/knowledge-orbits.tex` | 数学 → 组合数学 → Pólya 计数<br>`math/combinatorics/polya.md` | direct：轨道、稳定子与 Burnside 引理作为对称计数基础；群作用关联群论，不表示完整群论覆盖。<br>关联：数学 → 抽象代数 → 群论 |
| `knowledge-orbits-dihedral`<br>`docs/knowledge-orbits.tex` | 数学 → 组合数学 → Pólya 计数<br>`math/combinatorics/polya.md` | application：项链与手链通过旋转、反射的循环分类计数；退化长度及非忠实作用边界随原节保留。 |
| `knowledge-orbits-inventory`<br>`docs/knowledge-orbits.tex` | 数学 → 组合数学 → Pólya 计数<br>`math/combinatorics/polya.md` | application：固定颜色库存对应 Pólya 的循环指标代换；系数提取及组合数为关联方法，不复制整节到其他叶子。<br>关联：数学 → 多项式与生成函数 → 普通生成函数；数学 → 组合数学 → 排列组合 |
| `knowledge-orbits-modular`<br>`docs/knowledge-orbits.tex` | 数学 → 组合数学 → Pólya 计数<br>`math/combinatorics/polya.md` | application：轨道数的群阶除法应用：不可逆时先提升模数再整除；模算术和逆元仅是关联条件，示例并非新增通用算法。<br>关联：数学 → 数论 → 模算术简介；数学 → 数论 → 模逆元 |

| `knowledge-lte`<br>`docs/knowledge-lte.tex` | 数学 → 数论 → 升幂引理<br>`math/number-theory/lift-the-exponent.md` | direct：非零整数估值、奇素数和2的LTE、约公共因子、条件反例和整除应用；不代表完整p进数理论或新增算法。 |

| `knowledge-lagrange-inversion`<br>`docs/knowledge-lagrange.tex` | 数学 → 多项式与生成函数 → Lagrange 反演<br>`math/poly/lagrange-inversion.md` | direct：形式级数取系数公式、留数证明、有序多叉树与带标号有根树、现有FPS幂接口及模除法边界；不新增通用复合/复合逆或在线AC。<br>关联：复合逆、符号化方法、OGF、EGF、多项式初等函数、模逆元 |

| `knowledge-state-recurrence`<br>`docs/knowledge-state-recurrence.tex` | 数学 → 线性代数 → 特征多项式<br>`math/linear-algebra/char-poly.md` | composite：固定有限状态模型经Cayley–Hamilton证明递推阶数，再恢复指定标量序列与求远项；不新增特征多项式或矩阵最小多项式实现。<br>关联：BM、常系数齐次线性递推、矩阵 |

| `knowledge-inclusion-exact`<br>`docs/knowledge-inclusion.tex` | 数学 → 组合数学 → 容斥原理<br>`math/combinatorics/inclusion-exclusion-principle.md` | direct：交集和重数、恰好/至少反演、双向下标、空盒模型、现有模整数/组合数接口与边界；不新增算法或OJ覆盖。<br>关联：排列组合、斯特林数 |

| `knowledge-floor-sum`<br>`docs/knowledge-floor-sums.tex` | 数学 → 数论 → 类欧几里德算法<br>`math/number-theory/euclidean.md` | direct：迁移既有有符号规范化和格点交换推导，补全实现节号/页号；不新增算法或OJ覆盖。 |
| `knowledge-floor-moments`<br>`docs/knowledge-floor-sums.tex` | 数学 → 数论 → 类欧几里德算法<br>`math/number-theory/euclidean.md` | direct：迁移三个矩的归一化、高度递推与历史验证；明确空和及与基本floor_sum共同范围，不扩大任意高次矩范围。 |

| `knowledge-matrix-tree-weighted`<br>`docs/knowledge-matrix-tree.tex` | 图论 → 矩阵树定理<br>`graph/matrix-tree.md` | direct：带权构造、根方向与按行展开的统一证明；关联行列式，不扩展历史在线范围。 |
| `knowledge-matrix-tree-mod`<br>`docs/knowledge-matrix-tree.tex` | 图论 → 矩阵树定理<br>`graph/matrix-tree.md` | direct：任意正模数接口及溢出边界；定理无除法，消元实现仍须正确选择。 |

| `knowledge-partitions`<br>`docs/knowledge-partitions.tex` | 数学 → 组合数学 → 整数分拆<br>`math/combinatorics/partition.md` | direct：既有五边形递推、重数限制及历史记录；补共轭、恰好部分数、阶梯和禁止倍数转换，不新增接口。 |

| `knowledge-modular-conditions`<br>`docs/knowledge-modular-conditions.tex` | 数学 → 数论 → 模算术简介<br>`math/number-theory/mod-arithmetic.md` | composite：模运算条件、非单位元同余、已知整除的升模方法与指数阈值；关联模逆元、线性同余、CRT、Lucas、费马/欧拉，不新增算法。 |

| `knowledge-ballot-reflection`<br>`docs/knowledge-ballot.tex` | 数学 → 组合数学 → 卡特兰数<br>`math/combinatorics/catalan.md` | composite：弱/严格前缀、初始高度反射双射与组合数模运算选型；关联排列组合，不扩张为双边界或非单位步长。 |

| `knowledge-diophantine-bounds`<br>`docs/knowledge-diophantine.tex` | 数学 → 数论 → 裴蜀定理 & 一次不定方程<br>`math/number-theory/bezouts.md` | direct：裴蜀特解与有符号矩形参数区间，不误归类欧几里德整除和，不新增实现或线上记录。 |

| `knowledge-adaptive-integration`<br>`docs/knowledge-integration.tex` | 数学 → 数值算法 → 数值积分<br>`math/numerical/integral.md` | direct：估计与误差预算、资源停止、光滑混叠反例，不冒充严格误差证书。 |

| `knowledge-manhattan-mst`<br>`docs/knowledge-manhattan-mst.tex` | 图论 → 生成树问题 → 最小生成树<br>`graph/mst.md` | direct：四向闭锥、零链收缩与平局安全的割证明；不是受限边集问题。 |

| `knowledge-pick`<br>`docs/knowledge-pick.tex` | 计算几何 → Pick 定理<br>`geometry/pick.md` | direct：边界gcd、本原三角形、相容剖分及孔洞修正；旧混合节保留，未新增算法。 |

| `knowledge-prufer`<br>`docs/knowledge-prufer.tex` | 图论 → Prüfer 序列<br>`graph/prufer.md` | composite：双射、有标号度数/叶子计数、乘积权与连通块；不新增API。 |

| `knowledge-valuations`<br>`docs/knowledge-valuations.tex` | 数学 → 数论 → 阶乘取模<br>`math/number-theory/factorial.md` | composite：阶乘赋值、数位和、进位与整除阈值；不扩大ExLucas契约。 |

| `knowledge-stirling-definitions`<br>`docs/knowledge-stirling.tex` | 数学 → 组合数学 → 斯特林数<br>`math/combinatorics/stirling.md` | direct：定义、生成函数与四种行列算法推导。 |
| `knowledge-stirling-inversion`<br>`docs/knowledge-stirling.tex` | 数学 → 组合数学 → 斯特林数<br>`math/combinatorics/stirling.md` | direct：有/无符号反演、基底变换与应用。 |

| `knowledge-dujiao`<br>`docs/knowledge-sieve-notes.tex` | 数学 → 数论 → 狄利克雷双曲线法 & 杜教筛<br>`math/number-theory/hyperbola.md` | direct：预筛、商段与缓存写回；不把单次空间当成多询问上界。 |
| `knowledge-miller-bounds`<br>`docs/knowledge-sieve-notes.tex` | 数学 → 数论 → 素数<br>`math/number-theory/prime.md` | direct：固定七底的 64 位判素范围，不外推任意精度。 |
| `knowledge-phi-single`<br>`docs/knowledge-sieve-notes.tex` | 数学 → 数论 → 欧拉函数<br>`math/number-theory/euler-totient.md` | direct：单个正整数的试除与分解入口；不把 P4718 记成新 AC。 |
| `knowledge-linear-sieve`<br>`docs/knowledge-sieve-notes.tex` | 数学 → 数论 → 筛法<br>`math/number-theory/sieve.md` | direct：最小质因子、欧拉函数、莫比乌斯函数三张表。 |
| `knowledge-segmented-sieve`<br>`docs/knowledge-sieve-notes.tex` | 数学 → 数论 → 筛法<br>`math/number-theory/sieve.md` | application：只保存目标区间的素数筛；尚无在线 AC。 |

| `knowledge-coprime-rectangles`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 莫比乌斯反演<br>`math/number-theory/mobius.md` | application：矩形互质计数与 gcd=k 的四前缀容斥。 |
| `knowledge-divisor-power-sum`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 狄利克雷卷积<br>`math/number-theory/dirichlet.md` | direct：幂的约数和；合数模不除以 p-1。 |
| `knowledge-batch-inverse`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 模逆元<br>`math/number-theory/inverse.md` | direct：任意数组的前缀积批量逆元。 |
| `knowledge-linear-inverses`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 模逆元<br>`math/number-theory/inverse.md` | application：连续整数线性逆元表。 |
| `knowledge-linear-congruence`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 线性同余方程<br>`math/number-theory/linear-equation.md` | direct：最小非负解与最小正周期。 |
| `knowledge-excrt`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 中国剩余定理<br>`math/number-theory/crt.md` | direct：不要求两两互素的逐式合并。 |
| `knowledge-garner`<br>`docs/knowledge-arithmetic-notes.tex` | 数学 → 数论 → 中国剩余定理<br>`math/number-theory/crt.md` | application：混合进制重建与规范代表元。 |

| `knowledge-quadratic-residue`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 二次剩余<br>`math/number-theory/quad-residue.md` | direct：奇素数模的 Euler 判别与 Cipolla；不含合数模。 |
| `knowledge-primitive-root`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 阶 & 原根<br>`math/number-theory/primitive-root.md` | direct：乘法阶与原根存在条件。 |
| `knowledge-carmichael`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 费马小定理 & 欧拉定理<br>`math/number-theory/fermat.md` | application：最小公共指数与 Korselt 条件，不新增判素接口。 |
| `knowledge-lucas`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 卢卡斯定理<br>`math/number-theory/lucas.md` | direct：素数模组合数按素数进制逐位计算。 |
| `knowledge-exlucas`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 卢卡斯定理<br>`math/number-theory/lucas.md` | application：合数模拆成素数幂后再 CRT 合并。 |
| `knowledge-factorial-table`<br>`docs/knowledge-residues.tex` | 数学 → 数论 → 阶乘取模<br>`math/number-theory/factorial.md` | direct：阶乘表给出组合数与排列数的查表范围。 |

| `knowledge-counting-identities`<br>`docs/knowledge-model-notes.tex` | 数学 → 组合数学 → 容斥原理<br>`math/combinatorics/inclusion-exclusion-principle.md` | composite：容斥、反演、Catalan 差分式和球盒表。 |
| `knowledge-generating-recurrence`<br>`docs/knowledge-model-notes.tex` | 数学 → 多项式与生成函数 → 普通生成函数<br>`math/poly/ogf.md` | composite：OGF/EGF 乘法与 BM 不能代替递推证明。 |
| `knowledge-matrix-span`<br>`docs/knowledge-model-notes.tex` | 数学 → 线性代数 → 矩阵<br>`math/linear-algebra/matrix.md` | composite：特解加零空间，以及无向生成树余子式。 |
| `knowledge-widget-gauss`<br>`docs/knowledge-model-notes.tex` | 数学 → 数值算法 → 高斯消元<br>`math/numerical/gauss.md` | application：工厂工期是模 7 的线性方程组。 |
| `knowledge-numerical-boundaries`<br>`docs/knowledge-model-notes.tex` | 数学 → 数值算法 → 数值积分<br>`math/numerical/integral.md` | composite：积分奇点、排序弱序、三分与二分的前提。 |
| `knowledge-recurrence-direction`<br>`docs/knowledge-model-notes.tex` | 数学 → 多项式与生成函数 → 常系数齐次线性递推<br>`math/poly/linear-recurrence.md` | direct：系数方向与外推前的阶数证明。 |

| `knowledge-higher-residue`<br>`docs/knowledge-higher-residues.tex` | 数学 → 数论 → 高次剩余 & 单位根<br>`math/number-theory/residue.md` | direct：素数模高次剩余与单位根的存在条件。 |
| `knowledge-prime-power-residue`<br>`docs/knowledge-higher-residues.tex` | 数学 → 数论 → 高次剩余 & 单位根<br>`math/number-theory/residue.md` | application：素数幂模上从素数模的根提升。 |
| `knowledge-composite-residue`<br>`docs/knowledge-higher-residues.tex` | 数学 → 数论 → 高次剩余 & 单位根<br>`math/number-theory/residue.md` | application：合数模按素数幂分解后再 CRT 合并。 |
| `knowledge-residue-setup`<br>`docs/knowledge-higher-residues.tex` | 数学 → 数论 → 阶 & 原根<br>`math/number-theory/primitive-root.md` | application：自动准备模数分解与原根，不扩大原根存在范围。 |

| `knowledge-det-mod`<br>`docs/knowledge-poly-notes.tex` | 数学 → 线性代数 → 行列式<br>`math/linear-algebra/determinant.md` | direct：任意正模数行列式；合数模不能随意除。 |
| `knowledge-ntt-moduli`<br>`docs/knowledge-poly-notes.tex` | 数学 → 多项式与生成函数 → 快速数论变换<br>`math/poly/ntt.md` | direct：NTT 模数需要足够的 2 的幂因子和原根。 |
| `knowledge-bostan-mori`<br>`docs/knowledge-poly-notes.tex` | 数学 → 多项式与生成函数 → 常系数齐次线性递推<br>`math/poly/linear-recurrence.md` | application：Bostan–Mori 只求递推的单项。 |
| `knowledge-subset-conv`<br>`docs/knowledge-poly-notes.tex` | 数学 → 多项式与生成函数 → 快速沃尔什变换<br>`math/poly/fwt.md` | direct：集合变换与不相交子集卷积的模数条件。 |
| `knowledge-poly-shift`<br>`docs/knowledge-poly-notes.tex` | 数学 → 多项式与生成函数 → 多项式平移\|连续点值平移<br>`math/poly/shift.md` | direct：Taylor 平移与等比点求值只覆盖所需前缀。 |

| `knowledge-poly-division`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 多项式牛顿迭代<br>`math/poly/newton.md` | direct：带余除法先反转再求逆。 |
| `knowledge-poly-sqrt`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 多项式初等函数<br>`math/poly/elementary-func.md` | direct：开根处理前导零和自由尾项。 |
| `knowledge-poly-ln-exp`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 多项式初等函数<br>`math/poly/elementary-func.md` | direct：ln 与 exp 只保留所需前缀。 |
| `knowledge-poly-power`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 多项式初等函数<br>`math/poly/elementary-func.md` | application：大指数幂保留底数、指数和前导移位。 |
| `knowledge-fwt-inverse`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 快速沃尔什变换<br>`math/poly/fwt.md` | application：逆变换要求模数能除以 2 的幂。 |
| `knowledge-float-fft`<br>`docs/knowledge-poly-funcs.tex` | 数学 → 多项式与生成函数 → 快速傅里叶变换<br>`math/poly/fft.md` | direct：浮点 FFT 在舍入前约束最坏误差。 |

| `knowledge-persistent-concat`<br>`docs/knowledge-persistent-notes.tex` | 数据结构 → 可持久化数据结构 → 可持久化线段树<br>`ds/persistent-seg.md` | direct：区间拼接与懒标记的边界，不新增接口。 |
| `knowledge-hangzhou-k`<br>`docs/knowledge-persistent-notes.tex` | 数据结构 → 可持久化数据结构 → 可持久化线段树<br>`ds/persistent-seg.md` | application：杭州 2023 K 的跨版本拼接，不扩大契约。 |

| `knowledge-path-intersection`<br>`docs/knowledge-tree-notes.tex` | 图论 → 树上问题 → 最近公共祖先<br>`graph/lca.md` | application：用 LCA 投影判断树路径是否相交，距离按边数。 |
| `knowledge-set-diameter`<br>`docs/knowledge-tree-notes.tex` | 图论 → 树上问题 → 树的直径<br>`graph/tree-diameter.md` | direct：非负权点集只需保存直径两端。 |

| `knowledge-mo-time`<br>`docs/knowledge-mo-notes.tex` | 杂项 → 离线算法 → 莫队算法 → 带修改莫队<br>`misc/modifiable-mo-algo.md` | direct：用时间轴记录修改，并在区间移动时应用或撤销。 |

| `knowledge-mo-secondary`<br>`docs/knowledge-mo-secondary.tex` | 杂项 → 离线算法 → 莫队算法 → 莫队二次离线<br>`misc/mo-algo-secondary-offline.md` | direct：把区间询问拆成前缀事件，并扣除询问自身。 |

| `knowledge-functional-graph`<br>`docs/knowledge-functional-notes.tex` | 图论 → 图论相关概念<br>`graph/concept.md` | direct：固定导航没有单独的函数图页；入环链记在图论相关概念下。 |
| `knowledge-hangzhou-h`<br>`docs/knowledge-functional-notes.tex` | 图论 → 图论相关概念<br>`graph/concept.md` | application：杭州 2023 H 的成功概率是阶乘倒数，不验证跳转接口。 |
| `knowledge-hangzhou-g`<br>`docs/knowledge-functional-notes.tex` | 图论 → 最短路问题 → 最短路<br>`graph/shortest-path.md` | application：开放时间下的单位边最短路，不能用于一般边权。 |

| `knowledge-scc-template`<br>`docs/knowledge-structure-notes.tex` | 图论 → 连通性相关 → 强连通分量<br>`graph/scc.md` | application：模板题输出。局部名单名次不是全站排名。 |
| `knowledge-dsu-template`<br>`docs/knowledge-structure-notes.tex` | 数据结构 → 并查集 → 并查集<br>`ds/dsu.md` | application：P3367 只覆盖 merge、same 和 find。 |
| `knowledge-acl-compose`<br>`docs/knowledge-structure-notes.tex` | 数据结构 → 线段树 → 线段树基础<br>`ds/seg.md` | composite：懒标记先 g 后 f；SCC 与 2-SAT 编码不能互换。 |
| `knowledge-lct-product`<br>`docs/knowledge-structure-notes.tex` | 数据结构 → 动态树 → Link Cut Tree<br>`ds/lct.md` | application：固定树路径乘积，不含连边和删边。 |
| `knowledge-treap-flip`<br>`docs/knowledge-structure-notes.tex` | 数据结构 → 二叉搜索树 & 平衡树 → Treap<br>`ds/treap.md` | direct：逐位取反不同于区间顺序反转。 |
| `knowledge-scapegoat`<br>`docs/knowledge-structure-notes.tex` | 数据结构 → 二叉搜索树 & 平衡树 → 替罪羊树<br>`ds/sgt.md` | direct：副本、物理节点和活键分开计数。 |

| `knowledge-seg-stack`<br>`docs/knowledge-query-notes.tex` | 数据结构 → 线段树 → 线段树基础<br>`ds/seg.md` | composite：线段树做双向扫描，根上计算雨水体积。 |
| `knowledge-kdt-sum`<br>`docs/knowledge-query-notes.tex` | 数据结构 → K-D Tree<br>`ds/kdt.md` | direct：矩形和的重建边界；查询最坏仍是线性。 |
| `knowledge-cdq-conv`<br>`docs/knowledge-query-notes.tex` | 杂项 → 离线算法 → CDQ 分治<br>`misc/cdq-divide.md` | direct：贡献只跨越一次，实现用 NTT 而不是级数求逆。 |
| `knowledge-spfa-cost`<br>`docs/knowledge-query-notes.tex` | 图论 → 网络流 → 费用流<br>`graph/flow/min-cost.md` | application：允许负边，不允许负环。 |
| `knowledge-twosat-bcc`<br>`docs/knowledge-query-notes.tex` | 图论 → 2-SAT<br>`graph/2-sat.md` | composite：真值方向绑定 SCC 编号序，并写出点双定义。 |

| `knowledge-palindrome`<br>`docs/knowledge-application-notes.tex` | 字符串 → Manacher<br>`string/manacher.md` | composite：奇偶半径与回文树的出现次数不是同一契约。 |
| `knowledge-suffix-bounds`<br>`docs/knowledge-application-notes.tex` | 字符串 → 后缀数组 (SA) → 后缀数组简介<br>`string/sa.md` | composite：整数入口先离散化；SAM 次数按长度倒序。 |
| `knowledge-general-sam`<br>`docs/knowledge-application-notes.tex` | 字符串 → 广义后缀自动机<br>`string/general-sam.md` | direct：点数按 endpos，不是后缀 DFA 的最少状态。 |
| `knowledge-flow-units`<br>`docs/knowledge-application-notes.tex` | 图论 → 网络流 → 最大流<br>`graph/flow/max-flow.md` | application：单位边分类用残量 SCC，不是最小割。 |
| `knowledge-tree-uses`<br>`docs/knowledge-application-notes.tex` | 图论 → 树上问题 → 树分治<br>`graph/tree-divide.md` | composite：点分治、启发式合并与虚树最小边。 |
| `knowledge-gauss-xor`<br>`docs/knowledge-application-notes.tex` | 数学 → 数值算法 → 高斯消元<br>`math/numerical/gauss.md` | direct：模 2 消元给出特解和零空间基。 |
| `knowledge-second-mst`<br>`docs/knowledge-application-notes.tex` | 图论 → 生成树问题 → 最小生成树<br>`graph/mst.md` | application：严格次小要删不同权的第二大边。 |
| `knowledge-switch-min`<br>`docs/knowledge-application-notes.tex` | 数学 → 数值算法 → 高斯消元<br>`math/numerical/gauss.md` | application：最少开关枚举零空间，不数一份特解。 |
| `knowledge-closure-cuts`<br>`docs/knowledge-application-notes.tex` | 图论 → 网络流 → 最小割<br>`graph/flow/min-cut.md` | composite：闭合集、最小树形图和全局割。 |

## 本地检查

运行 `python3 tests/knowledge_taxonomy.py`。该检查独立解析固定导航源文件，验证快照哈希与生成导航一致、102 个知识标签恰好各映射一次、源路径和叶子路径有效、主归属遵从固定导航：数学68节为三级，数据结构9节中 K-D 树为二级、其余为三级，另有3节图论三级叶子，函数图两节归入图论相关概念二级叶子，矩阵树2节为图论的既定二级叶子，曼哈顿最小生成树1节归入图论的最小生成树三级叶子，Prüfer1节归入图论的既定二级叶子，Pick1节归入计算几何的既定二级叶子，以及范围声明仍明确保留历史知识未分类的限制。负例检查覆盖重复、遗漏、错误源文件、未知叶子和擅自扩大范围；改标题而不改标签不会改变分类。

这是分类数据检查，不是算法正确性、完整回归、线上 AC 或 PDF 视觉验收。数学例子与接口的原有验证仍见各知识源文件和 `tests/math_knowledge_*.py`。
