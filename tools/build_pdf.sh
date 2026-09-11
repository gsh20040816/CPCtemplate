#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/book.py
mkdir -p build/pdf output/pdf
cd docs
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=../build/pdf main.tex
cp ../build/pdf/main.pdf ../output/pdf/xcpc-template.pdf
