int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n + 1);
    for (int u = 1; u <= n; u++) cin >> a[u];
    TreeBlockDistinct g(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        g.add(u, v);
    }
    g.build(a);
    int last = 0;
    while (q--)
    {
        int u, v;
        cin >> u >> v;
        u ^= last;
        last = g.query(u, v);
        cout << last << '\n';
    }
}
