int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<IntegerPlane::Point> points(n);
    for (auto &p : points) cin >> p.x >> p.y;
    auto answer = closest_pair_i64(points);
    cout << (long long)*answer << '\n';
}
