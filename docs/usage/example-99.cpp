int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, s, t;
    cin >> n >> m >> s >> t;
    BoundedMaxFlow g(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long lo, hi;
        cin >> u >> v >> lo >> hi;
        g.add(u, v, lo, hi);
    }
    auto ans = g.minimum(s, t);
    if (!ans)
        cout << "NO\n";
    else
    {
        cout << "YES " << *ans << '\n';
        for (int i = 0; i < m; i++) cout << g.used(i) << '\n';
    }
}
