int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<int> type(q + 1), u(q + 1), v(q + 1), ans(q + 1);
    vector<vector<int>> g(q + 1);
    for (int i = 1; i <= q; i++)
    {
        int k;
        cin >> type[i] >> k >> u[i] >> v[i];
        g[k + 1].push_back(i);
    }
    RollbackDSU d(n);
    auto dfs = [&](auto &&self, int x) -> void
    {
        int t = d.snapshot();
        if (x)
        {
            if (type[x] == 0)
                d.merge(u[x], v[x]);
            else
                ans[x] = d.find(u[x]) == d.find(v[x]);
        }
        for (int y : g[x]) self(self, y);
        d.rollback(t);
    };
    dfs(dfs, 0);
    for (int i = 1; i <= q; i++)
        if (type[i] == 1) cout << ans[i] << '\n';
}
