#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN grid_cycle
template <class Count>
Count grid_cycle(vector<string> a)
{
    int n = a.size();
    if (n == 0) return Count(0);
    int m = a[0].size();
    for (auto &row : a)
    {
        assert((int)row.size() == m);
        for (char c : row) assert(c == '.' || c == '*');
    }
    if (m == 0) return Count(0);
    if (n < m)
    {
        vector<string> b(m, string(n, '*'));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++) b[j][i] = a[i][j];
        a.swap(b);
        swap(n, m);
    }
    assert(m <= 15);
    pair<int, int> last = {-1, -1};
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            if (a[i][j] == '.') last = {i, j};
    using Key = unsigned long long;
    unordered_map<Key, Count> dp, next;
    dp[0] = Count(1);
    Count answer = 0;
    for (int i = 0; i < n; i++)
    {
        next.clear();
        for (auto &[s, ways] : dp) next[s << 4] += ways;
        dp.swap(next);
        for (int j = 0; j < m; j++)
        {
            next.clear();
            bool down = i + 1 < n && a[i + 1][j] == '.';
            bool right = j + 1 < m && a[i][j + 1] == '.';
            for (auto &[s, ways] : dp)
            {
                vector<int> p(m + 1);
                for (int k = 0; k <= m; k++) p[k] = s >> (4 * k) & 15;
                int x = p[j];
                int y = p[j + 1];
                p[j] = 0;
                p[j + 1] = 0;
                auto add = [&]()
                {
                    array<int, 16> id{};
                    int count = 0;
                    Key key = 0;
                    for (int k = 0; k <= m; k++)
                    {
                        int v = p[k];
                        if (v && !id[v]) id[v] = ++count;
                        key |= Key(id[v]) << (4 * k);
                    }
                    next[key] += ways;
                };
                if (a[i][j] == '*')
                {
                    if (!x && !y) add();
                }
                else if (!x && !y)
                {
                    if (down && right)
                    {
                        p[j] = 15;
                        p[j + 1] = 15;
                        add();
                    }
                }
                else if (!x || !y)
                {
                    if (down)
                    {
                        p[j] = x + y;
                        add();
                        p[j] = 0;
                    }
                    if (right)
                    {
                        p[j + 1] = x + y;
                        add();
                    }
                }
                else if (x != y)
                {
                    for (int &v : p)
                        if (v == y) v = x;
                    add();
                }
                else if (make_pair(i, j) == last)
                {
                    if (all_of(p.begin(), p.end(), [](int v)
                    {
                        return v == 0;
                    })) answer += ways;
                }
            }
            dp.swap(next);
        }
    }
    return answer;
}
// END grid_cycle
