int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q;
    cin >> n >> m >> q;
    vector<IntegerPlane::Point> a(n), b(m);
    for (auto &v : a) cin >> v.x >> v.y;
    for (auto &v : b)
    {
        cin >> v.x >> v.y;
        v.x = -v.x;
        v.y = -v.y;
    }
    auto p = minkowski_sum(integer_hull(a), integer_hull(b));
    while (q--)
    {
        IntegerPlane::Point v;
        cin >> v.x >> v.y;
        cout << (convex_contains_i64(p, v) != 0) << '\n';
    }
}
