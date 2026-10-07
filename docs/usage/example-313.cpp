int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s;
    cin >> n >> m >> s;
    DenseDijkstra g(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        g.add(u, v, w);
    }
    g.run(s);
    for (int v = 1; v <= n; v++)
        if (g.dis[v] == DenseDijkstra::inf)
            cout << "INF\n";
        else
        {
            __int128 x = g.dis[v];
            string a;
            do
            {
                a += char('0' + x % 10);
                x /= 10;
            } while (x);
            reverse(a.begin(), a.end());
            cout << a;
            auto p = g.path(v);
            cout << ' ' << p.size();
            for (int u : p) cout << ' ' << u;
            cout << '\n';
        }
}
