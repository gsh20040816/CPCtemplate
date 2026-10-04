# Reproducing source snapshots after a fresh checkout

The receipt collector includes every ordinary file below `docs/`, except Python bytecode. This workspace has a 128-byte historical TeX `docs/missfont.log` from 2026-09-30. It is not an algorithm input or a font configuration change, but its exact bytes are included in the recorded source snapshots.

The file is ignored by Git as a generated log. Its original bytes are preserved here solely to reproduce those snapshots after recovery. If restoring the recorded workspace, copy `docs-missfont.log` to `docs/missfont.log` before comparing the source map. Do not overwrite a newer local log without checking its provenance. Generate ignored `docs/volume-*.tex` using `python3 tools/book.py` and `python3 tools/volumes.py` as documented in the repository README.

SHA-256 and recovery mapping are recorded in `verification/inside-triangle-checkpoint.json`. This preservation does not turn a failed historical TeX command into a successful build; current PDF builds and font-set checks are recorded separately.
