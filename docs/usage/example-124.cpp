int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<IntegerPlane::Point> p(n);
    for (auto &v : p) cin >> v.x >> v.y;
    auto h = integer_hull(move(p));
    cout << (long long)convex_diameter2(h) << '\n';
}
