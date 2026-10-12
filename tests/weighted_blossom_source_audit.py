"""Audit locked kuangbin 4.14 against subset DP and the replacement.

Requires build/source-audit/kuangbin.{pdf,txt}; txt is pdftotext -layout.
Original code stays in ignored build/, not redistributed as library code.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from compiler_config import CXX

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/weighted-blossom-source'
OUT.mkdir(parents=True, exist_ok=True)
pdf = ROOT / 'build/source-audit/kuangbin.pdf'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pdf) == 'f1c90eae0c3fb309d58a14b050fe12b239efb474b033299a547b55646c2768ad'
text = (pdf.with_suffix('.txt')).read_text()
start = text.index('//一般图的最大加权匹配模板')
start = text.rfind('\n', 0, start)
end = text.index('4.15', start)
lines = []
for line in text[start:end].splitlines():
    m = re.match(r'\s*(\d+)\s+(.*)', line)
    if m:
        assert int(m[1]) == len(lines) + 1
        lines.append(m[2].replace('−', '-'))
assert len(lines) == 70
original = OUT / 'original.inc'
original.write_text('\n'.join(lines) + '\n')
source = r'''
#include <bits/stdc++.h>
using namespace std;
namespace upstream {
#include "original.inc"
}
#include "../../src/compact/weighted_blossom.hpp"
int main(int argc, char **argv)
{
    if (argc > 1)
    {
        for (int i = 0; i < 4; i++)
            for (int j = 0; j < 4; j++)
                upstream::G[i][j] = i == j ? 0 : INT_MAX;
        cout << upstream::get_Match(4) << '\n';
        return 0;
    }
    mt19937 rng(20261012);
    int checks = 0;
    for (int n = 2; n <= 12; n += 2)
    {
        for (int trial = 0; trial < 1000; trial++)
        {
            WeightedBlossom graph(n);
            vector<vector<int>> w(n, vector<int>(n));
            for (int i = 0; i < n; i++)
            {
                for (int j = i + 1; j < n; j++)
                {
                    int value = int(rng() % 201) - 100;
                    if (trial % 5 == 0) value = int(rng() % 3) - 1;
                    if (trial % 5 == 1) value = -int(rng() % 101);
                    w[i][j] = w[j][i] = value;
                    upstream::G[i][j] = upstream::G[j][i] = value;
                    graph.add_edge(i + 1, j + 1, value);
                }
            }
            vector<int> dp(1 << n, -1000000000);
            dp[0] = 0;
            for (int mask = 1; mask < (1 << n); mask++)
            {
                int u = __builtin_ctz(unsigned(mask));
                for (int v = u + 1; v < n; v++)
                    if (mask >> v & 1)
                        dp[mask] = max(dp[mask], dp[mask ^ (1 << u) ^ (1 << v)] + w[u][v]);
            }
            srand(trial);
            int got = upstream::get_Match(n);
            auto now = graph.solve(true);
            if (got != dp.back() || now.weight != dp.back() || now.pairs != n / 2)
            {
                cerr << "Mismatch " << n << ' ' << trial << ' ' << got << ' ' << dp.back() << '\n';
                for (auto row : w)
                {
                    for (int x : row) cerr << x << ' ';
                    cerr << '\n';
                }
                return 1;
            }
            int sum = 0;
            for (int u = 0; u < n; u++)
            {
                int v = upstream::match[u];
                if (v < 0 || v >= n || v == u || upstream::match[v] != u) return 2;
                if (u < v) sum += w[u][v];
            }
            if (sum != got) return 3;
            checks++;
        }
    }
    // Zero-initialized absent edges are still treated as valid pairs upstream.
    memset(upstream::G, 0, sizeof(upstream::G));
    upstream::get_Match(4);
    if (upstream::match[0] != 1 || upstream::match[1] != 0
        || upstream::match[2] != 3 || upstream::match[3] != 2) return 5;
    WeightedBlossom empty(4);
    if (empty.solve(true).pairs != 0) return 4;
    cout << "PASS " << checks << " complete-even graphs; empty graph boundary reproduced\n";
}
'''
cpp = OUT / 'audit.cpp'
cpp.write_text(source)
report = {'source_pdf_sha256': sha(pdf), 'source_physical_pages': [159, 160],
          'original_lines': 70, 'original_sha256': sha(original),
          'harness_sha256': sha(cpp), 'runs': [],
          'scope': 'Local comparison, not a proof of upstream correctness or worst-case complexity.'}
for mode in ['normal', 'sanitizer']:
    exe = OUT / mode
    flags = ['-O2'] if mode == 'normal' else ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
    command = [CXX, '-std=gnu++14', *flags, str(cpp), '-o', str(exe)]
    subprocess.run(command, check=True, capture_output=True)
    run = subprocess.run([str(exe)], text=True, capture_output=True, timeout=180)
    print(mode, run.stdout, run.stderr, flush=True)
    assert run.returncode == 0, run.stderr
    report['runs'].append({'mode': mode, 'command': command, 'output': run.stdout.strip(), 'binary_sha256': sha(exe)})
    if mode == 'sanitizer':
        overflow = subprocess.run([str(exe), 'overflow'], text=True, capture_output=True, timeout=10)
        assert overflow.returncode != 0 and 'signed integer overflow' in overflow.stderr
        report['upstream_overflow'] = {'input': 'K4, every edge INT_MAX', 'expected_weight': 4294967294, 'diagnostic': overflow.stderr.strip()}
(ROOT / 'verification/weighted-blossom-source-audit.json').write_text(json.dumps(report, indent=2) + '\n')
