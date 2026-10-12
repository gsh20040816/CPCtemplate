int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<long double> c(n), b(m);
    vector<vector<long double>> a(m, vector<long double>(n));
    for (auto &v : c) cin >> v;
    for (int i = 0; i < m; i++)
    {
        for (auto &v : a[i]) cin >> v;
        cin >> b[i];
    }
    Simplex lp(a, b, c);
    auto result = lp.solve();
    if (result.status == Simplex::infeasible) cout << "Infeasible\n";
    else if (result.status == Simplex::unbounded) cout << "Unbounded\n";
    else
    {
        cout << fixed << setprecision(12) << result.value << '\n';
        for (auto x : result.x) cout << x << ' ';
        cout << '\n';
    }
}
