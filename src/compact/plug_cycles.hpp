#pragma once
#include <bits/stdc++.h>
#include <cassert>
using namespace std;

// BEGIN grid_cycles
template <class Count>
Count grid_cycles(vector<string> a, int k, bool nested = false)
{
    assert(k >= 0);
    int n = a.size();
    if (n == 0) return Count(k == 0);
    int m = a[0].size();
    long long cells = 0;
    for (auto &row : a)
    {
        assert((int)row.size() == m);
        for (char c : row)
        {
            assert(c == '.' || c == '*');
            cells += c == '.';
        }
    }
    if (cells == 0) return Count(k == 0);
    if (k == 0 || k > cells / 4) return Count(0);
    if (n < m)
    {
        vector<string> b(m, string(n, '*'));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++) b[j][i] = a[i][j];
        a.swap(b);
        swap(n, m);
    }
    assert(m <= 15);
    using Key = unsigned long long;
    vector<unordered_map<Key, Count>> dp(k + 1), next(k + 1);
    dp[0][0] = Count(1);
    for (int i = 0; i < n; i++)
    {
        for (int c = 0; c <= k; c++)
        {
            next[c].clear();
            for (auto &[s, ways] : dp[c]) next[c][s << 4] += ways;
        }
        dp.swap(next);
        for (int j = 0; j < m; j++)
        {
            for (auto &t : next) t.clear();
            bool down = i + 1 < n && a[i + 1][j] == '.';
            bool right = j + 1 < m && a[i][j + 1] == '.';
            for (int c = 0; c <= k; c++)
            {
                for (auto &[s, ways] : dp[c])
                {
                    array<int, 16> p{};
                    for (int t = 0; t <= m; t++) p[t] = s >> (4 * t) & 15;
                    int x = p[j];
                    int y = p[j + 1];
                    p[j] = 0;
                    p[j + 1] = 0;
                    auto add = [&](int count)
                    {
                        array<int, 16> id{};
                        int top = 0;
                        Key key = 0;
                        for (int t = 0; t <= m; t++)
                        {
                            int v = p[t];
                            if (v && !id[v]) id[v] = ++top;
                            key |= Key(id[v]) << (4 * t);
                        }
                        next[count][key] += ways;
                    };
                    if (a[i][j] == '*')
                    {
                        if (!x && !y) add(c);
                    }
                    else if (!x && !y)
                    {
                        if (down && right)
                        {
                            p[j] = 15;
                            p[j + 1] = 15;
                            add(c);
                        }
                    }
                    else if (!x || !y)
                    {
                        if (down)
                        {
                            p[j] = x + y;
                            add(c);
                            p[j] = 0;
                        }
                        if (right)
                        {
                            p[j + 1] = x + y;
                            add(c);
                        }
                    }
                    else if (x != y)
                    {
                        for (int &v : p)
                            if (v == y) v = x;
                        add(c);
                    }
                    else if (c < k)
                    {
                        int parity = 0;
                        for (int t = 0; t < j; t++) parity ^= p[t] != 0;
                        if (nested || parity == 0) add(c + 1);
                    }
                }
            }
            dp.swap(next);
        }
    }
    auto it = dp[k].find(0);
    return it == dp[k].end() ? Count(0) : it->second;
}
// END grid_cycles
