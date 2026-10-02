# 配套数学知识的 OI Wiki 分类

本表给六份知识源文件中的 **17 个带标签节** 登记显式分类。LTE与Lagrange反演是新增知识正文，其余15节保持原内容；分类本身不新增算法、模板覆盖或 OJ 验证记录。

## 固定来源与范围

- 官方导航使用与算法分类相同的固定版本：[bc070e827180](https://github.com/OI-wiki/OI-wiki/blob/bc070e827180fbd75c2e27a16c1212f1d671d949/mkdocs.yml)
- 本地来源为 [`references/oi-wiki-mkdocs.yml`](references/oi-wiki-mkdocs.yml)，SHA256：`de5d096840edf7d9e28e8b79fa25ccbb53ce2621d888bc0d09380fbb07c26806`
- 路径、完整大中小分类名和先后顺序取自 [`oi-taxonomy.json`](oi-taxonomy.json) 的 `navigation`，不另造 OI Wiki 叶子
- 分类数据为 [`knowledge-taxonomy.json`](knowledge-taxonomy.json)；源文件仍为 `knowledge-combinatorics.tex`、`knowledge-probability-games.tex`、`knowledge-mobius.tex`、`knowledge-orbits.tex`、`knowledge-lte.tex`、`knowledge-lagrange.tex`
- **`mathematics.tex` 的其余历史知识节尚未逐项分类**，继续保留在附录；这些历史内容还混有其他分册的应用说明。本次不声称完成全部数学知识重排或 issue #5/#7 的全部范围
- 导航来源是固定的 OI Wiki 官方仓库，不声称已核验 `oi-wiki.com` 与该导航相同，也不要求实时网站提供相同路径

## 数据与生成约定

`entries` 每项用 `label` 唯一标识现有整节；`source` 是相对仓库根目录的源文件；`path` 是唯一主归属叶子；`additional` 只说明跨页关联，不产生第二份正文。`relation` 为 `direct`（直接主题）、`application`（该主题的应用）或 `composite`（横跨多个主题），`note` 说明归类依据和边界。

`page_break_before` 可选布尔值只控制知识节前换页，并在分类标题之前执行，避免标题落在上一页。标题只用于显示，既不用于分类，也不用于定位。读取源文件后以节内的精确标签配对；大、中、小标题与排序从固定导航路径查询。多个知识节可以属于同一叶子；同叶子内按清单顺序保留。跨主题的整节不拆散、不重复，并保留其公式、列表、例子、代码、标签与交叉引用。

总册和数学分册使用同一份分类数据，把知识节并入对应叶子。生成历史附录时仅跳过这六份源文件的原有输入，避免重复；原始 `mathematics.tex` 与六份知识源文件继续保留。知识不是算法目录条目，不能加入算法覆盖或评测统计。

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

## 本地检查

运行 `python3 tests/knowledge_taxonomy.py`。该检查独立解析固定导航源文件，验证快照哈希与生成导航一致、17 个知识标签恰好各映射一次、源路径和叶子路径有效、主归属均为数学的大中小三级，以及范围声明仍明确保留历史知识未分类的限制。负例检查覆盖重复、遗漏、错误源文件、未知叶子和擅自扩大范围；改标题而不改标签不会改变分类。

这是分类数据检查，不是算法正确性、完整回归、线上 AC 或 PDF 视觉验收。数学例子与接口的原有验证仍见各知识源文件和 `tests/math_knowledge_*.py`。
