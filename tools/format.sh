#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
formatter="${CLANG_FORMAT:-clang-format}"
mode=(-i)
if [[ "${1:-}" == --check ]]; then mode=(--dry-run --Werror); fi
for style in compact; do
    "$formatter" "${mode[@]}" --style=file src/"$style"/*.hpp
    for file in verify/luogu/*."$style".cpp; do
        "$formatter" "${mode[@]}" --style="file:src/$style/.clang-format" "$file"
    done
done
