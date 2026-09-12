#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

struct DynamicKth
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    int n, free_head = 0;
    vector<int> bit, rank;
    vector<ll> vals;
    vector<Node> t{Node{}};

    DynamicKth(const vector<ll> &a, vector<ll> future = {})
        : n(a.size()), bit(n + 1), rank(n + 1)
    {
        assert(n > 0);
        vals = future;
        vals.insert(vals.end(), a.begin(), a.end());
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        for (int i = 1; i <= n; i++)
        {
            rank[i] = id(a[i - 1]);
            modify(i, rank[i], 1);
        }
    }

    int id(ll value) const
    {
        int p = lower_bound(vals.begin(), vals.end(), value) - vals.begin();
        assert(p < (int)vals.size() && vals[p] == value);
        return p;
    }

    int new_node()
    {
        if (!free_head)
        {
            t.push_back(Node{});
            return (int)t.size() - 1;
        }
        int p = free_head;
        free_head = t[p].l;
        t[p] = Node{};
        return p;
    }

    int update(int p, int l, int r, int x, int delta)
    {
        if (!p) p = new_node();
        t[p].sum += delta;
        if (l < r)
        {
            int m = (l + r) / 2;
            if (x <= m)
            {
                int child = update(t[p].l, l, m, x, delta);
                t[p].l = child;
            }
            else
            {
                int child = update(t[p].r, m + 1, r, x, delta);
                t[p].r = child;
            }
        }
        if (!t[p].sum)
        {
            t[p].l = free_head;
            free_head = p;
            return 0;
        }
        return p;
    }

    void modify(int pos, int x, int delta)
    {
        for (int i = pos; i <= n; i += i & -i)
            bit[i] = update(bit[i], 0, (int)vals.size() - 1, x, delta);
    }

    void set(int pos, ll value)
    {
        assert(1 <= pos && pos <= n);
        int x = id(value);
        if (rank[pos] == x) return;
        modify(pos, rank[pos], -1);
        modify(pos, x, 1);
        rank[pos] = x;
    }

    ll kth(int l, int r, int k) const
    {
        assert(1 <= l && l <= r && r <= n && 1 <= k && k <= r - l + 1);
        vector<int> a, b;
        for (int i = r; i; i -= i & -i) a.push_back(bit[i]);
        for (int i = l - 1; i; i -= i & -i) b.push_back(bit[i]);
        int L = 0, R = (int)vals.size() - 1;
        while (L < R)
        {
            int count = 0;
            for (int p : a) count += t[t[p].l].sum;
            for (int p : b) count -= t[t[p].l].sum;
            bool left = k <= count;
            if (!left) k -= count;
            for (int &p : a) p = left ? t[p].l : t[p].r;
            for (int &p : b) p = left ? t[p].l : t[p].r;
            int m = (L + R) / 2;
            if (left)
                R = m;
            else
                L = m + 1;
        }
        return vals[L];
    }
};
