int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, queries;
    cin >> n;
    vector<RealPlane::Point> p(n);
    for (auto &v : p)
        cin >> v.x >> v.y;
    cin >> queries;
    while (queries--)
    {
        RealPlane::Point a, b;
        cin >> a.x >> a.y >> b.x >> b.y;
        auto q = convex_cut(p, a, b);
        long double area = 0;
        long double error = 0;
        for (int i = 1; i + 1 < (int)q.size(); i++)
        {
            auto value = RealPlane::cross(q[i] - q[0], q[i + 1] - q[0]);
            auto y = value - error;
            auto next = area + y;
            error = (next - area) - y;
            area = next;
        }
        cout << fixed << setprecision(12) << abs(area) / 2 << '\n';
    }
}
