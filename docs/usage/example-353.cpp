int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q;
    while (cin >> n >> m >> q)
    {
        TimeConnectivity graph(n, q);
        // value = {active multiplicity, start of positive multiplicity}
        map<pair<int, int>, pair<int, int>> active;
        for (int i = 0; i < m; ++i)
        {
            int u, v;
            cin >> u >> v;
            if (u > v)
                swap(u, v);
            ++active[{u, v}].first;
        }
        vector<pair<int, int>> ask(q, {-1, -1});
        for (int t = 0; t < q; ++t)
        {
            char op;
            int u, v;
            cin >> op >> u >> v;
            if (op == '?')
            {
                ask[t] = {u, v};
                continue;
            }
            if (u > v)
                swap(u, v);
            pair<int, int> e = {u, v};
            auto &state = active[e];
            if (op == '+')
            {
                if (state.first == 0)
                    state.second = t;
                ++state.first;
            }
            else
            {
                assert(state.first > 0);
                --state.first;
                if (state.first == 0)
                    graph.add(state.second, t, u, v);
            }
        }
        for (auto [e, state] : active)
            if (state.first > 0)
                graph.add(state.second, q, e.first, e.second);
        graph.run([&](int t, const RollbackDSU &d)
        {
            auto [u, v] = ask[t];
            if (u != -1)
                cout << (d.find(u) == d.find(v)) << ' '
                     << d.siz[d.find(u)] << '\n';
        });
    }
    return 0;
}
