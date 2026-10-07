#pragma once
#include "ordered_set.hpp"
#include <cassert>
#include <numeric>

struct SequenceKth
{
    using ll = long long;
    using Key = pair<ll, int>;

    struct Node
    {
        int l = 0, r = 0, sz = 0;
        ll val = 0;
        ost<Key> keys;
    };

    vector<Node> a;
    int root = 0;

    SequenceKth(const vector<ll> &v = {}) : a(v.size() + 1)
    {
        vector<int> ids;
        for (int i = 0; i < (int)v.size(); i++)
        {
            a[i + 1].val = v[i];
            ids.push_back(i + 1);
        }
        root = build(ids, 0, (int)ids.size());
    }

    int size() const
    {
        return a[root].sz;
    }

    void pull(int u)
    {
        int l = a[u].l;
        int r = a[u].r;
        a[u].sz = a[l].sz + a[r].sz + 1;
        a[u].keys.clear();
        a[u].keys.insert({a[u].val, u});
        for (auto x : a[l].keys)
            a[u].keys.insert(x);
        for (auto x : a[r].keys)
            a[u].keys.insert(x);
    }

    int build(const vector<int> &v, int l, int r)
    {
        if (l == r)
            return 0;
        int m = l + (r - l) / 2;
        int u = v[m];
        a[u].l = build(v, l, m);
        a[u].r = build(v, m + 1, r);
        pull(u);
        return u;
    }

    void collect(int u, vector<int> &v) const
    {
        if (!u)
            return;
        collect(a[u].l, v);
        v.push_back(u);
        collect(a[u].r, v);
    }

    int balance(int u)
    {
        a[u].sz = a[a[u].l].sz + a[a[u].r].sz + 1;
        if (4LL * max(a[a[u].l].sz, a[a[u].r].sz) <= 3LL * a[u].sz)
            return u;
        vector<int> v;
        v.reserve(a[u].sz);
        collect(u, v);
        return build(v, 0, (int)v.size());
    }

    int insert(int u, int k, int id)
    {
        if (!u)
            return id;
        a[u].keys.insert({a[id].val, id});
        int left = a[a[u].l].sz;
        if (k <= left)
            a[u].l = insert(a[u].l, k, id);
        else
            a[u].r = insert(a[u].r, k - left - 1, id);
        return balance(u);
    }

    void insert(int k, ll x)
    {
        assert(0 <= k && k <= size());
        int id = (int)a.size();
        a.emplace_back();
        a[id].val = x;
        a[id].sz = 1;
        a[id].keys.insert({x, id});
        root = insert(root, k, id);
    }

    Key set(int u, int k, ll x)
    {
        int left = a[a[u].l].sz;
        Key old;
        if (k <= left)
            old = set(a[u].l, k, x);
        else if (k == left + 1)
        {
            old = {a[u].val, u};
            a[u].val = x;
        }
        else
            old = set(a[u].r, k - left - 1, x);
        a[u].keys.erase(old);
        a[u].keys.insert({x, old.second});
        return old;
    }

    void set(int k, ll x)
    {
        assert(1 <= k && k <= size());
        set(root, k, x);
    }

    int less(int u, int l, int r, ll x, bool equal) const
    {
        if (!u)
            return 0;
        if (l <= 1 && a[u].sz <= r)
            return a[u].keys.order_of_key({x, equal ? (int)a.size() : 0});
        int left = a[a[u].l].sz;
        int ans = 0;
        if (l <= left)
            ans += less(a[u].l, l, r, x, equal);
        if (l <= left + 1 && left + 1 <= r)
            ans += a[u].val < x || (equal && a[u].val == x);
        if (r > left + 1)
            ans += less(a[u].r, l - left - 1, r - left - 1, x, equal);
        return ans;
    }

    int less(int l, int r, ll x, bool equal = false) const
    {
        assert(1 <= l && l <= r && r <= size());
        return less(root, l, r, x, equal);
    }

    ll kth(int l, int r, int k) const
    {
        assert(1 <= l && l <= r && r <= size());
        assert(1 <= k && k <= r - l + 1);
        ll lo = a[root].keys.begin()->first;
        ll hi = a[root].keys.rbegin()->first;
        while (lo < hi)
        {
            ll mid = midpoint(lo, hi);
            if (less(l, r, mid, true) >= k)
                hi = mid;
            else
                lo = mid + 1;
        }
        return lo;
    }
};
