#include "../../src/compact/flow.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, e;
    cin >> n >> m >> e;
    int s = n + m + 1;
    int t = s + 1;
    Dinic g(t);
    for (int u = 0; u < n; u++)
        g.add(s, u + 1, 1);
    for (int v = 0; v < m; v++)
    {
        long long c;
        cin >> c;
        g.add(n + v + 1, t, c);
    }
    vector<array<int, 3>> edges;
    for (int i = 0; i < e; i++)
    {
        int u, v;
        cin >> u >> v;
        int id = g.add(u + 1, n + v + 1, 1);
        edges.push_back({u, v, id});
    }
    cout << g.flow(s, t) << '\n';
    for (auto [u, v, id] : edges)
        if (g.used(id))
            cout << u << ' ' << v << '\n';
}
