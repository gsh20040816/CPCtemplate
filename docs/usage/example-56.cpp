int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    vector<tuple<int, int, long long>> edges;
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        scanf("%d%d%lld", &u, &v, &w);
        edges.push_back({u, v, w});
    }
    auto tree = gomory_hu(n + 1, edges);
    vector<vector<pair<int, long long>>> g(n + 1);
    for (auto [u, v, w] : tree)
    {
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }
    int q;
    scanf("%d", &q);
    while (q--)
    {
        int u, v;
        scanf("%d%d", &u, &v);
        // Minimum cut = minimum edge on the tree path.
        long long answer = LLONG_MAX;
        auto dfs = [&](auto &&self, int x, int parent, long long value) -> void
        {
            if (x == v) answer = value;
            for (auto [y, w] : g[x])
                if (y != parent) self(self, y, x, min(value, w));
        };
        dfs(dfs, u, -1, LLONG_MAX);
        printf("%lld\n", answer);
    }
    return 0;
}
