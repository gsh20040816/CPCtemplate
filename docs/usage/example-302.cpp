int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    DagLongest t(n);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        t.add(u, v, 1);
    }
    t.run(1);
    if (t.dis[n] == -DagLongest::inf)
    {
        cout << "IMPOSSIBLE\n";
        return 0;
    }
    auto p = t.path(n);
    cout << p.size() + 1 << '\n';
    cout << 1;
    for (int id : p) cout << ' ' << t.e[id].v;
    cout << '\n';
}
