# kuangbin HDU4656 source fixture

Complete119 numbered lines, printed52–54 / physical54–56; related problem prose and derivation on printed51–52 were also visually checked. Locked PDF SHA256 f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad. Original attribution remains kuangbin; not relicensed as new project code.

Only mathematical minus normalization and print-line/indent removal. The unmodified fixture is included in a namespace with standard headers. Original line30 has signed64 multiplication overflow, reproduced with n=1,b=c=1,d=0,a0=100 under UBSan.

The runner generates a separate119-line copy replacing only line30 with exact int128 modular multiplication for full-program numerical comparisons; the repair and its hash are recorded. Source comparisons use residues0..1000002,nonzero c,n<=100010. Original c=0 mismatch is retained as a diagnostic. New signed-int and c=0 support are separately tested extensions; no official HDU resource/acceptance claim.
