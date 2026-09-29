#pragma once
#include <algorithm>
#include <cassert>
#include <optional>
#include <vector>
using namespace std;

struct ScapegoatTree
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, count = 0, size = 0, nodes = 0, live = 0;
        ll value = 0;
    };

    vector<Node> a{Node{}};
    int root = 0;

    int size() const { return a[root].size; }

    void pull(int p)
    {
        int l = a[p].l, r = a[p].r;
        a[p].size = a[l].size + a[r].size + a[p].count;
        a[p].nodes = a[l].nodes + a[r].nodes + 1;
        a[p].live = a[l].live + a[r].live + (a[p].count > 0);
    }

    void collect(int p, vector<int> &v)
    {
        if (!p) return;
        collect(a[p].l, v);
        if (a[p].count) v.push_back(p);
        collect(a[p].r, v);
    }

    int build(const vector<int> &v, int l, int r)
    {
        if (l == r) return 0;
        int m = l + (r - l) / 2, p = v[m];
        a[p].l = build(v, l, m);
        a[p].r = build(v, m + 1, r);
        pull(p);
        return p;
    }

    int balance(int p)
    {
        pull(p);
        int heavy = max(a[a[p].l].nodes, a[a[p].r].nodes);
        if (4LL * heavy <= 3LL * a[p].nodes && 2LL * a[p].live >= a[p].nodes) return p;
        vector<int> v;
        v.reserve(a[p].live);
        collect(p, v);
        return build(v, 0, v.size());
    }

    int insert(int p, ll x)
    {
        if (!p)
        {
            a.push_back({0, 0, 1, 1, 1, 1, x});
            return a.size() - 1;
        }
        if (x < a[p].value)
            a[p].l = insert(a[p].l, x);
        else if (x > a[p].value)
            a[p].r = insert(a[p].r, x);
        else
            a[p].count++;
        return balance(p);
    }

    int erase(int p, ll x, bool &found)
    {
        if (!p) return 0;
        if (x < a[p].value)
            a[p].l = erase(a[p].l, x, found);
        else if (x > a[p].value)
            a[p].r = erase(a[p].r, x, found);
        else if (a[p].count)
        {
            a[p].count--;
            found = true;
        }
        return balance(p);
    }

    void insert(ll x) { root = insert(root, x); }

    bool erase(ll x)
    {
        bool found = false;
        root = erase(root, x, found);
        return found;
    }

    int less(ll x, bool equal = false) const
    {
        int p = root, answer = 0;
        while (p)
        {
            if (a[p].value < x || (equal && a[p].value == x))
            {
                answer += a[a[p].l].size + a[p].count;
                p = a[p].r;
            }
            else
                p = a[p].l;
        }
        return answer;
    }

    int rank(ll x) const { return less(x) + 1; }

    ll kth(int k) const
    {
        assert(1 <= k && k <= size());
        int p = root;
        while (true)
        {
            int left = a[a[p].l].size;
            if (k <= left)
                p = a[p].l;
            else if (k <= left + a[p].count)
                return a[p].value;
            else
            {
                k -= left + a[p].count;
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
