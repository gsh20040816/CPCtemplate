#pragma once
#include <cassert>
#include <bits/stdc++.h>
using namespace std;

struct DSU
{
    vector<int> fa, siz;

    DSU(int n = 0)
    {
        init(n);
    }

    void init(int n)
    {
        fa.resize(n + 1);
        iota(fa.begin(), fa.end(), 0);
        siz.assign(n + 1, 1);
    }

    int find(int x)
    {
        while (x != fa[x])
        {
            fa[x] = fa[fa[x]];
            x = fa[x];
        }
        return x;
    }

    bool merge(int x, int y)
    {
        x = find(x);
        y = find(y);
        if (x == y)
            return false;
        if (siz[x] < siz[y])
            swap(x, y);
        fa[y] = x;
        siz[x] += siz[y];
        return true;
    }
};

struct RollbackDSU
{
    vector<int> fa, siz;
    vector<pair<int, int>> his;

    RollbackDSU(int n) : fa(n + 1), siz(n + 1, 1)
    {
        iota(fa.begin(), fa.end(), 0);
    }

    int find(int x) const
    {
        while (x != fa[x])
            x = fa[x];
        return x;
    }

    int snapshot() const
    {
        return (int)his.size();
    }

    bool merge(int x, int y)
    {
        x = find(x);
        y = find(y);
        if (x == y)
            return false;
        if (siz[x] < siz[y])
            swap(x, y);
        his.push_back({y, siz[x]});
        fa[y] = x;
        siz[x] += siz[y];
        return true;
    }

    void rollback(int t)
    {
        assert(0 <= t && t <= snapshot());
        while (snapshot() > t)
        {
            auto [y, s] = his.back();
            his.pop_back();
            siz[fa[y]] = s;
            fa[y] = y;
        }
    }
};

template <class T = long long> struct Fenwick
{
    int n;
    vector<T> a;

    Fenwick(int n = 0) : n(n), a(n + 1)
    {
    }

    void add(int x, T v)
    {
        assert(x >= 1);
        for (; x <= n; x += x & -x)
            a[x] += v;
    }

    T sum(int x) const
    {
        T ans = 0;
        for (; x; x -= x & -x)
            ans += a[x];
        return ans;
    }

    T query(int l, int r) const
    {
        return sum(r) - sum(l - 1);
    }

    // Nonnegative frequencies; returns n+1 if k exceeds total.
    int kth(T k) const
    {
        assert(k > 0);
        int x = 0, b = 1;
        while (b <= n / 2)
            b *= 2;
        for (; b; b >>= 1)
            if (x + b <= n && a[x + b] < k)
            {
                k -= a[x + b];
                x += b;
            }
        return x + 1;
    }
};

struct LazySeg
{
    int n;
    vector<long long> sum, tag;

    LazySeg(int n) : n(n), sum(4 * n + 4), tag(4 * n + 4)
    {
        assert(n > 0);
    }

    void apply(int p, int l, int r, long long v)
    {
        sum[p] += (r - l + 1) * v;
        tag[p] += v;
    }

    void push(int p, int l, int r)
    {
        int m = (l + r) / 2;
        apply(p * 2, l, m, tag[p]);
        apply(p * 2 + 1, m + 1, r, tag[p]);
        tag[p] = 0;
    }

    void add(int l, int r, long long v)
    {
        add(1, 1, n, l, r, v);
    }

    void add(int p, int l, int r, int ql, int qr, long long v)
    {
        if (ql <= l && r <= qr)
        {
            apply(p, l, r, v);
            return;
        }
        push(p, l, r);
        int m = (l + r) / 2;
        if (ql <= m)
            add(p * 2, l, m, ql, qr, v);
        if (qr > m)
            add(p * 2 + 1, m + 1, r, ql, qr, v);
        sum[p] = sum[p * 2] + sum[p * 2 + 1];
    }

    long long query(int l, int r)
    {
        return query(1, 1, n, l, r);
    }

    long long query(int p, int l, int r, int ql, int qr)
    {
        if (ql <= l && r <= qr)
            return sum[p];
        push(p, l, r);
        int m = (l + r) / 2;
        long long ans = 0;
        if (ql <= m)
            ans += query(p * 2, l, m, ql, qr);
        if (qr > m)
            ans += query(p * 2 + 1, m + 1, r, ql, qr);
        return ans;
    }
};

struct XorBasis
{
    unsigned long long a[64]{};

    bool insert(unsigned long long x)
    {
        for (int i = 63; i >= 0; i--)
            if (x >> i & 1)
            {
                if (!a[i])
                {
                    a[i] = x;
                    return true;
                }
                x ^= a[i];
            }
        return false;
    }

    unsigned long long query(unsigned long long x = 0) const
    {
        for (int i = 63; i >= 0; i--)
            x = max(x, x ^ a[i]);
        return x;
    }
};
