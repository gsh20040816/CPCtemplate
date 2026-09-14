int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    Johnson graph(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        graph.add(u, v, w);
    }
    if (!graph.build())
    {
        cout << -1 << '\n';
        return 0;
    }
    for (int s = 1; s <= n; s++)
    {
        auto d = graph.distances(s);
        Johnson::I answer = 0;
        for (int v = 1; v <= n; v++)
            answer += v * (d[v] == Johnson::inf ? 1000000000 : d[v]);
        cout << (long long)answer << '\n';
    }
}
