int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using Tree = MatrixTreeExact<boost::multiprecision::cpp_int>;
    int t;
    cin >> t;
    while (t--)
    {
        int n, m;
        cin >> n >> m;
        set<pair<int, int>> seen;
        while (m--)
        {
            int u, v;
            cin >> u >> v;
            u--;
            v--;
            if (u > v)
                swap(u, v);
            if (u != v)
                seen.insert({u, v});
        }
        vector<Tree::Edge> edges;
        for (auto [u, v] : seen)
            edges.emplace_back(u, v, 1);
        cout << Tree::count(n, edges, n - 1, Tree::Kind::undirected) << '\n';
    }
    return 0;
}
