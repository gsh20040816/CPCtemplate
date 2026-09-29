#pragma once
#include <algorithm>
#include <bit>
#include <cassert>
#include <vector>
using namespace std;

struct WaveletMatrix
{
    int n, h;
    vector<long long> val;
    vector<int> mid;
    vector<vector<unsigned long long>> bit;
    vector<vector<int>> sum;

    WaveletMatrix(const vector<long long> &a) : n(a.size()), val(a)
    {
        sort(val.begin(), val.end());
        val.erase(unique(val.begin(), val.end()), val.end());
        h = bit_width((unsigned)max(1, (int)val.size()) - 1);
        mid.resize(h);
        bit.assign(h, vector<unsigned long long>(n / 64 + 1));
        sum.assign(h, vector<int>(n / 64 + 1));
        vector<int> v(n), w(n);
        for (int i = 0; i < n; i++)
            v[i] = lower_bound(val.begin(), val.end(), a[i]) - val.begin();
        for (int d = h - 1; d >= 0; d--)
        {
            for (int i = 0; i < n; i++)
            {
                if (v[i] >> d & 1)
                    bit[d][i / 64] |= 1ULL << (i % 64);
                else
                    mid[d]++;
            }
            for (int i = 1; i < (int)sum[d].size(); i++)
                sum[d][i] = sum[d][i - 1] + popcount(bit[d][i - 1]);
            int l = 0, r = mid[d];
            for (int x : v)
            {
                if (x >> d & 1)
                    w[r++] = x;
                else
                    w[l++] = x;
            }
            v.swap(w);
        }
    }

    // Internal: number of one bits before position i at level d.
    int rank(int d, int i) const
    {
        return sum[d][i / 64] + popcount(bit[d][i / 64] & ((1ULL << (i % 64)) - 1));
    }

    // [l, r), k is zero-based; requires 0 <= k < r-l.
    long long kth(int l, int r, int k) const
    {
        assert(0 <= l && l <= r && r <= n && 0 <= k && k < r - l);
        int x = 0;
        for (int d = h - 1; d >= 0; d--)
        {
            int a = rank(d, l), b = rank(d, r);
            int z = r - l - b + a;
            if (k < z)
            {
                l -= a;
                r -= b;
            }
            else
            {
                k -= z;
                x |= 1 << d;
                l = mid[d] + a;
                r = mid[d] + b;
            }
        }
        return val[x];
    }

    // Count values < x; empty intervals and absent values are allowed.
    int less(int l, int r, long long x) const
    {
        assert(0 <= l && l <= r && r <= n);
        int q = lower_bound(val.begin(), val.end(), x) - val.begin();
        if (q == (int)val.size()) return r - l;
        int ans = 0;
        for (int d = h - 1; d >= 0; d--)
        {
            int a = rank(d, l), b = rank(d, r);
            if (q >> d & 1)
            {
                ans += r - l - b + a;
                l = mid[d] + a;
                r = mid[d] + b;
            }
            else
            {
                l -= a;
                r -= b;
            }
        }
        return ans;
    }

    int freq(int l, int r, long long x) const
    {
        assert(0 <= l && l <= r && r <= n);
        int q = lower_bound(val.begin(), val.end(), x) - val.begin();
        if (q == (int)val.size() || val[q] != x) return 0;
        for (int d = h - 1; d >= 0; d--)
        {
            int a = rank(d, l), b = rank(d, r);
            if (q >> d & 1)
            {
                l = mid[d] + a;
                r = mid[d] + b;
            }
            else
            {
                l -= a;
                r -= b;
            }
        }
        return r - l;
    }
};
