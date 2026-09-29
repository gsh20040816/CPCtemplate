#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <vector>
using namespace std;

struct DivisionTree
{
    int n;
    vector<long long> sorted;
    vector<vector<long long>> a;
    vector<vector<int>> pre;

    DivisionTree(const vector<long long> &v) : n(v.size()), sorted(v)
    {
        sort(sorted.begin(), sorted.end());
        int h = bit_width((unsigned)max(1, n) - 1) + 1;
        a.assign(h, vector<long long>(n));
        pre.assign(h, vector<int>(n + 1));
        a[0] = v;
        if (n) build(0, n, 0);
    }

    void build(int l, int r, int d)
    {
        if (r - l == 1) return;
        int m = l + (r - l) / 2, same = m - l;
        for (int i = l; i < r; i++) same -= a[d][i] < sorted[m - 1];
        int x = l, y = m;
        for (int i = l; i < r; i++)
        {
            bool left = a[d][i] < sorted[m - 1];
            if (a[d][i] == sorted[m - 1] && same > 0)
            {
                left = true;
                same--;
            }
            if (left)
                a[d + 1][x++] = a[d][i];
            else
                a[d + 1][y++] = a[d][i];
            pre[d][i + 1] = pre[d][i] + left;
        }
        build(l, m, d + 1);
        build(m, r, d + 1);
    }

    long long query(int L, int R, int l, int r, int d, int k) const
    {
        if (r - l == 1) return a[d][l];
        int m = L + (R - L) / 2;
        int before = pre[d][l] - pre[d][L], cnt = pre[d][r] - pre[d][l];
        if (k < cnt) return query(L, m, L + before, L + before + cnt, d + 1, k);
        int x = m + (l - L - before);
        return query(m, R, x, x + (r - l - cnt), d + 1, k - cnt);
    }

    long long kth(int l, int r, int k) const
    {
        assert(0 <= l && l < r && r <= n && 0 <= k && k < r - l);
        return query(0, n, l, r, 0, k);
    }
};
