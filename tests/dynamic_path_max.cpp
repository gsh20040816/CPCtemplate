#include "../src/compact/dynamic_path_max.hpp"
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void require(bool ok)
{
    if (!ok)
        throw runtime_error("DynamicPathMax mismatch");
}

struct Oracle
{
    vector<vector<int>> g;
    vector<ll> v;

    Oracle(const vector<ll> &values) : g(values.size()), v(values)
    {
    }

    vector<int> path(int x, int y) const
    {
        vector<int> p(v.size(), -1);
        queue<int> q;
        p[x] = x;
        q.push(x);
        while (!q.empty())
        {
            int u = q.front();
            q.pop();
            for (int w : g[u])
                if (p[w] == -1)
                {
                    p[w] = u;
                    q.push(w);
                }
        }
        if (p[y] == -1)
            return {};
        vector<int> ans{y};
        while (y != x)
        {
            y = p[y];
            ans.push_back(y);
        }
        reverse(ans.begin(), ans.end());
        return ans;
    }

    bool link(int x, int y)
    {
        if (!path(x, y).empty())
            return false;
        g[x].push_back(y);
        g[y].push_back(x);
        return true;
    }

    bool cut(int x, int y)
    {
        auto it = find(g[x].begin(), g[x].end(), y);
        if (it == g[x].end())
            return false;
        g[x].erase(it);
        g[y].erase(find(g[y].begin(), g[y].end(), x));
        return true;
    }

    bool cut_parent(int root, int x)
    {
        auto p = path(root, x);
        if (p.size() < 2)
            return false;
        return cut(p[p.size() - 2], x);
    }

    bool add(int x, int y, ll w)
    {
        auto p = path(x, y);
        for (int u : p)
            v[u] += w;
        return !p.empty();
    }

    optional<ll> query(int x, int y) const
    {
        auto p = path(x, y);
        if (p.empty())
            return nullopt;
        ll ans = LLONG_MIN;
        for (int u : p)
            ans = max(ans, v[u]);
        return ans;
    }
};

void check(DynamicPathMax &t, const Oracle &o)
{
    for (int x = 0; x < (int)o.v.size(); x++)
        for (int y = 0; y < (int)o.v.size(); y++)
            require(t.query(x + 1, y + 1) == o.query(x, y));
    require(t.a[0].fa == 0 && t.a[0].add == 0 && !t.a[0].rev);
}

int main()
{
    int forests = 0, states = 0, transitions = 0;
    for (int n = 1; n <= 4; n++)
    {
        vector<pair<int, int>> edges;
        for (int x = 0; x < n; x++)
            for (int y = x + 1; y < n; y++)
                edges.push_back({x, y});
        for (int mask = 0; mask < (1 << edges.size()); mask++)
        {
            Oracle base(vector<ll>(n, 0));
            bool forest = true;
            for (int j = 0; j < (int)edges.size(); j++)
                if (mask >> j & 1)
                    forest &= base.link(edges[j].first, edges[j].second);
            if (!forest)
                continue;
            forests++;
            for (int bits = 0; bits < (1 << n); bits++)
            {
                auto o = base;
                for (int i = 0; i < n; i++)
                    o.v[i] = bits >> i & 1 ? 7 : -7;
                DynamicPathMax t(o.v);
                for (int j = 0; j < (int)edges.size(); j++)
                    if (mask >> j & 1)
                        require(t.link(edges[j].first + 1, edges[j].second + 1));
                states++;
                check(t, o);
                for (int x = 0; x < n; x++)
                    for (int y = 0; y < n; y++)
                        for (int op = 0; op < 4; op++)
                        {
                            auto u = t;
                            auto p = o;
                            bool a, b;
                            if (op == 0)
                            {
                                a = u.link(x + 1, y + 1);
                                b = p.link(x, y);
                            }
                            else if (op == 1)
                            {
                                a = u.cut(x + 1, y + 1);
                                b = p.cut(x, y);
                            }
                            else if (op == 2)
                            {
                                a = u.cut_parent(x + 1, y + 1);
                                b = p.cut_parent(x, y);
                            }
                            else
                            {
                                a = u.add(x + 1, y + 1, -19);
                                b = p.add(x, y, -19);
                            }
                            require(a == b);
                            check(u, p);
                            transitions++;
                        }
            }
        }
    }
    mt19937 rng(40102026);
    for (int trial = 0; trial < 30; trial++)
    {
        int n = 2 + rng() % 39;
        vector<ll> v(n);
        for (auto &x : v)
            x = (ll)(rng() % 1000) - 2000;
        Oracle o(v);
        DynamicPathMax t(v);
        for (int i = 1; i < n; i++)
        {
            int p = rng() % i;
            require(t.link(i + 1, p + 1) == o.link(i, p));
        }
        for (int i = 0; i < 1000; i++)
        {
            int x = rng() % n, y = rng() % n, op = rng() % 6;
            ll w = (ll)(rng() % 1000) - 500;
            if (op == 0)
                require(t.link(x + 1, y + 1) == o.link(x, y));
            if (op == 1)
                require(t.cut(x + 1, y + 1) == o.cut(x, y));
            if (op == 2)
                require(t.cut_parent(x + 1, y + 1) == o.cut_parent(x, y));
            if (op == 3)
                require(t.add(x + 1, y + 1, w) == o.add(x, y, w));
            if (op == 4)
                require(t.query(x + 1, y + 1) == o.query(x, y));
            if (op == 5)
                t.make_root(x + 1);
            if (i % 50 == 0)
                check(t, o);
        }
        check(t, o);
    }
    DynamicPathMax extreme({LLONG_MIN, LLONG_MAX});
    require(extreme.link(1, 2));
    require(extreme.query(1, 1) == LLONG_MIN);
    require(extreme.query(2, 1) == LLONG_MAX);
    require(extreme.add(1, 1, 1));
    require(extreme.add(2, 2, -1));
    require(extreme.query(1, 1) == LLONG_MIN + 1);
    require(extreme.query(1, 2) == LLONG_MAX - 1);
    int n = 100000;
    DynamicPathMax chain(vector<ll>(n, -1000000000000LL));
    for (int i = 1; i < n; i++)
        require(chain.link(i, i + 1));
    require(chain.add(1, n, 17));
    for (int i = 0; i < 1000; i++)
    {
        require(chain.query(n, 1) == -999999999983LL);
        require(chain.cut_parent(1, n));
        require(!chain.query(1, n));
        require(chain.link(n, n - 1));
        require(chain.cut(1, 2));
        require(!chain.add(1, n, 1));
        require(chain.link(1, 2));
    }
    cout << forests << ' ' << states << ' ' << transitions << " 30000 100000 PASS\n";
    return 0;
}
