#!/usr/bin/env bash
set -euo pipefail
count=${1:-1000}
[[ $count =~ ^[1-9][0-9]*$ ]] || exit 2
dir=$(mktemp -d ./stress.XXXXXX)
echo "saved in $dir" >&2
trap 'echo "stopped at seed $seed; files: $dir" >&2' ERR
for ((seed=1; seed<=count; seed++)); do
    echo "$seed" > "$dir/seed"
    for name in input expected actual diff gen.err brute.err main.err; do
        : > "$dir/$name"
    done
    timeout -k 1s 2s ./gen "$seed" > "$dir/input" 2> "$dir/gen.err"
    timeout -k 1s 2s ./brute < "$dir/input" > "$dir/expected" 2> "$dir/brute.err"
    timeout -k 1s 2s ./main < "$dir/input" > "$dir/actual" 2> "$dir/main.err"
    diff -u "$dir/expected" "$dir/actual" > "$dir/diff"
done
echo "passed $count seeds; last case: $dir"
