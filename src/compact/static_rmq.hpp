#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <climits>
#include <cstdint>
#include <functional>
#include <vector>
using namespace std;

template <class T = long long, class Cmp = less<T>>
struct StaticRMQ
{
    int n, b;
    vector<T> a;
    vector<uint32_t> mask;
    vector<vector<int>> st;
    Cmp cmp;

    StaticRMQ(const vector<T> &v, Cmp cmp = Cmp()) : a(v), cmp(cmp)
    {
        assert(v.size() <= INT_MAX / 2);
        n = v.size();
        b = max(1, (int)bit_width((uint32_t)n));
        mask.resize(n);
        if (!n) return;
        st.push_back({});
        uint32_t s = 0;
        for (int i = 0; i < n; i++)
        {
            int start = i - i % b;
            if (i % b == 0) s = 0;
            while (s && cmp(a[i], a[start + bit_width(s) - 1]))
            {
                s ^= uint32_t(1) << (bit_width(s) - 1);
            }
            s |= uint32_t(1) << (i % b);
            mask[i] = s;
            if (i % b == b - 1 || i == n - 1)
            {
                st[0].push_back(start + countr_zero(s));
            }
        }
        int m = st[0].size();
        for (int k = 1; (1 << k) <= m; k++)
        {
            st.push_back(vector<int>(m - (1 << k) + 1));
            for (int i = 0; i + (1 << k) <= m; i++)
            {
                st[k][i] = better(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
            }
        }
    }

    int better(int x, int y) const
    {
        if (cmp(a[x], a[y])) return x;
        if (cmp(a[y], a[x])) return y;
        return min(x, y);
    }

    int small(int l, int r) const
    {
        return l + countr_zero(mask[r - 1] >> (l % b));
    }

    int query(int l, int r) const
    {
        assert(0 <= l && l < r && r <= n);
        int x = l / b, y = (r - 1) / b;
        if (x == y) return small(l, r);
        int ans = better(small(l, (x + 1) * b), small(y * b, r));
        x++;
        if (x < y)
        {
            int k = bit_width((uint32_t)(y - x)) - 1;
            ans = better(ans, better(st[k][x], st[k][y - (1 << k)]));
        }
        return ans;
    }
};
