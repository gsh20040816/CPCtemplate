# kuangbin DA complete source fixture

Full121 numbered lines from §1.5.1, printed11–14 / physical13–16, visually checked. Locked PDF SHA256 f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad. Original attribution remains kuangbin; this fixture is not relicensed as new project code.

Mathematical minus glyphs normalized, print line numbers removed, wrapped lines8/9/10/33/97 joined; source indentation is not significant. No algorithm changes. The test supplies standard headers, includes the complete fragment in a namespace (avoiding std::rank ambiguity), and calls its original main.

Original-domain tests use printableASCII33..126 and token lengths1..10004, satisfying its m=128 and MAXN=20010 combined-sequence storage. Full EOF input and exact substring output are checked, not just the suffix-array helper. New byte-extension and500001-length cases never run against this source.
