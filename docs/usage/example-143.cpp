int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int m, n;
    cin >> m >> n;
    vector<string> a(m);
    for (auto &s : a) cin >> s;
    string b;
    cin >> b;
    for (int i = 0; i < m; i++) a[i] += b[i];
    auto sol = GaussXor::solve(a, n);
    if (!sol.consistent)
    {
        cout << -1 << '\n';
        return 0;
    }
    cout << sol.kernel.size() << '\n';
    cout << sol.particular << '\n';
    for (auto &v : sol.kernel) cout << v << '\n';
}
