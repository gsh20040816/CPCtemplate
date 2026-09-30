int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    assert(1 <= tests && tests <= 10000);
    while (tests--)
    {
        char mode;
        int n, m, start, finish;
        cin >> mode >> n >> m >> start >> finish;
        assert(1 <= n && n <= 200 && 0 <= m && m <= 800);
        assert(mode == 'C' || mode == 'A' || mode == 'P');
        assert(mode == 'P' ? 1 <= start && start <= n && 1 <= finish && finish <= n
                           : start == 0 && finish == 0);
        vector<array<int, 3>> edges(m);
        for (auto &[u, v, type] : edges) cin >> u >> v >> type;
        optional<vector<pair<int, int>>> direction;
        if (mode == 'A')
            direction = mixed_euler_trail(n, edges);
        else if (mode == 'C')
            direction = mixed_euler_orientation(n, edges);
        else
            direction = mixed_euler_orientation(n, edges, start, finish);
        if (!direction)
        {
            cout << "NO\n";
            continue;
        }
        // A present empty vector is a valid zero-edge circuit, not failure.
        DirectedEuler trail(n);
        for (auto [u, v] : *direction) trail.add(u, v);
        // Preserve a requested start. The orientation is not globally lexicographic.
        if (!trail.run(start, false)) return 1;
        cout << "YES\nVERTICES " << trail.vertices.size();
        for (int u : trail.vertices) cout << ' ' << u;
        cout << "\nEDGES " << trail.edge_ids.size();
        // add() used original input order; its 0-based IDs become 1-based here.
        for (int id : trail.edge_ids) cout << ' ' << id + 1;
        cout << '\n';
    }
    return 0;
}
