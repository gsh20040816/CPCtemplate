#include "../../src/compact/flow.hpp"

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int k, n;
    cin >> k >> n;
    int s = n + k + 1;
    int t = s + 1;
    Dinic g(t);
    long long need = 0;
    for (int v = 1; v <= k; v++)
    {
        long long c;
        cin >> c;
        need += min(c, 1LL * n + 1);
        g.add(n + v, t, c);
    }
    vector<vector<pair<int, int>>> ids(k + 1);
    for (int u = 1; u <= n; u++)
    {
        g.add(s, u, 1);
        int p;
        cin >> p;
        while (p--)
        {
            int v;
            cin >> v;
            int id = g.add(u, n + v, 1);
            ids[v].push_back({u, id});
        }
    }
    if (g.flow(s, t) != need)
    {
        cout << "No Solution!\n";
        return 0;
    }
    for (int v = 1; v <= k; v++)
    {
        cout << v << ':';
        for (auto [u, id] : ids[v])
            if (g.used(id))
                cout << ' ' << u;
        cout << '\n';
    }
}
