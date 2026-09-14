int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using G = GaussMod<998244353>;
    int n, m;
    cin >> n >> m;
    G::Matrix a(n, vector<G::Z>(m + 1));
    for (auto &row : a)
        for (int j = 0; j < m; j++) cin >> row[j].v;
    for (auto &row : a) cin >> row[m].v;
    auto s = G::solve(move(a), m);
    if (!s.consistent)
    {
        cout << -1 << '\n';
        return 0;
    }
    cout << s.kernel.size() << '\n';
    auto print = [&](const vector<G::Z> &row)
    {
        for (int j = 0; j < m; j++) cout << row[j].v << (j + 1 == m ? '\n' : ' ');
    };
    print(s.particular);
    for (auto &row : s.kernel) print(row);
}
