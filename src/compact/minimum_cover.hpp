#pragma once
#include <algorithm>
#include <cassert>
#include <climits>
#include <cstddef>
#include <optional>
#include <vector>
using namespace std;

// BEGIN MinimumCover
struct MinimumCover
{
    struct Node
    {
        int l, r, u, d, c, row;
    };
    int m, best = 0;
    vector<Node> a;
    vector<int> s, path, ans;
    vector<unsigned char> mark;

    MinimumCover(int columns, const vector<vector<int>> &rows) : m(columns)
    {
        assert(0 <= m && m < INT_MAX && rows.size() < INT_MAX);
        size_t z = size_t(m) + 1;
        for (const auto &r : rows)
        {
            assert(r.size() <= size_t(INT_MAX) - z);
            z += r.size();
        }
        a.reserve(z);
        s.assign(m + 1, 0);
        mark.resize(m + 1);
        path.reserve(m);
        ans.reserve(m);
        for (int c = 0; c <= m; c++)
            a.push_back({c ? c - 1 : m, c == m ? 0 : c + 1, c, c, c, -1});
        vector<int> seen(m, -1);
        for (int i = 0; i < int(rows.size()); i++)
        {
            int h = -1;
            for (int col : rows[i])
            {
                assert(0 <= col && col < m && seen[col] != i);
                seen[col] = i;
                int c = col + 1, x = a.size(), u = a[c].u;
                a.push_back({x, x, u, c, c, i});
                a[u].d = x;
                a[c].u = x;
                s[c]++;
                if (h == -1) h = x;
                else
                {
                    int l = a[h].l;
                    a[x].l = l;
                    a[x].r = h;
                    a[l].r = x;
                    a[h].l = x;
                }
            }
        }
    }

    // x is a selected row node, not a column header.
    void remove(int x)
    {
        for (int i = a[x].d; i != x; i = a[i].d)
        {
            a[a[i].l].r = a[i].r;
            a[a[i].r].l = a[i].l;
        }
    }

    void restore(int x)
    {
        for (int i = a[x].u; i != x; i = a[i].u)
        {
            a[a[i].l].r = i;
            a[a[i].r].l = i;
        }
    }

    int lower_bound()
    {
        fill(mark.begin(), mark.end(), 0);
        for (int c = a[0].r; c; c = a[c].r) mark[c] = 1;
        int bound = 0;
        for (int c = a[0].r; c; c = a[c].r)
        {
            if (!mark[c]) continue;
            bound++;
            mark[c] = 0;
            for (int i = a[c].d; i != c; i = a[i].d)
                for (int j = a[i].r; j != i; j = a[j].r)
                    mark[a[j].c] = 0;
        }
        return bound;
    }

    void dfs()
    {
        int depth = path.size(), c = a[0].r;
        if (!c)
        {
            if (depth < best)
            {
                best = depth;
                ans = path;
            }
            return;
        }
        if (lower_bound() >= best - depth) return;
        for (int j = a[c].r; j; j = a[j].r)
            if (s[j] < s[c]) c = j;
        for (int i = a[c].d; i != c; i = a[i].d)
        {
            path.push_back(a[i].row);
            remove(i);
            for (int j = a[i].r; j != i; j = a[j].r) remove(j);
            dfs();
            for (int j = a[i].l; j != i; j = a[j].l) restore(j);
            restore(i);
            path.pop_back();
        }
    }

    optional<vector<int>> solve()
    {
        path.clear();
        ans.clear();
        best = m + 1;
        dfs();
        if (best > m) return nullopt;
        return ans;
    }
};
// END MinimumCover
