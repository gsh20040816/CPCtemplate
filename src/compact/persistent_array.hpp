#pragma once
#include <cassert>
#include <vector>
using namespace std;

struct PersistentArray
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0;
        ll value = 0;
    };

    int n;
    vector<Node> t{Node{}};
    vector<int> root;

    PersistentArray(const vector<ll> &a, int changes = 0) : n(a.size())
    {
        assert(n > 0 && changes >= 0);
        int levels = 1;
        for (int x = n - 1; x; x >>= 1)
            levels++;
        t.reserve(2ULL * n + 1ULL * changes * levels + 1);
        root.push_back(build(1, n, a));
    }

    int build(int l, int r, const vector<ll> &a)
    {
        int p = t.size();
        t.push_back(Node{});
        if (l == r)
            t[p].value = a[l - 1];
        else
        {
            int m = (l + r) / 2;
            int left = build(l, m, a);
            int right = build(m + 1, r, a);
            t[p].l = left;
            t[p].r = right;
        }
        return p;
    }

    int modify(int old, int l, int r, int pos, ll value)
    {
        int p = t.size();
        Node copy = t[old];
        t.push_back(copy);
        if (l == r)
            t[p].value = value;
        else
        {
            int m = (l + r) / 2;
            if (pos <= m)
            {
                int child = modify(t[old].l, l, m, pos, value);
                t[p].l = child;
            }
            else
            {
                int child = modify(t[old].r, m + 1, r, pos, value);
                t[p].r = child;
            }
        }
        return p;
    }

    // Create a new version from any existing version. Positions are 1-based.
    int set(int version, int pos, ll value)
    {
        assert(0 <= version && version < (int)root.size());
        assert(1 <= pos && pos <= n);
        int p = modify(root[version], 1, n, pos, value);
        root.push_back(p);
        return (int)root.size() - 1;
    }

    int copy(int version)
    {
        assert(0 <= version && version < (int)root.size());
        root.push_back(root[version]);
        return (int)root.size() - 1;
    }

    ll query(int version, int pos) const
    {
        assert(0 <= version && version < (int)root.size());
        assert(1 <= pos && pos <= n);
        int p = root[version], l = 1, r = n;
        while (l < r)
        {
            int m = (l + r) / 2;
            if (pos <= m)
            {
                p = t[p].l;
                r = m;
            }
            else
            {
                p = t[p].r;
                l = m + 1;
            }
        }
        return t[p].value;
    }
};
