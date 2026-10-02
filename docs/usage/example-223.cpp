int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    unsigned long long k;
    if (!(cin >> n >> m >> k)) return 0;
    MaxPlusMatrix a(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long c;
        cin >> u >> v >> c;
        --u, --v;
        a.a[u][v] = max(a.a[u][v], -MaxPlusMatrix::I(c));
    }
    auto r = a.power(k);
    auto x = r.a[0][n - 1];
    // Official bounds imply each finite answer is in [1, 10^18].
    if (x == MaxPlusMatrix::neg) cout << -1 << '\n';
    else cout << (long long)(-x) << '\n';
}
