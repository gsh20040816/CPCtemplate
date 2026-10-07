# Source fixture attribution

`kuangbin.inc` is the complete 63-line kuangbin 2018 section 1.7 program,
printed pages 23–24 (PDF physical pages 25–26), retained for source auditing.
Source: https://kuangbin.github.io/2018/08/01/ACM-template/
The original author's rights are retained; this fixture is not relicensed as
new MIT implementation. Only PDF line numbers/headers/layout whitespace,
Unicode minus signs and the wrapped line 54 were normalized.

The fixture intentionally retains the original negative-column access. The
runner compiles it unchanged to reproduce UBSan's diagnostic, and separately
records the single loop-bound patch used for algorithm comparisons. See
`docs/INTERVAL-SUBSTRING-SOURCE-AUDIT.md` for the limits of this evidence.
