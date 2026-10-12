#pragma once
#include <algorithm>
#include <array>
#include <cassert>
#include <vector>
using namespace std;

// Fixed rooted tree; growth may serve parent(x) or subtree(x), harvest subtree(x).
struct DynamicPeachTree
{
    using ll = long long;
    static constexpr ll INF = 1LL << 60;
    using State = array<ll, 4>;
    struct Matrix
    {
        array<State, 4> a;
        Matrix(bool identity = false)
        {
            for (int i = 0; i < 4; i++)
            {
                a[i].fill(INF);
                if (identity)
                    a[i][i] = 0;
            }
        }
    };
    struct Node
    {
        array<int, 2> ch{};
        int p = 0;
        ll b = 0, g = 0, h = 0;
        ll sumg = 0, sumh = 0, sumb = 0;
        Matrix mat, tot;
    };
    vector<Node> t;
    State ans{};
    ll budget = 0;

    static Matrix join(const Matrix &a, const Matrix &b)
    {
        Matrix c;
        for (int i = 0; i < 3; i++)
        {
            for (int j = 0; j < 3; j++)
                for (int k = 0; k < 4; k++)
                    if (a.a[i][j] != INF && b.a[j][k] != INF)
                        c.a[i][k] = min(c.a[i][k], a.a[i][j] + b.a[j][k]);
            c.a[i][3] = min(c.a[i][3], a.a[i][3]);
        }
        c.a[3][3] = 0;
        return c;
    }

    State get(int u) const
    {
        State a{};
        for (int i = 0; i < 3; i++)
            a[i] = *min_element(t[u].tot.a[i].begin(), t[u].tot.a[i].end());
        return a;
    }

    void pull(int u)
    {
        t[u].tot = join(join(t[t[u].ch[0]].tot, t[u].mat), t[t[u].ch[1]].tot);
    }

    void branch(int u, const State &a, int sign)
    {
        t[u].sumg += sign * a[0];
        t[u].sumh += sign * min({a[1], a[2], 0LL});
        t[u].sumb += sign * *min_element(a.begin(), a.end());
    }

    void update(int u)
    {
        auto &a = t[u];
        a.mat = Matrix();
        a.mat.a[0][0] = a.b + a.h - a.g + a.sumg;
        for (int j = 1; j < 4; j++)
            a.mat.a[1][j] = a.h + a.sumh;
        for (int j = 0; j < 4; j++)
            a.mat.a[2][j] = a.b + a.h + a.sumb;
        a.mat.a[3][3] = 0;
        pull(u);
    }

    int init(int u, const vector<vector<int>> &children)
    {
        int size = 1;
        for (int v : children[u])
        {
            size += init(v, children);
            branch(u, get(v), 1);
        }
        update(u);
        return size;
    }

    // 0-based parent, one -1 root. Nonnegative b; total b + all event counts <= 1e15.
    DynamicPeachTree(const vector<int> &parent, const vector<ll> &b)
        : t(parent.size() + 1)
    {
        int n = parent.size(), root = 0;
        assert(n > 0 && n <= 200000 && (int)b.size() == n);
        t[0].tot = Matrix(true);
        vector<vector<int>> children(n + 1);
        for (int i = 0; i < n; i++)
        {
            assert(b[i] >= 0 && b[i] <= 1000000000000000LL - budget);
            budget += b[i];
            t[i + 1].b = b[i];
            assert(parent[i] >= -1 && parent[i] < n && parent[i] != i);
            t[i + 1].p = parent[i] + 1;
            if (parent[i] == -1)
            {
                assert(root == 0);
                root = i + 1;
            }
            else
                children[parent[i] + 1].push_back(i + 1);
        }
        assert(root > 0);
        int size = init(root, children);
        assert(size == n);
        (void)size;
        ans = get(root);
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

    // type 1: growth, type 2: harvest. Returns feasibility of the whole prefix.
    bool add(int type, int x, ll value)
    {
        assert(type == 1 || type == 2);
        assert(x >= 0 && x + 1 < (int)t.size());
        assert(value >= 0 && value <= 1000000000000000LL - budget);
        budget += value;
        int u = x + 1;
        State old{};
        for (int i = u, q = 0; i; q = i, i = t[i].p)
        {
            splay(i);
            if (t[i].ch[1])
                branch(i, get(t[i].ch[1]), 1);
            t[i].ch[1] = q;
            if (q)
                branch(i, old, -1);
            else if (type == 1)
                t[i].g += value;
            else
                t[i].h += value;
            old = get(i);
            update(i);
        }
        splay(u);
        ans = get(u);
        return healthy();
    }

    bool healthy() const
    {
        return ans[0] == *min_element(ans.begin(), ans.end());
    }
};
