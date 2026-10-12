int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    TimeConnectivity tree(n, q);
    map<pair<int, int>, int> start;
    vector<pair<int, int>> query(q, {-1, -1});
    for (int t = 0; t < q; t++)
    {
        int op, u, v;
        cin >> op >> u >> v;
        if (u > v) swap(u, v);
        pair<int, int> edge{u, v};
        if (op == 0)
            start[edge] = t;
        else if (op == 1)
        {
            auto it = start.find(edge);
            tree.add(it->second, t, u, v);
            start.erase(it);
        }
        else
            query[t] = edge;
    }
    for (auto [edge, l] : start)
        tree.add(l, q, edge.first, edge.second);
    tree.run([&](int t, const RollbackDSU &d)
    {
        auto [u, v] = query[t];
        if (u != -1)
            cout << (d.find(u) == d.find(v) ? 'Y' : 'N') << '\n';
    });
}
