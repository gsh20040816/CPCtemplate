#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN tree_probability
// Symmetric percentages in [0,100], zero diagonal; 1 <= n <= 50.
long double tree_probability(const vector<vector<int>> &p)
{
    int n = p.size();
    assert(1 <= n && n <= 50);
    vector<int> fa(n);
    iota(fa.begin(), fa.end(), 0);
    auto find = [&](auto &&self, int u) -> int
    {
        if (fa[u] == u)
            return u;
        return fa[u] = self(self, fa[u]);
    };
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++)
            if (p[u][v] == 100)
            {
                int a = find(find, u);
                int b = find(find, v);
                if (a == b)
                    return 0;
                fa[a] = b;
            }
    vector<int> id(n, -1);
    int k = 0;
    for (int u = 0; u < n; u++)
    {
        int r = find(find, u);
        if (id[r] == -1)
            id[r] = k++;
        id[u] = id[r];
    }
    vector<vector<long double>> a(k - 1, vector<long double>(k - 1));
    long double ans = 0;
    for (int u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++)
        {
            int w = p[u][v];
            if (w > 0)
                fa[find(find, u)] = find(find, v);
            if (w == 100)
                continue;
            ans += logl((100 - w) / 100.0L);
            int x = id[u];
            int y = id[v];
            if (x == y)
                continue;
            long double t = (long double)w / (100 - w);
            if (x < k - 1)
                a[x][x] += t;
            if (y < k - 1)
                a[y][y] += t;
            if (x < k - 1 && y < k - 1)
            {
                a[x][y] -= t;
                a[y][x] -= t;
            }
        }
    for (int u = 0; u < n; u++)
        if (find(find, u) != find(find, 0))
            return 0;
    for (int i = 0; i < k - 1; i++)
    {
        // The connected graph cofactor is positive definite.
        assert(a[i][i] > 0);
        ans += logl(a[i][i]);
        for (int j = i + 1; j < k - 1; j++)
        {
            long double t = a[j][i] / a[i][i];
            for (int z = i + 1; z < k - 1; z++)
                a[j][z] -= t * a[i][z];
        }
    }
    return expl(ans);
}
// END tree_probability
