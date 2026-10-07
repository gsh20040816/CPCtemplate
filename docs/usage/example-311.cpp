int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    BipartiteMatching g(n, n);
    for (int i = 1; i <= n; i++)
    {
        string row;
        cin >> row;
        for (int j = 1; j <= n; j++)
        {
            if (row[j - 1] == 'o') g.add(i, j);
        }
    }
    cout << g.solve() << '\n';
    auto [a, b] = g.cover();
    for (int u : a) cout << 1 << ' ' << u << '\n';
    for (int v : b) cout << 2 << ' ' << v << '\n';
}
