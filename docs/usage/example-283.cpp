int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        LiftingLCA h(n);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            long long w;
            cin >> u >> v >> w;
            h.add(u, v, w);
        }
        h.build();
        vector<long long> d(n + 1);
        auto dfs = [&](auto &&self, int u, int p) -> void
        {
            for (auto [v, w] : h.g[u])
            {
                if (v == p) continue;
                d[v] = d[u] + w;
                self(self, v, u);
            }
        };
        dfs(dfs, 1, 0);
        string cmd;
        while (cin >> cmd && cmd != "DONE")
        {
            int u, v;
            cin >> u >> v;
            int p = h.lca(u, v);
            if (cmd == "DIST") cout << (d[u] - d[p]) + (d[v] - d[p]) << '\n';
            else
            {
                int k;
                cin >> k;
                int a = h.depth[u] - h.depth[p];
                int b = h.depth[v] - h.depth[p];
                int ans = k <= a + 1 ? h.jump(u, k - 1) : h.jump(v, a + b + 1 - k);
                cout << ans << '\n';
            }
        }
        cout << '\n';
    }
}
