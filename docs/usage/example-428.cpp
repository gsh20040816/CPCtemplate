int main()
{
    using M = MatrixTree<10007>;
    int n, m;
    cin >> n >> m;
    vector<vector<int>> seen(n, vector<int>(n));
    vector<M::Edge> edges;
    while (m--)
    {
        int a, b;
        cin >> a >> b;
        a--;
        b--;
        if (a != b && !seen[a][b])
        {
            seen[a][b] = 1;
            edges.push_back({a, b, 1});
        }
    }
    cout << M::count(n, edges, 0, M::Kind::toward_root).v << '\n';
}
