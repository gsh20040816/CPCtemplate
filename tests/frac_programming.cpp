#include "../src/compact/frac_programming.hpp"
#include <cassert>
#include <iostream>
#include <random>

// Dinkelbach and binary search on two classic models versus exhaustive enumeration.
mt19937_64 rng(25);

int main()
{
    long long checks = 0;
    // 1. choose exactly k items, maximize sum a / sum b (b > 0)
    for (int it = 0; it < 3000; it++)
    {
        int n = 1 + rng() % 12, k = 1 + rng() % n;
        vector<double> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = (double)((long long)(rng() % 2001) - 1000), b[i] = 1 + rng() % 1000;
        double brute = -1e18;
        for (int mask = 0; mask < 1 << n; mask++)
            if (__builtin_popcount(mask) == k)
            {
                double A = 0, B = 0;
                for (int i = 0; i < n; i++)
                    if (mask >> i & 1) A += a[i], B += b[i];
                brute = max(brute, A / B);
            }
        auto best = [&](double lambda)
        {
            vector<int> id(n);
            iota(id.begin(), id.end(), 0);
            sort(id.begin(), id.end(), [&](int x, int y) { return a[x] - lambda * b[x] > a[y] - lambda * b[y]; });
            double A = 0, B = 0;
            for (int i = 0; i < k; i++) A += a[id[i]], B += b[id[i]];
            return pair<double, double>{A, B};
        };
        auto [A0, B0] = best(0);
        double got = dinkelbach(best, A0 / B0);
        assert(fabs(got - brute) <= 1e-9 * max(1.0, fabs(brute)));
        // binary search: F(lambda) = max(A - lambda B) >= 0 iff lambda <= optimum
        double lo = -1001, hi = 1001;
        for (int r = 0; r < 100; r++)
        {
            double mid = (lo + hi) / 2;
            auto [A, B] = best(mid);
            (A - mid * B >= 0 ? lo : hi) = mid;
        }
        assert(fabs(lo - brute) <= 1e-7);
        checks += 2;
    }
    // 2. optimal ratio spanning tree: maximize sum a / sum b over spanning trees
    for (int it = 0; it < 600; it++)
    {
        int n = 2 + rng() % 4;
        vector<array<int, 2>> e;
        for (int v = 1; v < n; v++) e.push_back({(int)(rng() % v), v}); // keep connected
        int extra = rng() % 5;
        for (int j = 0; j < extra; j++)
        {
            int u = rng() % n, v = rng() % n;
            if (u != v) e.push_back({u, v});
        }
        int m = e.size();
        vector<double> a(m), b(m);
        for (int j = 0; j < m; j++) a[j] = (double)((long long)(rng() % 201) - 100), b[j] = 1 + rng() % 100;
        auto is_tree = [&](int mask)
        {
            vector<int> p(n);
            iota(p.begin(), p.end(), 0);
            function<int(int)> f = [&](int x) { return p[x] == x ? x : p[x] = f(p[x]); };
            int cnt = 0;
            for (int j = 0; j < m; j++)
                if (mask >> j & 1)
                {
                    int x = f(e[j][0]), y = f(e[j][1]);
                    if (x == y) return false;
                    p[x] = y, cnt++;
                }
            return cnt == n - 1;
        };
        double brute = -1e18;
        for (int mask = 0; mask < 1 << m; mask++)
            if (is_tree(mask))
            {
                double A = 0, B = 0;
                for (int j = 0; j < m; j++)
                    if (mask >> j & 1) A += a[j], B += b[j];
                brute = max(brute, A / B);
            }
        auto best = [&](double lambda) // maximum spanning tree on a - lambda b (Kruskal)
        {
            vector<int> id(m), p(n);
            iota(id.begin(), id.end(), 0), iota(p.begin(), p.end(), 0);
            sort(id.begin(), id.end(), [&](int x, int y) { return a[x] - lambda * b[x] > a[y] - lambda * b[y]; });
            function<int(int)> f = [&](int x) { return p[x] == x ? x : p[x] = f(p[x]); };
            double A = 0, B = 0;
            for (int j : id)
            {
                int x = f(e[j][0]), y = f(e[j][1]);
                if (x != y) p[x] = y, A += a[j], B += b[j];
            }
            return pair<double, double>{A, B};
        };
        auto [A0, B0] = best(0);
        double got = dinkelbach(best, A0 / B0);
        assert(fabs(got - brute) <= 1e-9 * max(1.0, fabs(brute)));
        checks++;
    }
    cout << "Fractional programming: choose-k and ratio spanning trees by Dinkelbach and binary search "
            "vs enumeration PASS (" << checks << " checks)\n";
}
