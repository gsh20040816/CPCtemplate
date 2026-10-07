int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    AssignmentSpectrum matching(n, n);
    while (m--)
    {
        int x, y;
        long long w;
        cin >> x >> y >> w;
        matching.add(x - 1, y - 1, w);
    }
    matching.solve();
    cout << (long long)matching.best[n] << '\n';
    for (int x : matching.r)
        cout << x + 1 << ' ';
    cout << '\n';
    return 0;
}
