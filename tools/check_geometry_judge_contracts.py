#!/usr/bin/env python3
"""Probe default floating intersection contracts against two legal AOJ cases.

Exit 1 means a measured judge-contract incompatibility, NOT an API-contract
violation. This diagnostic is deliberately not a passing algorithm unit test.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, getcontext
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADERS = ['src/compact/line_circle_intersections.hpp', 'src/compact/circle_intersections.hpp']
SOURCE = '''#include <bits/stdc++.h>
#include "src/compact/line_circle_intersections.hpp"
#include "src/compact/circle_intersections.hpp"
int main() {
    std::cout << std::setprecision(30);
    std::cout << "precision " << std::numeric_limits<long double>::digits << '\\n';
    auto print = [](const char *name, auto result) {
        std::cout << name << ' ' << int(result.kind) << ' ' << result.p.size();
        for (auto p : result.p) std::cout << ' ' << p.x << ' ' << p.y;
        std::cout << '\\n';
    };
    print("CGL_7_D", line_circle_intersections({9797,396}, {9574,5913}, {{0,0},9805}));
    print("CGL_7_E", circle_intersections({{0,0},10000}, {{9999,1},1}));
}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources(path, found):
    path = path.resolve()
    if path in found:
        return
    found.add(path)
    for name in re.findall(r'^\s*#include "([^"\n]+)"', path.read_text(), re.M):
        sources(path.parent / name, found)


def references():
    getcontext().prec = 70
    vx, vy, r = -223, 5517, 9805
    q = vx*vx + vy*vy
    cross = vx*396 - vy*9797
    assert r*r*q - cross*cross == 1
    line = [(D(9797), D(396)), (D(9797)-2*D(vx)/D(q), D(396)-2*D(vy)/D(q))]
    circle_q = 9999**2 + 1
    k = circle_q + 10000**2 - 1
    disc = 4*10000**2*circle_q-k*k
    assert disc == 39999
    x, y = D(9999)*D(k)/(2*D(circle_q)), D(k)/(2*D(circle_q))
    w = D(disc).sqrt()/(2*D(circle_q))
    circle = [(x-w, y+9999*w), (x+w, y-9999*w)]
    return {'CGL_7_D': (sorted(line), 1), 'CGL_7_E': (sorted(circle), disc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New directory beneath build/')
    args = parser.parse_args()
    (ROOT/'build').mkdir(exist_ok=True)
    work = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='geometry-contract-', dir=ROOT/'build'))
    if args.output:
        assert work.is_relative_to(ROOT/'build')
        work.mkdir(parents=True, exist_ok=False)
    compiler = Path(shutil.which(os.environ.get('CXX', 'g++'))).resolve()
    files = {Path(__file__).resolve()}
    for header in HEADERS:
        sources(ROOT/header, files)
    before = {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)}
    compiler_hash = sha(compiler)
    source, binary = work/'probe.cpp', work/'probe'
    source.write_text(SOURCE)
    command = [str(compiler), '-std=c++20', '-O2', '-I', str(ROOT), str(source), '-o', str(binary)]
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=120)
    (work/'compile.log').write_text(compiled.stdout+compiled.stderr)
    compiled.check_returncode()
    run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
    (work/'stdout.txt').write_text(run.stdout)
    (work/'stderr.txt').write_text(run.stderr)
    run.check_returncode()
    assert not run.stderr
    rows = run.stdout.splitlines()
    assert rows[0].startswith('precision ') and len(rows) == 3
    cases = []
    expected = references()
    for line in rows[1:]:
        tokens = line.split()
        name, kind, count = tokens[0], int(tokens[1]), int(tokens[2])
        assert name in expected and len(tokens) == 3+2*count
        points = [(D(tokens[i]), D(tokens[i+1])) for i in range(3,len(tokens),2)]
        adapted = sorted(points if count != 1 else points*2)
        reference, discriminant = expected[name]
        error = max(abs(x-y) for p,q in zip(adapted,reference) for x,y in zip(p,q)) if len(adapted)==2 else None
        compatible = kind in (1, 2) and error is not None and error < D('0.000001')
        cases.append(dict(problem=name, source='https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id='+name,
                          exact_positive_discriminant=discriminant, expected_intersections=2, actual_kind=kind,
                          actual_point_count=count, actual_points=[[str(x),str(y)] for x,y in points],
                          reference_points=[[str(x),str(y)] for x,y in reference],
                          max_coordinate_error_after_ordering_and_tangent_duplication=str(error) if error is not None else None,
                          compatible_with_judge_tolerance=compatible))
    after = {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)}
    assert before == after and sha(compiler) == compiler_hash
    result = dict(scope='Two legal integer-input counterexamples only; default tolerance-aware API may merge near tangencies. Not an API violation, global geometry validation, sanitizer test or online AC.',
                  checked_at=datetime.now(timezone.utc).isoformat(), long_double_mantissa_bits=int(rows[0].split()[1]),
                  source_sha256=before, source_unchanged=True, compiler=str(compiler), compiler_sha256=compiler_hash,
                  compiler_version=subprocess.check_output([str(compiler),'--version'],text=True), command=command,
                  probe_sha256=sha(source), binary_sha256=sha(binary), stdout_sha256=sha(work/'stdout.txt'), cases=cases)
    (work/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Report:',work/'report.json')
    for case in cases:
        print(case['problem'], 'compatible:',case['compatible_with_judge_tolerance'], 'max error:',case['max_coordinate_error_after_ordering_and_tangent_duplication'])
    return int(not all(case['compatible_with_judge_tolerance'] for case in cases))


if __name__ == '__main__':
    raise SystemExit(main())
