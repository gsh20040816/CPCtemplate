int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    DenseDijkstra g(n);
    for (int i = 0; i < n; i++)
    {
        int u, k;
        cin >> u >> k;
        while (k--)
        {
            int v;
            long long w;
            cin >> v >> w;
            g.add(u + 1, v + 1, w);
        }
    }
    g.run(1);
    for (int u = 1; u <= n; u++)
    {
        cout << u - 1 << ' ' << (long long)g.dis[u] << '\n';
    }
}
