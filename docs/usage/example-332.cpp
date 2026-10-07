int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, e, limit;
    cin >> n >> m >> e >> limit;
    AssignmentSpectrum matching(n, m);
    while (e--)
    {
        int x, y;
        long long w;
        cin >> x >> y >> w;
        matching.add(x, y, w);
    }
    int k = matching.solve(limit);
    // 本演示限定 n,m<=1000，边权绝对值<=10^9，可安全转 long long。
    cout << k << '\n';
    for (auto value : matching.best)
        cout << (long long)value << ' ';
    cout << '\n';
    for (int y : matching.l)
        cout << y << ' ';
    cout << '\n';
    cout << (long long)matching.level << '\n';
    for (auto value : matching.lx)
        cout << (long long)value << ' ';
    cout << '\n';
    for (auto value : matching.ly)
        cout << (long long)value << ' ';
    cout << '\n';
    return 0;
}
