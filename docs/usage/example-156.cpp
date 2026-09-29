int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    IntegerPlane::Point a, b;
    long long r, s;
    cin >> a.x >> a.y >> r >> b.x >> b.y >> s;
    auto ans = IntegerTangents::solve(a, r, b, s);
    cout << fixed << setprecision(12);
    for (auto line : ans.lines) cout << line.a.x << ' ' << line.a.y << '\n';
}
