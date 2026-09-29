#include <bits/stdc++.h>
#include "../src/compact/gauss_xor.hpp"
using namespace std;

mt19937 rng(20260929);
long long systems = 0;

string image(const vector<string> &a, const string &x)
{
    string b(a.size(), '0');
    for (int i = 0; i < (int)a.size(); i++)
        for (int j = 0; j < (int)x.size(); j++)
            if (a[i][j] == '1' && x[j] == '1') b[i] ^= 1;
    return b;
}

void small(const vector<string> &a, int n)
{
    auto saved = a;
    auto sol = GaussXor::solve(a, n);
    assert(a == saved);
    string rhs;
    for (auto &r : a) rhs += r[n];
    set<string> images, solutions;
    for (int mask = 0; mask < (1 << n); mask++)
    {
        string x(n, '0');
        for (int j = 0; j < n; j++) x[j] += mask >> j & 1;
        auto y = image(a, x);
        images.insert(y);
        if (y == rhs) solutions.insert(x);
    }
    assert(images.size() == (1ULL << sol.rank));
    assert(sol.consistent == !solutions.empty());
    if (!sol.consistent)
    {
        assert(sol.particular.empty() && sol.kernel.empty());
        systems++;
        return;
    }
    assert((int)sol.kernel.size() == n - sol.rank);
    assert(solutions.count(sol.particular));
    set<string> generated;
    for (int mask = 0; mask < (1 << sol.kernel.size()); mask++)
    {
        string x = sol.particular;
        for (int j = 0; j < (int)sol.kernel.size(); j++)
            if (mask >> j & 1)
                for (int k = 0; k < n; k++) x[k] ^= sol.kernel[j][k] - '0';
        assert(generated.insert(x).second);
    }
    assert(generated == solutions);
    systems++;
}

int main()
{
    for (int m = 0; m <= 3; m++)
        for (int n = 0; n <= 3; n++)
            for (int mask = 0; mask < (1 << (m * (n + 1))); mask++)
            {
                vector<string> a(m, string(n + 1, '0'));
                for (int i = 0; i < m; i++)
                    for (int j = 0; j <= n; j++)
                        a[i][j] += mask >> (i * (n + 1) + j) & 1;
                small(a, n);
            }
    for (int t = 0; t < 600; t++)
    {
        int n = rng() % 11, m = rng() % 13;
        vector<string> a(m, string(n + 1, '0'));
        for (auto &r : a)
            for (char &c : r) c += rng() % 2;
        small(a, n);
    }
    // Independent rank from a planted identity block; row additions preserve it.
    for (int n : {63, 64, 65, 127, 128, 129, 257})
        for (int r : {0, 1, n / 2, n})
        {
            int m = n + 10;
            vector<string> a(m, string(n + 1, '0'));
            string x(n, '0');
            for (char &c : x) c += rng() % 2;
            for (int i = 0; i < r; i++)
            {
                a[i][i] = '1';
                for (int j = r; j < n; j++) a[i][j] += rng() % 2;
            }
            for (int t = 0; t < 8 * n; t++)
            {
                int u = rng() % m, v = rng() % m;
                if (u != v)
                    for (int j = 0; j < n; j++) a[u][j] ^= a[v][j] - '0';
            }
            auto b = image(a, x);
            for (int i = 0; i < m; i++) a[i][n] = b[i];
            auto sol = GaussXor::solve(a, n);
            assert(sol.consistent && sol.rank == r && (int)sol.kernel.size() == n - r);
            assert(image(a, sol.particular) == b);
            for (auto &v : sol.kernel) assert(image(a, v) == string(m, '0'));
            a.push_back(string(n, '0') + '1');
            sol = GaussXor::solve(a, n);
            assert(!sol.consistent && sol.rank == r);
        }
    int n = 4096;
    vector<string> a(n, string(n + 1, '0'));
    for (int i = 0; i < n; i++)
    {
        a[i][n - 1 - i] = '1';
        a[i][n] += i % 2;
    }
    auto sol = GaussXor::solve(a, n);
    assert(sol.consistent && sol.rank == n && sol.kernel.empty());
    for (int i = 0; i < n; i++) assert(sol.particular[n - 1 - i] == '0' + i % 2);
    for (auto &r : a) fill(r.begin(), r.end(), '0');
    sol = GaussXor::solve(a, n);
    assert(sol.consistent && sol.rank == 0 && sol.particular == string(n, '0'));
    assert((int)sol.kernel.size() == n);
    for (int i = 0; i < n; i++)
    {
        assert(sol.kernel[i][i] == '1');
        assert(count(sol.kernel[i].begin(), sol.kernel[i].end(), '1') == 1);
    }
    a.back().back() = '1';
    sol = GaussXor::solve(a, n);
    assert(!sol.consistent && sol.rank == 0);
    cout << "GaussXor PASS: " << systems
         << " enumerated-image/solution systems; 56 planted-rank word-boundary "
            "systems; 4096 reverse identity/zero/inconsistent matrices\n";
}
