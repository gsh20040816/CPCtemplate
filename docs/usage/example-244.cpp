int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> rows(n);
    for (auto &row : rows)
    {
        int k;
        cin >> k;
        row.resize(k);
        for (int &c : row) cin >> c;
    }
    MinimumCover cover(m, rows);
    auto ans = cover.solve();
    if (!ans) cout << -1 << '\n';
    else
    {
        cout << ans->size() << '\n';
        for (int row : *ans) cout << row << ' ';
        cout << '\n';
    }
}
