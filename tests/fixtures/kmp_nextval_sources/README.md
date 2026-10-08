# kuangbin KMP source fixture

Complete first47 numbered lines of §1.1, printed5–6 / physical7–8. Locked PDF SHA256 f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad. Both pages visually inspected. Original attribution remains kuangbin, fixture not relicensed as new code.

Only mathematical minus normalization, joining wrapped line15, and removing print line numbers/indentation. Standard headers and namespace supplied by harness; source algorithms unchanged. preKMP tables and KMP_Count counts checked independently. The original count function uses ordinary kmp_pre, not its commented optimized alternative.

Tests pass zero-terminated storage and nonzero byte patterns, lengths1..10009 for next[10010]. Arbitrary zero bytes and longer patterns belong only to the new adapter. Subsequent POJ3167 source is outside this47-line fixture and was addressed by the earlier sequence-matching batch.
