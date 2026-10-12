#pragma once
#include <array>
#include <cassert>
#include <vector>
using namespace std;

struct XorPathSum
{
    using ll = long long;
    static constexpr int B = 27;
    struct Info
    {
        array<array<int, 2>, B> up{}, down{};
        int path = 0;
        ll sum = 0;
    };
    struct Node
    {
        array<int, 2> ch{};
        int p = 0;
        Info val, tot;
        array<array<int, 2>, B> cnt{};
        array<array<ll, 2>, B> pairs{};
        ll sum = 0;
    };
    vector<Node> t;
    ll ans = 0;

    static Info join(const Info &a, const Info &b)
    {
        Info c;
        c.path = a.path ^ b.path;
        c.sum = a.sum + b.sum;
        for (int i = 0; i < B; i++)
            for (int j = 0; j < 2; j++)
            {
                c.sum += (1LL << i) * a.down[i][j] * b.up[i][j ^ 1];
                c.up[i][j] = a.up[i][j] + b.up[i][j ^ (a.path >> i & 1)];
                c.down[i][j] = b.down[i][j] + a.down[i][j ^ (b.path >> i & 1)];
            }
        return c;
    }

    void pull(int u)
    {
        t[u].tot = join(join(t[t[u].ch[0]].tot, t[u].val), t[t[u].ch[1]].tot);
    }

    // sign = +1 adds a virtual child; -1 removes its old aggregate.
    void branch(int u, const Info &s, int sign)
    {
        auto &a = t[u];
        for (int i = 0; i < B; i++)
        {
            if (sign < 0)
                for (int j = 0; j < 2; j++)
                    a.cnt[i][j] -= s.up[i][j];
            for (int x = 0; x < 2; x++)
            {
                ll ways = s.up[i][1 ^ x];
                for (int j = 0; j < 2; j++)
                    ways += 1LL * a.cnt[i][j] * s.up[i][j ^ 1 ^ x];
                a.pairs[i][x] += sign * ways;
            }
            if (sign > 0)
                for (int j = 0; j < 2; j++)
                    a.cnt[i][j] += s.up[i][j];
        }
        a.sum += sign * s.sum;
    }

    void update(int u)
    {
        auto &a = t[u];
        a.val.sum = a.val.path + a.sum;
        for (int i = 0; i < B; i++)
        {
            int bit = a.val.path >> i & 1;
            a.val.sum += (1LL << i) * a.pairs[i][bit];
            for (int j = 0; j < 2; j++)
            {
                a.val.up[i][j] = a.cnt[i][j ^ bit];
                a.val.down[i][j] = a.cnt[i][j ^ bit];
            }
            a.val.up[i][bit]++;
            a.val.down[i][bit]++;
        }
        pull(u);
    }

    int init(int u, const vector<vector<int>> &g)
    {
        int size = 1;
        for (int v : g[u])
        {
            size += init(v, g);
            branch(u, t[v].tot, 1);
        }
        update(u);
        return size;
    }

    // parent/value are 0-based; exactly one parent is -1, topology stays fixed.
    XorPathSum(const vector<int> &parent, const vector<int> &value)
        : t(parent.size() + 1)
    {
        int n = parent.size();
        assert(n > 0 && n <= 200000 && (int)value.size() == n);
        vector<vector<int>> g(n + 1);
        int root = 0;
        for (int i = 0; i < n; i++)
        {
            assert(value[i] >= 0 && value[i] < (1 << B));
            assert(parent[i] >= -1 && parent[i] < n && parent[i] != i);
            t[i + 1].val.path = value[i];
            t[i + 1].p = parent[i] + 1;
            if (parent[i] == -1)
            {
                assert(root == 0);
                root = i + 1;
            }
            else
                g[parent[i] + 1].push_back(i + 1);
        }
        assert(root > 0);
        int size = init(root, g);
        assert(size == n);
        (void)size;
        ans = t[root].tot.sum;
    }

    bool isroot(int u) const
    {
        int p = t[u].p;
        return t[p].ch[0] != u && t[p].ch[1] != u;
    }

    void rotate(int u)
    {
        int p = t[u].p, q = t[p].p;
        int k = t[p].ch[1] == u;
        int v = t[u].ch[k ^ 1];
        if (!isroot(p))
            t[q].ch[t[q].ch[1] == p] = u;
        t[u].p = q;
        t[p].ch[k] = v;
        if (v)
            t[v].p = p;
        t[u].ch[k ^ 1] = p;
        t[p].p = u;
        pull(p);
    }

    void splay(int u)
    {
        while (!isroot(u))
        {
            int p = t[u].p, q = t[p].p;
            if (!isroot(p))
                rotate((t[p].ch[1] == u) == (t[q].ch[1] == p) ? p : u);
            rotate(u);
        }
        pull(u);
    }

    ll set(int x, int value)
    {
        assert(x >= 0 && x + 1 < (int)t.size());
        assert(value >= 0 && value < (1 << B));
        int u = x + 1;
        Info old;
        for (int i = u, q = 0; i; q = i, i = t[i].p)
        {
            splay(i);
            if (t[i].ch[1])
                branch(i, t[t[i].ch[1]].tot, 1);
            t[i].ch[1] = q;
            if (q)
                branch(i, old, -1);
            else
                t[i].val.path = value;
            old = t[i].tot;
            update(i);
        }
        splay(u);
        ans = t[u].tot.sum;
        return ans;
    }

    ll sum() const
    {
        return ans;
    }
};
