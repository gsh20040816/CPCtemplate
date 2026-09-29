int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    BiconnectedCore graph(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        cin >> u >> v;
        graph.add(u, v);
    }
    graph.run();
    auto tree = block_cut_forest(graph);
    vector<int> sz(tree.size());
    auto dfs = [&](auto &&self, int u, int p) -> void
    {
        sz[u] = (u <= n);
        for (int v : tree[u])
        {
            if (v == p) continue;
            self(self, v, u);
            sz[u] += sz[v];
        }
    };
    long long ans = 0;
    auto calc = [&](auto &&self, int u, int p, int total) -> void
    {
        long long sum = total - sz[u];
        long long cnt = u <= n ? 2LL * (total - 1) : 0;
        for (int v : tree[u])
        {
            if (v == p) continue;
            cnt += 2 * sum * sz[v];
            sum += sz[v];
            self(self, v, u, total);
        }
        long long w = u <= n ? -1 : (int)tree[u].size();
        ans += w * cnt;
    };
    for (int u = 1; u <= n; u++)
    {
        if (sz[u]) continue;
        dfs(dfs, u, 0);
        calc(calc, u, 0, sz[u]);
    }
    cout << ans << '\n';
    return 0;
}
