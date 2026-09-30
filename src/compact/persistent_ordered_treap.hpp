#pragma once
#include <cassert>
#include <optional>
#include <random>
#include <vector>
using namespace std;

// Version 0 is empty. Expected O(log(size+1)) per operation; copy is amortized O(1).
// Updates retain O(path length) nodes, queries allocate none. No worst-case bound.
// Keep version/node counts and each multiset size below INT_MAX; reserve t if needed.
// Reconstruct the object for an independent test case.
struct PersistentOrderedTreap
{
    using ll = long long;

    struct Node
    {
        ll val = 0;
        unsigned long long pri = 0;
        int l = 0, r = 0, siz = 0, cnt = 0;
    };

    vector<Node> t{Node{}};
    vector<int> root{0};
    mt19937_64 rng;

    PersistentOrderedTreap(unsigned long long seed = 712367821) : rng(seed) {}

    void check(int v) const { assert(0 <= v && v < (int)root.size()); }

    int clone(int p)
    {
        Node node = t[p];
        t.push_back(node);
        return (int)t.size() - 1;
    }

    void pull(int p) { t[p].siz = t[t[p].l].siz + t[t[p].r].siz + t[p].cnt; }

    // Only rotate freshly copied nodes; the promoted child was copied by add.
    int add(int p, ll x)
    {
        if (!p)
        {
            t.push_back({x, rng(), 0, 0, 1, 1});
            return (int)t.size() - 1;
        }
        int u = clone(p);
        if (x == t[u].val)
            t[u].cnt++;
        else if (x < t[u].val)
        {
            int q = add(t[u].l, x);
            t[u].l = q;
            if (t[q].pri > t[u].pri)
            {
                t[u].l = t[q].r;
                t[q].r = u;
                pull(u);
                u = q;
            }
        }
        else
        {
            int q = add(t[u].r, x);
            t[u].r = q;
            if (t[q].pri > t[u].pri)
            {
                t[u].r = t[q].l;
                t[q].l = u;
                pull(u);
                u = q;
            }
        }
        pull(u);
        return u;
    }

    int merge(int l, int r)
    {
        if (!l || !r) return l ? l : r;
        if (t[l].pri > t[r].pri)
        {
            int u = clone(l);
            int q = merge(t[u].r, r);
            t[u].r = q;
            pull(u);
            return u;
        }
        int u = clone(r);
        int q = merge(l, t[u].l);
        t[u].l = q;
        pull(u);
        return u;
    }

    int remove(int p, ll x)
    {
        if (!p) return 0;
        if (x == t[p].val)
        {
            if (t[p].cnt == 1) return merge(t[p].l, t[p].r);
            int u = clone(p);
            t[u].cnt--;
            pull(u);
            return u;
        }
        bool left = x < t[p].val;
        int old = left ? t[p].l : t[p].r;
        int q = remove(old, x);
        if (q == old) return p;
        int u = clone(p);
        if (left)
            t[u].l = q;
        else
            t[u].r = q;
        pull(u);
        return u;
    }

    // Updates append versions; erase removes one occurrence, or changes nothing.
    int insert(int v, ll x)
    {
        check(v);
        int p = add(root[v], x);
        root.push_back(p);
        return (int)root.size() - 1;
    }

    int erase(int v, ll x)
    {
        check(v);
        int p = remove(root[v], x);
        root.push_back(p);
        return (int)root.size() - 1;
    }

    int copy(int v)
    {
        check(v);
        root.push_back(root[v]);
        return (int)root.size() - 1;
    }

    int size(int v) const
    {
        check(v);
        return t[root[v]].siz;
    }

    int less(int v, ll x, bool equal = false) const
    {
        check(v);
        int p = root[v], ans = 0;
        while (p)
        {
            if (t[p].val < x || (equal && t[p].val == x))
            {
                ans += t[t[p].l].siz + t[p].cnt;
                p = t[p].r;
            }
            else
                p = t[p].l;
        }
        return ans;
    }

    int rank(int v, ll x) const { return less(v, x) + 1; }

    // Ranks and k are 1-based. No sentinel values are reserved.
    ll kth(int v, int k) const
    {
        assert(1 <= k && k <= size(v));
        int p = root[v];
        while (true)
        {
            int left = t[t[p].l].siz;
            if (k <= left)
                p = t[p].l;
            else if (k <= left + t[p].cnt)
                return t[p].val;
            else
            {
                k -= left + t[p].cnt;
                p = t[p].r;
            }
        }
    }

    optional<ll> prev(int v, ll x) const
    {
        int k = less(v, x);
        if (!k) return nullopt;
        return kth(v, k);
    }

    optional<ll> next(int v, ll x) const
    {
        int k = less(v, x, true);
        if (k == size(v)) return nullopt;
        return kth(v, k + 1);
    }
};
