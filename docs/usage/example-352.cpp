int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    TimeConnectivity graph(n, q);
    map<pair<int, int>, int> start;
    vector<pair<int, int>> ask(q, {-1, -1});
    for (int t = 0; t < q; ++t)
    {
        string op;
        int u, v;
        cin >> op >> u >> v;
        if (u > v)
            swap(u, v);
        pair<int, int> e = {u, v};
        if (op == "Connect")
            start[e] = t;
        else if (op == "Destroy")
        {
            auto it = start.find(e);
            graph.add(it->second, t, u, v);
            start.erase(it);
        }
        else
            ask[t] = e;
    }
    for (auto [e, t] : start)
        graph.add(t, q, e.first, e.second);
    graph.run([&](int t, const RollbackDSU &d)
    {
        auto [u, v] = ask[t];
        if (u != -1)
            cout << (d.find(u) == d.find(v) ? "Yes" : "No") << '\n';
    });
    return 0;
}
