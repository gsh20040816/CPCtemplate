#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>
using namespace std;

struct AssignmentSpectrum
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 120;
    int n, m;
    vector<vector<I>> w;
    vector<I> lx, ly, best;
    vector<int> l, r;
    I level = 0;

    AssignmentSpectrum(int n, int m)
        : n(n), m(m), w(n, vector<I>(m, -inf))
    {
    }

    void add(int x, int y, long long value)
    {
        assert(0 <= x && x < n && 0 <= y && y < m);
        w[x][y] = max(w[x][y], I(value));
    }

    int solve(int limit = INT_MAX)
    {
        assert(limit >= 0);
        level = 0;
        for (const auto &row : w)
            for (I value : row)
                level = max(level, value);
        lx.assign(n, level);
        ly.assign(m, 0);
        l.assign(n, -1);
        r.assign(m, -1);
        best.assign(1, 0);
        int bound = min({n, m, limit});
        for (int k = 0; k < bound; k++)
        {
            vector<bool> sx(n), sy(m);
            vector<I> slack(m, inf);
            vector<int> from(m, -1);
            auto relax = [&](int x)
            {
                sx[x] = true;
                for (int y = 0; y < m; y++)
                {
                    if (sy[y] || w[x][y] == -inf)
                        continue;
                    I value = lx[x] + ly[y] - w[x][y];
                    if (value < slack[y])
                    {
                        slack[y] = value;
                        from[y] = x;
                    }
                }
            };
            for (int x = 0; x < n; x++)
                if (l[x] == -1)
                    relax(x);
            int y;
            while (true)
            {
                y = -1;
                for (int j = 0; j < m; j++)
                    if (!sy[j] && (y == -1 || slack[j] < slack[y]))
                        y = j;
                if (y == -1 || slack[y] == inf)
                    return k;
                I delta = slack[y];
                level -= delta;
                for (int x = 0; x < n; x++)
                    if (sx[x])
                        lx[x] -= delta;
                for (int j = 0; j < m; j++)
                {
                    if (sy[j])
                        ly[j] += delta;
                    else if (slack[j] != inf)
                        slack[j] -= delta;
                }
                sy[y] = true;
                if (r[y] == -1)
                    break;
                relax(r[y]);
            }
            I answer = best.back();
            while (y != -1)
            {
                int x = from[y];
                int old = l[x];
                answer += w[x][y];
                if (old != -1)
                    answer -= w[x][old];
                l[x] = y;
                r[y] = x;
                y = old;
            }
            best.push_back(answer);
        }
        return bound;
    }
};
