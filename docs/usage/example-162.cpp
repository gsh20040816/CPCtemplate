int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    BiconnectedCore g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        cin >> u >> v;
        g.add(u + 1, v + 1);
    }
    g.run();
    auto [before, after] = removal_components(g);
    for (int u = 1; u <= n; u++)
        if (after[u] > before) cout << u - 1 << '\n';
}
