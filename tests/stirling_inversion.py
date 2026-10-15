#!/usr/bin/env python3
"""Run the printed power-sum listing of the Stirling inversion section and check both inversion pairs."""
import os
import re
import subprocess
from pathlib import Path
from compiler_config import CXX

root = Path(__file__).resolve().parents[1]
tex = (root / 'docs/knowledge-stirling.tex').read_text()
listings = re.findall(r'\\begin\{lstlisting\}\n(.*?)\\end\{lstlisting\}', tex, re.S)
assert len(listings) == 1
program = '#include "' + str(root / 'src/compact/stirling.hpp') + '"\n#include <iostream>\n' + listings[0] + r'''
int main()
{
    const long long P = 998244353;
    // Exact small tables by recurrence, as integers.
    const int N = 40;
    vector<vector<long long>> c(N + 1, vector<long long>(N + 1)), S = c;
    c[0][0] = S[0][0] = 1;
    for (int n = 1; n <= N; n++)
        for (int k = 1; k <= n; k++)
        {
            c[n][k] = (c[n - 1][k - 1] + (n - 1) * c[n - 1][k]) % P;
            S[n][k] = (S[n - 1][k - 1] + k * S[n - 1][k]) % P;
        }
    auto sgn = [](int x) { return x % 2 ? P - 1 : 1; };
    unsigned seed = 7;
    auto rnd = [&]() { return seed = seed * 1103515245u + 12345u; };
    for (int test = 0; test < 200; test++)
    {
        vector<long long> a(N + 1), b(N + 1), back(N + 1);
        for (auto &x : a) x = rnd() % P;
        // Pair 1: b = S a, a = s b.
        for (int n = 0; n <= N; n++)
            for (int k = 0; k <= n; k++) b[n] = (b[n] + S[n][k] * a[k]) % P;
        for (int n = 0; n <= N; n++)
            for (int k = 0; k <= n; k++)
                back[n] = (back[n] + sgn(n - k) * c[n][k] % P * b[k]) % P;
        if (back != a) return 1;
        // Pair 2: b = c a, a = (-1)^(n-k) S b.
        fill(b.begin(), b.end(), 0);
        fill(back.begin(), back.end(), 0);
        for (int n = 0; n <= N; n++)
            for (int k = 0; k <= n; k++) b[n] = (b[n] + c[n][k] * a[k]) % P;
        for (int n = 0; n <= N; n++)
            for (int k = 0; k <= n; k++)
                back[n] = (back[n] + sgn(n - k) * S[n][k] % P * b[k]) % P;
        if (back != a) return 2;
    }
    // Rows from the templates agree with the tables used in the inversion.
    for (int n = 0; n <= N; n++)
    {
        auto first = stirling_first_row(n);
        auto second = stirling_second_row(n, n);
        for (int k = 0; k <= n; k++)
            if (first[k].v != c[n][k] || second[k].v != S[n][k]) return 3;
    }
    // Printed power sum versus direct summation, including n < k and n = 0.
    for (int k = 0; k <= 12; k++)
        for (unsigned long long n = 0; n <= 60; n++)
        {
            Z want = 0;
            for (unsigned long long i = 0; i <= n; i++) want += Z(i).pow(k);
            if (power_sum(n, k).v != want.v) return 4;
        }
    // Large n: compare with Faulhaber via the known closed form for k = 1, 2, 3.
    unsigned long long n = 1000000000000000000ULL;
    Z m = Z(n % P);
    if (power_sum(n, 1).v != (m * (m + 1) / 2).v) return 5;
    if (power_sum(n, 2).v != (m * (m + 1) * (m + m + 1) / 6).v) return 6;
    if (power_sum(n, 3).v != (m * (m + 1) / 2).pow(2).v) return 7;
    cout << "Stirling inversion pairs, printed power_sum listing and 1e18 closed forms PASS\n";
}
'''
out = root / 'build/stirling-inversion'
out.mkdir(parents=True, exist_ok=True)
source = out / 'program.cpp'
source.write_text(program)
flags = ['-std=c++20', '-O2']
if os.environ.get('CPC_SANITIZE') == '1':
    flags = ['-std=c++20', '-O1', '-g', '-fsanitize=address,undefined']
exe = out / 'program'
subprocess.run([CXX, *flags, '-I', str(root / 'tests'), str(source), '-o', str(exe)], check=True)
run = subprocess.run([str(exe)], capture_output=True, text=True)
assert run.returncode == 0 and not run.stderr, (run.returncode, run.stderr)
print(run.stdout.strip(), flush=True)
