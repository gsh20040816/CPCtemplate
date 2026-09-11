#pragma once
#include <cassert>
#include <vector>
using namespace std;

template <int NODES> struct Persistent_Array
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0;
        ll value = 0;
    };

    int n;
    Node t[NODES + 1];
    int tot = 0;
    vector<int> root;

    void Init(const vector<ll> &a)
    {
        n = a.size();
        assert(n > 0);
        tot = 0;
        root.clear();
        root.push_back(Build(1, n, a));
    }

    int Build(int l, int r, const vector<ll> &a)
    {
        assert(tot < NODES);
        int p = ++tot;
        t[p] = Node{};
        if ( l == r )
            t[p].value = a[l - 1];
        else
        {
            int m = (l + r) / 2;
            int left = Build(l, m, a);
            int right = Build(m + 1, r, a);
            t[p].l = left;
            t[p].r = right;
        }
        return p;
    }

    int Modify(int old, int l, int r, int pos, ll value)
    {
        assert(tot < NODES);
        int p = ++tot;
        t[p] = t[old];
        if ( l == r )
            t[p].value = value;
        else
        {
            int m = (l + r) / 2;
            if ( pos <= m )
            {
                int child = Modify(t[old].l, l, m, pos, value);
                t[p].l = child;
            }
            else
            {
                int child = Modify(t[old].r, m + 1, r, pos, value);
                t[p].r = child;
            }
        }
        return p;
    }

    // Create a new version from any existing version. Positions are 1-based.
    int Set(int version, int pos, ll value)
    {
        assert(0 <= version && version < (int)root.size());
        assert(1 <= pos && pos <= n);
        int p = Modify(root[version], 1, n, pos, value);
        root.push_back(p);
        return (int)root.size() - 1;
    }

    int Copy(int version)
    {
        assert(0 <= version && version < (int)root.size());
        root.push_back(root[version]);
        return (int)root.size() - 1;
    }

    ll Query(int version, int pos) const
    {
        assert(0 <= version && version < (int)root.size());
        assert(1 <= pos && pos <= n);
        int p = root[version], l = 1, r = n;
        while ( l < r )
        {
            int m = (l + r) / 2;
            if ( pos <= m )
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
