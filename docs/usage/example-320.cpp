int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    Dinic g(n);
    vector<int> ids;
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long c;
        cin >> u >> v >> c;
        ids.push_back(g.add(u, v, c));
    }
    cout << g.flow(s, t) << '\n';
    cout << (flow_unique(g) ? "UNIQUE" : "MULTIPLE") << '\n';
    for (int id : ids)
        cout << g.used(id) << '\n';
}
