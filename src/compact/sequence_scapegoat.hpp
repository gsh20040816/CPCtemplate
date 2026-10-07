#pragma once
#include <algorithm>
#include <cassert>
#include <map>
#include <vector>
using namespace std;

struct SequenceScapegoat
{
    using ll = long long;

    struct Node
    {
        int l = 0, r = 0, sz = 0, cnt = 0;
        ll val = 0;
        bool live = false;
        map<ll, int> freq;
    };

    vector<Node> a{Node{}};
    vector<int> spare;
    int root = 0;

    SequenceScapegoat(const vector<ll> &v = {})
    {
        vector<int> ids;
        for (ll x : v)
            ids.push_back(make(x));
        root = build(ids, 0, (int)ids.size());
    }

    int size() const
    {
        return a[root].sz;
    }

    int make(ll x)
    {
        int u;
        if (spare.empty())
        {
            u = (int)a.size();
            a.push_back(Node{});
        }
        else
        {
            u = spare.back();
            spare.pop_back();
        }
        a[u].sz = 1;
        a[u].cnt = 1;
        a[u].val = x;
        a[u].live = true;
        a[u].freq[x] = 1;
        return u;
    }

    void change(int u, ll x, int d)
    {
        int &v = a[u].freq[x];
        v += d;
        if (v == 0)
            a[u].freq.erase(x);
    }

    void pull(int u)
    {
        int l = a[u].l;
        int r = a[u].r;
        a[u].sz = a[l].sz + a[r].sz + a[u].live;
        a[u].cnt = a[l].cnt + a[r].cnt + 1;
        a[u].freq.clear();
        if (a[u].live)
            a[u].freq[a[u].val] = 1;
        for (auto [x, c] : a[l].freq)
            a[u].freq[x] += c;
        for (auto [x, c] : a[r].freq)
            a[u].freq[x] += c;
    }

    void collect(int u, vector<int> &v)
    {
        if (!u)
            return;
        collect(a[u].l, v);
        if (a[u].live)
            v.push_back(u);
        collect(a[u].r, v);
        if (!a[u].live)
        {
            a[u] = Node{};
            spare.push_back(u);
        }
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

    int balance(int u)
    {
        int heavy = max(a[a[u].l].cnt, a[a[u].r].cnt);
        if (4LL * heavy <= 3LL * a[u].cnt && 2LL * a[u].sz >= a[u].cnt)
            return u;
        vector<int> v;
        v.reserve(a[u].sz);
        collect(u, v);
        return build(v, 0, (int)v.size());
    }

    int insert(int u, int k, ll x)
    {
        if (!u)
            return make(x);
        int left = a[a[u].l].sz;
        if (k <= left)
            a[u].l = insert(a[u].l, k, x);
        else
            a[u].r = insert(a[u].r, k - left - a[u].live, x);
        a[u].sz++;
        a[u].cnt = a[a[u].l].cnt + a[a[u].r].cnt + 1;
        change(u, x, 1);
        return balance(u);
    }

    void insert(int k, ll x)
    {
        assert(0 <= k && k <= size());
        root = insert(root, k, x);
    }

    int erase(int u, int k, ll &x)
    {
        int left = a[a[u].l].sz;
        if (k <= left)
            a[u].l = erase(a[u].l, k, x);
        else if (a[u].live && k == left + 1)
        {
            x = a[u].val;
            a[u].live = false;
        }
        else
            a[u].r = erase(a[u].r, k - left - a[u].live, x);
        a[u].sz--;
        a[u].cnt = a[a[u].l].cnt + a[a[u].r].cnt + 1;
        change(u, x, -1);
        return balance(u);
    }

    ll erase(int k)
    {
        assert(1 <= k && k <= size());
        ll x = 0;
        root = erase(root, k, x);
        return x;
    }

    int count(int u, int l, int r, ll x) const
    {
        if (!u || l > r)
            return 0;
        if (l <= 1 && a[u].sz <= r)
        {
            auto it = a[u].freq.find(x);
            return it == a[u].freq.end() ? 0 : it->second;
        }
        int left = a[a[u].l].sz;
        int ans = 0;
        if (l <= left)
            ans += count(a[u].l, l, r, x);
        if (a[u].live && l <= left + 1 && left + 1 <= r && a[u].val == x)
            ans++;
        int offset = left + a[u].live;
        if (r > offset)
            ans += count(a[u].r, l - offset, r - offset, x);
        return ans;
    }

    int count(int l, int r, ll x) const
    {
        assert(1 <= l && l <= r && r <= size());
        return count(root, l, r, x);
    }

    void rotate(int l, int r)
    {
        assert(1 <= l && l <= r && r <= size());
        ll x = erase(r);
        insert(l - 1, x);
    }
};
