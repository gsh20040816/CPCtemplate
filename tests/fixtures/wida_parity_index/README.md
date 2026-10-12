# WIDA jiangly 08A parity counting source

Unmodified upstream bytes from hh2048/XCPC tree cfdb12db6792eb2303798541fb5c760ed2bc618b, `03 - jiangly模板收集/04 - 数据结构/08A - 其他平衡树.cpp`, blob 9d785e3c04661dc419f41bfda7c4cee50eb58470.

Attribution: jiangly, https://ac.nowcoder.com/acm/contest/view-submission?submissionId=63246177 (2023-08-04). The original GPL-3.0 provenance is retained. Runtime evidence does not establish the full original contest protocol, which currently requires login to read.

The fixture's position domain is [0,n), k is nonnegative, and tested version differences have nonnegative counts at every position. query1 returns max(0, largest occupied odd position, position of descending zero-based rank k among all elements). query2 returns the position, multiplicity and remaining zero-based rank among odd-position elements; when the rank is beyond all such elements, it returns {0,0,k-total_odd}. Position parity is the original integer parity, not the parity of a compressed rank.
