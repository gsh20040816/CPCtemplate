int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using H = IntegerHalfplanes;
    int n;
    cin >> n;
    vector<H::Line> lines;
    while (n--)
    {
        int m;
        cin >> m;
        vector<pair<long long, long long>> p(m);
        for (auto &[x, y] : p) cin >> x >> y;
        for (int i = 0; i < m; i++)
        {
            auto [x, y] = p[i];
            auto [u, v] = p[(i + 1) % m];
            long long a = v - y, b = x - u;
            lines.push_back({a, b, a * x + b * y});
        }
    }
    auto p = H::bounded_polygon(move(lines));
    long double area2 = 0;
    for (int i = 0; i < (int)p.size(); i++)
    {
        auto u = p[i], v = p[(i + 1) % p.size()];
        H::I numerator = H::I(u.x) * v.y - H::I(u.y) * v.x;
        H::I denominator = H::I(u.d) * v.d;
        area2 += (long double)numerator / (long double)denominator;
    }
    cout << fixed << setprecision(3) << fabsl(area2) / 2 << '\n';
}
