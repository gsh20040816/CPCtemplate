#pragma once
#include <cassert>
#include <climits>
#include <optional>
#include <utility>
#include <vector>
using namespace std;

struct MergeSplay
{
    using ll = long long;
    struct Node
    {
        int ch[2]{}, fa = 0, siz = 1;
        ll val = 0;
    };
    int n;
    vector<Node> a;

    // Each original ID starts in its own singleton set.
    MergeSplay(const vector<ll> &v)
    {
        assert(v.size() < INT_MAX);
        n = v.size();
        a.resize(n + 1);
        a[0].siz = 0;
        for (int i = 0; i < n; i++) a[i + 1].val = v[i];
    }

    void pull(int x)
    {
        a[x].siz = a[a[x].ch[0]].siz + a[a[x].ch[1]].siz + 1;
    }

    bool less(int x, int y) const
    {
        return pair{a[x].val, x} < pair{a[y].val, y};
    }

    void rotate(int x)
    {
        int y = a[x].fa, z = a[y].fa;
        int k = a[y].ch[1] == x, w = a[x].ch[k ^ 1];
        if (z) a[z].ch[a[z].ch[1] == y] = x;
        a[x].fa = z;
        a[y].ch[k] = w;
        if (w) a[w].fa = y;
        a[x].ch[k ^ 1] = y;
        a[y].fa = x;
        pull(y);
        pull(x);
    }

    void splay(int x)
    {
        while (a[x].fa)
        {
            int y = a[x].fa, z = a[y].fa;
            if (z)
            {
                bool same = (a[y].ch[1] == x) == (a[z].ch[1] == y);
                rotate(same ? y : x);
            }
            rotate(x);
        }
    }

    int expose(int id)
    {
        assert(0 <= id && id < n);
        int x = id + 1;
        splay(x);
        return x;
    }

    int insert(int root, int x)
    {
        if (!root) return x;
        int u = root;
        while (true)
        {
            int k = less(u, x);
            if (!a[u].ch[k])
            {
                a[u].ch[k] = x;
                a[x].fa = u;
                break;
            }
            u = a[u].ch[k];
        }
        splay(x);
        return x;
    }

    void transfer(int u, int &root)
    {
        if (!u) return;
        int l = a[u].ch[0], r = a[u].ch[1];
        a[u] = Node{{0, 0}, 0, 1, a[u].val};
        root = insert(root, u);
        transfer(l, root);
        transfer(r, root);
    }

    bool same(int u, int v)
    {
        int x = expose(u), y = expose(v);
        return x == y || a[x].fa != 0;
    }

    bool merge(int u, int v)
    {
        int x = expose(u), y = expose(v);
        if (x == y || a[x].fa) return false;
        if (a[x].siz < a[y].siz) swap(x, y);
        transfer(y, x);
        return true;
    }

    int size(int id)
    {
        return a[expose(id)].siz;
    }

    ll value(int id) const
    {
        assert(0 <= id && id < n);
        return a[id + 1].val;
    }

    // Change this element's value; its ID and set membership do not change.
    void set(int id, ll val)
    {
        int x = expose(id);
        int l = a[x].ch[0], r = a[x].ch[1];
        if (l) a[l].fa = 0;
        if (r) a[r].fa = 0;
        int root = r;
        if (l)
        {
            root = l;
            while (a[root].ch[1]) root = a[root].ch[1];
            splay(root);
            a[root].ch[1] = r;
            if (r) a[r].fa = root;
            pull(root);
        }
        a[x] = Node{{0, 0}, 0, 1, val};
        insert(root, x);
    }

    // 1-based rank among (value, original ID) in this element's set.
    int rank(int id)
    {
        int x = expose(id);
        return a[a[x].ch[0]].siz + 1;
    }

    // Return an original ID, not its value. Invalid k returns nullopt.
    optional<int> kth(int id, ll k)
    {
        int x = expose(id);
        if (k <= 0 || k > a[x].siz) return nullopt;
        while (true)
        {
            int l = a[a[x].ch[0]].siz;
            if (k == l + 1)
            {
                splay(x);
                return x - 1;
            }
            if (k <= l) x = a[x].ch[0];
            else
            {
                k -= l + 1;
                x = a[x].ch[1];
            }
        }
    }
};
