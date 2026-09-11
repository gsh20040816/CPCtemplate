#pragma once
#include <algorithm>
#include <cassert>
#include <vector>
using namespace std;

template <int N, int NODES> struct Dynamic_Kth
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, sum = 0;
    };

    int n, tot, free_head;
    int bit[N + 1], rank[N + 1];
    vector<ll> vals;
    Node t[NODES + 1];

    void Init(const vector<ll> &a, const vector<ll> &future = {})
    {
        n = a.size();
        assert(0 < n && n <= N);
        tot = 0;
        free_head = 0;
        t[0] = Node{};
        fill(bit, bit + n + 1, 0);
        vals = future;
        vals.insert(vals.end(), a.begin(), a.end());
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        for ( int i = 1; i <= n; i++ )
        {
            rank[i] = Id(a[i - 1]);
            Modify(i, rank[i], 1);
        }
    }

    int Id(ll value) const
    {
        int p = lower_bound(vals.begin(), vals.end(), value) - vals.begin();
        assert(p < (int)vals.size() && vals[p] == value);
        return p;
    }

    int New_Node()
    {
        if ( !free_head )
        {
            assert(tot < NODES);
            int p = ++tot;
            t[p] = Node{};
            return p;
        }
        int p = free_head;
        free_head = t[p].l;
        t[p] = Node{};
        return p;
    }

    int Update(int p, int l, int r, int x, int delta)
    {
        if ( !p )
            p = New_Node();
        t[p].sum += delta;
        if ( l < r )
        {
            int m = (l + r) / 2;
            if ( x <= m )
            {
                int child = Update(t[p].l, l, m, x, delta);
                t[p].l = child;
            }
            else
            {
                int child = Update(t[p].r, m + 1, r, x, delta);
                t[p].r = child;
            }
        }
        if ( !t[p].sum )
        {
            t[p].l = free_head;
            free_head = p;
            return 0;
        }
        return p;
    }

    void Modify(int pos, int x, int delta)
    {
        for ( int i = pos; i <= n; i += i & -i )
            bit[i] = Update(bit[i], 0, (int)vals.size() - 1, x, delta);
    }

    void Set(int pos, ll value)
    {
        assert(1 <= pos && pos <= n);
        int x = Id(value);
        if ( rank[pos] == x )
            return;
        Modify(pos, rank[pos], -1);
        Modify(pos, x, 1);
        rank[pos] = x;
    }

    ll Kth(int l, int r, int k) const
    {
        assert(1 <= l && l <= r && r <= n && 1 <= k && k <= r - l + 1);
        vector<int> a, b;
        for ( int i = r; i; i -= i & -i )
            a.push_back(bit[i]);
        for ( int i = l - 1; i; i -= i & -i )
            b.push_back(bit[i]);
        int L = 0, R = (int)vals.size() - 1;
        while ( L < R )
        {
            int count = 0;
            for ( int p : a )
                count += t[t[p].l].sum;
            for ( int p : b )
                count -= t[t[p].l].sum;
            bool left = k <= count;
            if ( !left )
                k -= count;
            for ( int &p : a )
                p = left ? t[p].l : t[p].r;
            for ( int &p : b )
                p = left ? t[p].l : t[p].r;
            int m = (L + R) / 2;
            if ( left )
                R = m;
            else
                L = m + 1;
        }
        return vals[L];
    }
};
