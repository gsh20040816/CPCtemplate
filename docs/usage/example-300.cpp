int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    TarjanSCC t(n);
    vector<array<int, 3>> e;
    auto add = [&](int u, int v, int w)
    {
        t.add(u, v);
        e.push_back({u, v, w});
    };
    while (m--)
    {
        int op, a, b;
        cin >> op >> a >> b;
        if (op == 1)
        {
            add(a, b, 0);
            add(b, a, 0);
        }
        else if (op == 2) add(a, b, 1);
        else if (op == 3) add(b, a, 0);
        else if (op == 4) add(b, a, 1);
        else add(a, b, 0);
    }
    t.run();
    vector<vector<pair<int, int>>> g(t.cnt + 1);
    for (auto [u, v, w] : e)
    {
        int a = t.bel[u], b = t.bel[v];
        if (a == b)
        {
            if (w)
            {
                cout << -1 << '\n';
                return 0;
            }
        }
        else g[a].push_back({b, w});
    }
    vector<int> dis(t.cnt + 1, 1);
    for (int u = t.cnt; u >= 1; u--)
        for (auto [v, w] : g[u])
            dis[v] = max(dis[v], dis[u] + w);
    long long sum = 0;
    for (int u = 1; u <= n; u++) sum += dis[t.bel[u]];
    cout << sum << '\n';
    return 0;
}
