int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    ShortestPathTree t(n);
    while (m--)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    int s;
    cin >> s;
    t.run(s);
    cout << (long long)t.weight << '\n';
    for (int id : t.ids) cout << id + 1 << ' ';
    cout << '\n';
}
