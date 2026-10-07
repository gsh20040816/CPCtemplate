# kuangbin §2.16 source fixture

Full151 numbered lines, printed47–49 / physical49–51 of the pinned kuangbin PDF. Source attribution remains kuangbin; these historical source fixtures are not newly authored templates and are not relicensed as project code. Used only for source auditing.

PDF SHA256: f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad.

raw.cpp transcribes the151 lines, normalizing the PDF mathematical minus and visible-space glyphs. It intentionally retains the malformed line35 comment swallowing the opening brace and line148 old MSVC output format. The test records compilation rejection.

compat.cpp adds standard headers/namespace, moves that one brace outside the comment, and substitutes %lld for %I64d. No algorithm edits. The full T/Case protocol is compared only on positive int inputs. See docs/FIBONACCI-PERIOD.md for domain limits, prime-power caveat and independent oracles.
