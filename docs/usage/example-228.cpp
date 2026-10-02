int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    if (!(cin >> n) || n < 0 || n > 200000) return 1;
    using P = RealPlane::Point;
    vector<pair<P, int>> points(n);
    for (int i = 0; i < n; i++)
    {
        auto &p = points[i].first;
        if (!(cin >> p.x >> p.y) || !isfinite(p.x) || !isfinite(p.y)) return 1;
        points[i].second = i + 1;
    }
    RealPolarLess less;
    sort(points.begin(), points.end(), [&](const auto &a, const auto &b)
    {
        return less(a.first, b.first) ||
               (!less(b.first, a.first) && a.second < b.second);
    });
    for (const auto &p : points) cout << p.second << ' ';
    cout << '\n';
}
