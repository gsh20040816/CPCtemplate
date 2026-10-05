#pragma once
#include <cassert>
#include <climits>
#include <cstddef>
#include <optional>
#include <vector>
using namespace std;

// BEGIN ExactCover
struct ExactCover
{
    struct Node { int l, r, u, d, c, row; };
    int m;
    vector<Node> a;
    vector<int> s, ans;

    ExactCover(int columns, const vector<vector<int>> &rows) : m(columns)
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
                a[u].d = a[c].u = x;
                s[c]++;
                if (h == -1) h = x;
                else
                {
                    int l = a[h].l;
                    a[x].l = l; a[x].r = h;
                    a[l].r = a[h].l = x;
                }
            }
        }
    }

    void cover(int c)
    {
        a[a[c].l].r = a[c].r;
        a[a[c].r].l = a[c].l;
        for (int i = a[c].d; i != c; i = a[i].d)
            for (int j = a[i].r; j != i; j = a[j].r)
            {
                a[a[j].u].d = a[j].d;
                a[a[j].d].u = a[j].u;
                s[a[j].c]--;
            }
    }

    void uncover(int c)
    {
        for (int i = a[c].u; i != c; i = a[i].u)
            for (int j = a[i].l; j != i; j = a[j].l)
            {
                s[a[j].c]++;
                a[a[j].u].d = a[a[j].d].u = j;
            }
        a[a[c].l].r = a[a[c].r].l = c;
    }

    bool dfs()
    {
        int c = a[0].r;
        if (!c) return true;
        for (int j = a[c].r; j; j = a[j].r)
            if (s[j] < s[c]) c = j;
        cover(c);
        for (int i = a[c].d; i != c; i = a[i].d)
        {
            ans.push_back(a[i].row);
            for (int j = a[i].r; j != i; j = a[j].r) cover(a[j].c);
            bool ok = dfs();
            for (int j = a[i].l; j != i; j = a[j].l) uncover(a[j].c);
            if (ok)
            {
                uncover(c);
                return true;
            }
            ans.pop_back();
        }
        uncover(c);
        return false;
    }

    optional<vector<int>> solve()
    {
        ans.clear();
        ans.reserve(m);
        if (!dfs()) return nullopt;
        return ans;
    }
};
// END ExactCover
