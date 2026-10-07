int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q;
    cin >> n >> m >> q;
    vector<vector<long long>> a(n, vector<long long>(m));
    for (auto &row : a)
    {
        for (auto &x : row) cin >> x;
    }
    StaticRMQ2D<long long> mn(a);
    StaticRMQ2D<long long, greater<long long>> mx(a);
    while (q--)
    {
        int x1, y1, x2, y2;
        cin >> x1 >> y1 >> x2 >> y2;
        auto [u, v] = mn.query(x1, y1, x2, y2);
        auto [s, t] = mx.query(x1, y1, x2, y2);
        cout << u << ' ' << v << ' ' << s << ' ' << t << '\n';
    }
}
