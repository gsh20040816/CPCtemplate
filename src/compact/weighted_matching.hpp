#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

struct WeightedMatching
{
    using I = __int128_t;
    static constexpr I inf = I(1) << 120;
    int n, m;
    vector<vector<I>> w;
    vector<int> l, r;

    WeightedMatching(int n, int m)
        : n(n), m(m), w(n + 1, vector<I>(m + 1, -inf)), l(n + 1), r(m + 1)
    {
    }

    void add(int x, int y, long long weight)
    {
        assert(1 <= x && x <= n && 1 <= y && y <= m);
        w[x][y] = max(w[x][y], I(weight));
    }

    optional<I> solve(bool allow_unmatched = false)
    {
        fill(l.begin(), l.end(), 0);
        fill(r.begin(), r.end(), 0);
        if (!allow_unmatched && n > m)
            return nullopt;
        int cols = m + (allow_unmatched ? n : 0);
        vector<I> u(n + 1), v(cols + 1);
        vector<int> p(cols + 1), way(cols + 1);
        for (int i = 1; i <= n; i++)
        {
            p[0] = i;
            int j0 = 0;
            vector<I> dis(cols + 1, inf);
            vector<bool> used(cols + 1);
            do
            {
                used[j0] = true;
                int x = p[j0], j1 = 0;
                I delta = inf;
                for (int j = 1; j <= cols; j++)
                {
                    if (used[j])
                        continue;
                    I weight = j <= m ? w[x][j] : 0;
                    if (weight != -inf)
                    {
                        I cur = -weight - u[x] - v[j];
                        if (cur < dis[j])
                        {
                            dis[j] = cur;
                            way[j] = j0;
                        }
                    }
                    if (dis[j] < delta)
                    {
                        delta = dis[j];
                        j1 = j;
                    }
                }
                if (delta == inf)
                    return nullopt;
                for (int j = 0; j <= cols; j++)
                {
                    if (used[j])
                    {
                        u[p[j]] += delta;
                        v[j] -= delta;
                    }
                    else if (dis[j] != inf)
                        dis[j] -= delta;
                }
                j0 = j1;
            } while (p[j0]);
            do
            {
                int j1 = way[j0];
                p[j0] = p[j1];
                j0 = j1;
            } while (j0);
        }
        I answer = 0;
        for (int j = 1; j <= m; j++)
        {
            if (!p[j])
                continue;
            l[p[j]] = j;
            r[j] = p[j];
            answer += w[p[j]][j];
        }
        return answer;
    }
};
