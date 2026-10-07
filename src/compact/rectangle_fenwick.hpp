#pragma once
#include <array>
#include <cassert>
#include <vector>
using namespace std;

// BEGIN RectangleFenwick
template <class T = long long> struct RectangleFenwick
{
    int n, m;
    vector<vector<array<T, 4>>> bit;

    RectangleFenwick(int n, int m) : n(n), m(m)
    {
        assert(0 <= n && n < (1 << 30) && 0 <= m && m < (1 << 30));
        bit.assign(n + 1, vector<array<T, 4>>(m + 1));
    }

    // Difference impulse at (x,y); boundary impulses do not affect the grid.
    void corner(int x, int y, T v)
    {
        if (x == n || y == m) return;
        array<T, 4> a{v, v * x, v * y, v * x * y};
        for (int i = x + 1; i <= n; i += i & -i)
            for (int j = y + 1; j <= m; j += j & -j)
                for (int k = 0; k < 4; k++) bit[i][j][k] += a[k];
    }

    // Add to [l,r) x [d,u), 0-based. Empty rectangles are allowed.
    void add(int l, int d, int r, int u, T v)
    {
        assert(0 <= l && l <= r && r <= n && 0 <= d && d <= u && u <= m);
        if (l == r || d == u) return;
        corner(l, d, v);
        corner(r, d, -v);
        corner(l, u, -v);
        corner(r, u, v);
    }

    T prefix(int x, int y) const
    {
        assert(0 <= x && x <= n && 0 <= y && y <= m);
        array<T, 4> a{};
        for (int i = x; i; i -= i & -i)
            for (int j = y; j; j -= j & -j)
                for (int k = 0; k < 4; k++) a[k] += bit[i][j][k];
        return a[0] * x * y - a[1] * y - a[2] * x + a[3];
    }

    T sum(int l, int d, int r, int u) const
    {
        assert(0 <= l && l <= r && r <= n && 0 <= d && d <= u && u <= m);
        if (l == r || d == u) return T{};
        return prefix(r, u) - prefix(l, u) - prefix(r, d) + prefix(l, d);
    }
};
// END RectangleFenwick
