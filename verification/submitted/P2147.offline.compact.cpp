#include <bits/stdc++.h>
#include <cassert>
using namespace std;
struct RollbackDSU
{
    vector<int> fa, siz;
    vector<pair<int, int>> his;

    RollbackDSU(int n) : fa(n + 1), siz(n + 1, 1) { iota(fa.begin(), fa.end(), 0); }

    int find(int x) const
    {
        while (x != fa[x]) x = fa[x];
        return x;
    }

    int snapshot() const { return (int)his.size(); }

    bool merge(int x, int y)
    {
        x = find(x);
        y = find(y);
        if (x == y) return false;
        if (siz[x] < siz[y]) swap(x, y);
        his.push_back({y, siz[x]});
        fa[y] = x;
        siz[x] += siz[y];
        return true;
    }

    void rollback(int t)
    {
        assert(0 <= t && t <= snapshot());
        while (snapshot() > t)
        {
            auto [y, s] = his.back();
            his.pop_back();
            siz[fa[y]] = s;
            fa[y] = y;
        }
    }
};


struct TimeConnectivity
{
    int n, q;
    vector<vector<pair<int, int>>> edges;

    TimeConnectivity(int n, int q) : n(n), q(q), edges(4 * size_t(q) + 1)
    {
        assert(n >= 0 && n < INT_MAX && q >= 0 && q <= INT_MAX / 4);
    }

    // Edge (u,v) exists at times l <= t < r. Empty intervals are allowed.
    void add(int l, int r, int u, int v)
    {
        assert(0 <= l && l <= r && r <= q);
        assert(0 <= u && u <= n && 0 <= v && v <= n);
        if (l < r)
            insert(1, 0, q, l, r, {u, v});
    }

    template <class F> void run(F visit) const
    {
        RollbackDSU d(n);
        if (q > 0)
            dfs(1, 0, q, d, visit);
    }

private:
    void insert(int p, int l, int r, int a, int b, pair<int, int> e)
    {
        if (a <= l && r <= b)
        {
            edges[p].push_back(e);
            return;
        }
        int m = l + (r - l) / 2;
        if (a < m)
            insert(p * 2, l, m, a, b, e);
        if (m < b)
            insert(p * 2 + 1, m, r, a, b, e);
    }

    template <class F>
    void dfs(int p, int l, int r, RollbackDSU &d, F &visit) const
    {
        int saved = d.snapshot();
        for (auto [u, v] : edges[p])
            d.merge(u, v);
        if (r - l == 1)
            visit(l, static_cast<const RollbackDSU &>(d));
        else
        {
            int m = l + (r - l) / 2;
            dfs(p * 2, l, m, d, visit);
            dfs(p * 2 + 1, m, r, d, visit);
        }
        d.rollback(saved);
    }
};

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    TimeConnectivity graph(n, q);
    map<pair<int, int>, int> start;
    vector<pair<int, int>> ask(q, {-1, -1});
    for (int t = 0; t < q; ++t)
    {
        string op;
        int u, v;
        cin >> op >> u >> v;
        if (u > v)
            swap(u, v);
        pair<int, int> e = {u, v};
        if (op == "Connect")
            start[e] = t;
        else if (op == "Destroy")
        {
            auto it = start.find(e);
            graph.add(it->second, t, u, v);
            start.erase(it);
        }
        else
            ask[t] = e;
    }
    for (auto [e, t] : start)
        graph.add(t, q, e.first, e.second);
    graph.run([&](int t, const RollbackDSU &d)
    {
        auto [u, v] = ask[t];
        if (u != -1)
            cout << (d.find(u) == d.find(v) ? "Yes" : "No") << '\n';
    });
    return 0;
}
