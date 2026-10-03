#pragma once
#include "data_structure.hpp"

struct Dominance3D
{
    static vector<int> count(const vector<array<long long, 3>> &p)
    {
        assert(p.size() <= INT_MAX / 2);
        int n = int(p.size());
        vector<int> order(n), group(n), w;
        iota(order.begin(), order.end(), 0);
        sort(order.begin(), order.end(), [&](int i, int j) { return p[i] < p[j]; });
        vector<array<long long, 3>> v;
        for (int i : order)
        {
            if (v.empty() || v.back() != p[i])
            {
                v.push_back(p[i]);
                w.push_back(0);
            }
            ++w.back();
            group[i] = int(v.size()) - 1;
        }
        int m = int(v.size());
        vector<long long> z;
        for (auto q : v) z.push_back(q[2]);
        sort(z.begin(), z.end());
        z.erase(unique(z.begin(), z.end()), z.end());
        struct Node
        {
            long long y;
            int z, w, id;
        };
        vector<Node> a(m), tmp(m);
        vector<int> cnt(m), ans(n);
        for (int i = 0; i < m; ++i)
            a[i] = {v[i][1], int(lower_bound(z.begin(), z.end(), v[i][2]) -
                                z.begin()) + 1, w[i], i};
        Fenwick<int> bit(int(z.size()));
        auto cdq = [&](auto &&self, int l, int r) -> void
        {
            if (r - l <= 1) return;
            int mid = l + (r - l) / 2;
            self(self, l, mid);
            self(self, mid, r);
            int i = l, k = l;
            for (int j = mid; j < r; ++j)
            {
                while (i < mid && a[i].y <= a[j].y)
                {
                    bit.add(a[i].z, a[i].w);
                    tmp[k++] = a[i++];
                }
                cnt[a[j].id] += bit.sum(a[j].z);
                tmp[k++] = a[j];
            }
            for (int t = l; t < i; ++t) bit.add(a[t].z, -a[t].w);
            while (i < mid) tmp[k++] = a[i++];
            copy(tmp.begin() + l, tmp.begin() + r, a.begin() + l);
        };
        cdq(cdq, 0, m);
        for (int i = 0; i < n; ++i)
            ans[i] = cnt[group[i]] + w[group[i]] - 1;
        return ans;
    }
};
