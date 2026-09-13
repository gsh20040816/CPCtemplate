#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/oi_taxonomy.py
python3 tools/book.py
python3 tools/volumes.py
mkdir -p build/pdf output/pdf
cd docs
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/pdf main.tex
cp ../build/pdf/main.pdf ../output/pdf/xcpc-template.pdf

for volume in strings mathematics data-structures graphs geometry misc; do
    latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/pdf "volume-$volume.tex"
    cp "../build/pdf/volume-$volume.pdf" "../output/pdf/xcpc-$volume.pdf"
done

cd ..
python3 tools/infra.py
cd docs
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/pdf infra.tex
cp ../build/pdf/infra.pdf ../output/pdf/infra.pdf
cd ..
python3 tools/pdf_audit.py
if [[ -x build/tools-env/bin/python ]]; then
    build/tools-env/bin/python tools/infra_audit.py
else
    python3 tools/infra_audit.py
fi
