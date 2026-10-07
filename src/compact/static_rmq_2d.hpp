#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <climits>
#include <functional>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

template <class T = long long, class Cmp = less<T>>
struct StaticRMQ2D
{
    int n, m;
    vector<vector<T>> a;
    vector<vector<vector<int>>> st;
    Cmp cmp;

    StaticRMQ2D(const vector<vector<T>> &v, Cmp cmp = Cmp()) : a(v), cmp(cmp)
    {
        assert(v.size() <= INT_MAX / 2);
        n = v.size();
        assert(n == 0 || v[0].size() <= INT_MAX / 2);
        m = n ? v[0].size() : 0;
        for (const auto &row : v) assert(row.size() == (size_t)m);
        assert(1LL * n * m <= INT_MAX / 2);
        if (!n || !m) return;
        int h = bit_width((unsigned)n), w = bit_width((unsigned)m);
        st.assign(h, vector<vector<int>>(w, vector<int>(n * m)));
        iota(st[0][0].begin(), st[0][0].end(), 0);
        for (int k = 0; k < h; k++)
        {
            for (int l = 0; l < w; l++)
            {
                if (k == 0 && l == 0) continue;
                for (int x = 0; x + (1 << k) <= n; x++)
                {
                    for (int y = 0; y + (1 << l) <= m; y++)
                    {
                        int id = x * m + y;
                        if (k)
                        {
                            st[k][l][id] = better(st[k - 1][l][id],
                                st[k - 1][l][id + (1 << (k - 1)) * m]);
                        }
                        else
                        {
                            st[k][l][id] = better(st[k][l - 1][id],
                                st[k][l - 1][id + (1 << (l - 1))]);
                        }
                    }
                }
            }
        }
    }

    int better(int x, int y) const
    {
        const auto &u = a[x / m][x % m], &v = a[y / m][y % m];
        if (cmp(u, v)) return x;
        if (cmp(v, u)) return y;
        return min(x, y);
    }

    pair<int, int> query(int x1, int y1, int x2, int y2) const
    {
        assert(0 <= x1 && x1 < x2 && x2 <= n);
        assert(0 <= y1 && y1 < y2 && y2 <= m);
        int k = bit_width((unsigned)(x2 - x1)) - 1;
        int l = bit_width((unsigned)(y2 - y1)) - 1;
        x2 -= 1 << k;
        y2 -= 1 << l;
        const auto &t = st[k][l];
        int top = better(t[x1 * m + y1], t[x1 * m + y2]);
        int bottom = better(t[x2 * m + y1], t[x2 * m + y2]);
        int id = better(top, bottom);
        return {id / m, id % m};
    }
};
