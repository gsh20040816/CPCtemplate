#pragma once
#include <cassert>
#include <optional>
#include <random>
#include <vector>
using namespace std;

struct OrderedTreap
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0;
        ll val = 0;
        unsigned long long pri = 0;
    };

    vector<Node> a{Node{}};
    mt19937_64 rng;
    int root = 0;

    OrderedTreap(unsigned long long seed = 712367821) : rng(seed) {}

    void pull(int p) { a[p].siz = a[a[p].l].siz + a[a[p].r].siz + 1; }

    int node(ll x)
    {
        int p = a.size();
        a.push_back({0, 0, 1, x, rng()});
        return p;
    }

    // left: val < x, or val <= x when equal is true. No x-1 overflow.
    void split(int p, ll x, int &l, int &r, bool equal = false)
    {
        if (!p)
        {
            l = 0;
            r = 0;
            return;
        }
        if (a[p].val < x || (equal && a[p].val == x))
        {
            l = p;
            split(a[p].r, x, a[p].r, r, equal);
        }
        else
        {
            r = p;
            split(a[p].l, x, l, a[p].l, equal);
        }
        pull(p);
    }

    int merge(int l, int r)
    {
        if (!l || !r) return l ? l : r;
        if (a[l].pri > a[r].pri)
        {
            a[l].r = merge(a[l].r, r);
            pull(l);
            return l;
        }
        a[r].l = merge(l, a[r].l);
        pull(r);
        return r;
    }

    void insert(ll x)
    {
        int p = node(x), l, r;
        split(root, x, l, r);
        root = merge(merge(l, p), r);
    }

    bool erase(ll x)
    {
        int l, mid, r;
        split(root, x, l, mid);
        split(mid, x, mid, r, true);
        bool found = mid != 0;
        if (mid) mid = merge(a[mid].l, a[mid].r);
        root = merge(l, merge(mid, r));
        return found;
    }

    int size() const { return a[root].siz; }

    int less(ll x, bool equal = false) const
    {
        int p = root, ans = 0;
        while (p)
        {
            if (a[p].val < x || (equal && a[p].val == x))
            {
                ans += a[a[p].l].siz + 1;
                p = a[p].r;
            }
            else
                p = a[p].l;
        }
        return ans;
    }

    int rank(ll x) const { return less(x) + 1; }

    ll kth(int k) const
    {
        assert(1 <= k && k <= size());
        int p = root;
        while (true)
        {
            int left = a[a[p].l].siz;
            if (k == left + 1) return a[p].val;
            if (k <= left)
                p = a[p].l;
            else
            {
                k -= left + 1;
                p = a[p].r;
            }
        }
    }

    optional<ll> prev(ll x) const
    {
        int k = less(x);
        if (!k) return nullopt;
        return kth(k);
    }

    optional<ll> next(ll x) const
    {
        int k = less(x, true);
        if (k == size()) return nullopt;
        return kth(k + 1);
    }
};

struct SequenceTreap
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, siz = 0;
        ll val = 0, sum = 0, tag = 0;
        unsigned long long pri = 0;
        bool rev = false;
    };

    vector<Node> a{Node{}};
    mt19937_64 rng;
    int root = 0;

    SequenceTreap(unsigned long long seed = 712367821) : rng(seed) {}

    int size() const { return a[root].siz; }

    void pull(int p)
    {
        a[p].siz = a[a[p].l].siz + a[a[p].r].siz + 1;
        a[p].sum = a[a[p].l].sum + a[p].val + a[a[p].r].sum;
    }

    void apply_add(int p, ll x)
    {
        if (!p) return;
        a[p].val += x;
        a[p].sum += x * a[p].siz;
        a[p].tag += x;
    }

    void apply_reverse(int p)
    {
        if (!p) return;
        swap(a[p].l, a[p].r);
        a[p].rev = !a[p].rev;
    }

    void push(int p)
    {
        if (a[p].rev)
        {
            apply_reverse(a[p].l);
            apply_reverse(a[p].r);
            a[p].rev = false;
        }
        if (a[p].tag)
        {
            apply_add(a[p].l, a[p].tag);
            apply_add(a[p].r, a[p].tag);
            a[p].tag = 0;
        }
    }

    // Split into the first k elements and the rest.
    void split(int p, int k, int &l, int &r)
    {
        if (!p)
        {
            l = 0;
            r = 0;
            return;
        }
        push(p);
        int left = a[a[p].l].siz;
        if (k > left)
        {
            l = p;
            split(a[p].r, k - left - 1, a[p].r, r);
        }
        else
        {
            r = p;
            split(a[p].l, k, l, a[p].l);
        }
        pull(p);
    }

    int merge(int l, int r)
    {
        if (!l || !r) return l ? l : r;
        if (a[l].pri > a[r].pri)
        {
            push(l);
            a[l].r = merge(a[l].r, r);
            pull(l);
            return l;
        }
        push(r);
        a[r].l = merge(l, a[r].l);
        pull(r);
        return r;
    }

    // Insert after the first k elements, 0 <= k <= size().
    void insert(int k, ll value)
    {
        assert(0 <= k && k <= size());
        int p = a.size(), l, r;
        a.push_back({0, 0, 1, value, value, 0, rng(), false});
        split(root, k, l, r);
        root = merge(merge(l, p), r);
    }

    // All range operations use 1-based inclusive intervals.
    void erase(int l, int r)
    {
        assert(1 <= l && l <= r && r <= size());
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        root = merge(x, z);
    }

    void reverse(int l, int r)
    {
        assert(1 <= l && l <= r && r <= size());
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        apply_reverse(y);
        root = merge(merge(x, y), z);
    }

    void add(int l, int r, ll value)
    {
        assert(1 <= l && l <= r && r <= size());
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        apply_add(y, value);
        root = merge(merge(x, y), z);
    }

    ll query(int l, int r)
    {
        assert(1 <= l && l <= r && r <= size());
        int x, y, z;
        split(root, r, y, z);
        split(y, l - 1, x, y);
        ll ans = a[y].sum;
        root = merge(merge(x, y), z);
        return ans;
    }

    void collect(int p, vector<ll> &out)
    {
        if (!p) return;
        push(p);
        collect(a[p].l, out);
        out.push_back(a[p].val);
        collect(a[p].r, out);
    }

    vector<ll> values()
    {
        vector<ll> answer;
        collect(root, answer);
        return answer;
    }
};
