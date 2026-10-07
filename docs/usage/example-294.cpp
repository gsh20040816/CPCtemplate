int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    BellmanFord t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    if (t.run(0)) cout << "NO\n";
    else
    {
        cout << "YES\n" << t.e[t.cycle[0]].u;
        for (int id : t.cycle) cout << ' ' << t.e[id].v;
        cout << '\n';
    }
}
