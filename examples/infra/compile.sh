#!/usr/bin/env bash
set -euo pipefail
file=
out=
run=1
flags=(-Wall -Wextra -Wno-sign-compare -std=c++23)
mode=(-O1 -g -fsanitize=address,undefined -fno-sanitize-recover=all)
while (($#)); do
    case "$1" in
        -O2)
            mode=(-O2)
            ;;
        -o)
            [[ $# -ge 2 && $2 != -* ]] || exit 2
            out=$2
            run=0
            shift
            ;;
        -*)
            echo "unknown option: $1" >&2
            exit 2
            ;;
        *)
            [[ -z $file ]] || exit 2
            file=$1
            ;;
    esac
    shift
done
[[ -n $file ]] || exit 2
file="${file%.cpp}.cpp"
[[ -f $file ]] || exit 2
out=${out:-${file%.cpp}}
[[ $out == /* ]] || out="./$out"
[[ ! -L $out && ! $file -ef $out ]] || exit 2
[[ ! -e $out || ( -f $out && -x $out ) ]] || exit 2
g++ "$file" -o "$out" "${flags[@]}" "${mode[@]}"
echo "compiled: $out" >&2
if ((run)); then
    "$out"
fi
