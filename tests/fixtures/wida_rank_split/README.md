# WIDA jiangly 08D merge/split source

Unmodified bytes from hh2048/XCPC tree cfdb12db6792eb2303798541fb5c760ed2bc618b. Path `03 - jiangly模板收集/04 - 数据结构/08D - 其他平衡树.cpp`; blob efe3fa09a520e97e0a861c17767390b3d9899e1c.

Attribution: jiangly, https://ac.nowcoder.com/acm/contest/view-submission?submissionId=63162242 (2023-07-31). Original GPL-3.0 provenance retained. Source functions remain unchanged.

The runtime audit checks count merge and ascending/descending rank split on nonnegative multisets with duplicate values. This count-only domain has cntnew=0. An isolated probe establishes that arbitrary marked duplicate occurrences are not a valid assumed interpretation: at a partially split leaf, cntnew is retained wholly in the first piece. The original full problem and its marker invariant remain unresolved; no original-problem bug is asserted.
