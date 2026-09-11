#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
if [[ -z "${CXX:-}" ]]; then
    if command -v g++-16 >/dev/null 2>&1; then CXX=g++-16; else CXX=g++; fi
fi
flags=(-std=c++20 -O2 -Wall -Wextra)
if [[ -d /opt/homebrew/include/boost ]]; then flags+=(-I/opt/homebrew/include); fi
if [[ "${SANITIZE:-0}" == 1 ]]; then flags+=(-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer); fi
"$CXX" "${flags[@]}" tests/property.cpp -o build/property
build/property

"$CXX" "${flags[@]}" tests/classic.cpp -o build/classic
build/classic

"$CXX" "${flags[@]}" tests/algebra.cpp -o build/algebra
build/algebra
"$CXX" "${flags[@]}" tests/optimization.cpp -o build/optimization
build/optimization
"$CXX" "${flags[@]}" tests/graph_advanced.cpp -o build/graph_advanced
build/graph_advanced
"$CXX" "${flags[@]}" tests/geometry_extra.cpp -o build/geometry_extra
build/geometry_extra
"$CXX" "${flags[@]}" tests/dual.cpp -o build/dual
build/dual
"$CXX" "${flags[@]}" tests/lowlink.cpp -o build/lowlink
build/lowlink
"$CXX" "${flags[@]}" tests/boundaries.cpp -o build/boundaries
build/boundaries
"$CXX" "${flags[@]}" tests/trees.cpp -o build/trees
build/trees

"$CXX" "${flags[@]}" tests/gcd_sequence.cpp -o build/gcd_sequence
build/gcd_sequence

"$CXX" "${flags[@]}" tests/blossom.cpp -o build/blossom
build/blossom

"$CXX" "${flags[@]}" tests/recurrence.cpp -o build/recurrence
build/recurrence

"$CXX" "${flags[@]}" tests/tarjan.cpp -o build/tarjan
build/tarjan

"$CXX" "${flags[@]}" -pthread tests/biconnected.cpp -o build/biconnected
build/biconnected

"$CXX" "${flags[@]}" tests/palindromic_tree.cpp -o build/palindromic_tree
build/palindromic_tree

"$CXX" "${flags[@]}" -pthread tests/centroid.cpp -o build/centroid
build/centroid

"$CXX" "${flags[@]}" -pthread tests/dsu_on_tree.cpp -o build/dsu_on_tree
build/dsu_on_tree
