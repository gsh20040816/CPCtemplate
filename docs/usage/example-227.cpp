int main()
{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    int n, m;
    if (!(std::cin >> n >> m)) return 0;
    BiconnectedCore core(n);
    Lowlink graph(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        std::cin >> u >> v;
        core.add(u, v);
        graph.add(u, v); // Same insertion order preserves logical edge IDs.
    }
    // Existing recursive cores require a sufficiently large process stack.
    // An 8 MiB stack fails at n=400000; judge stack availability is not assumed.
    core.run();
    EdgeCompression compressed(core);
    int root = 1;
    for (int c = 2; c <= compressed.n; c++)
        if (compressed.size[c] > compressed.size[root]) root = c;
    auto direction = orient_edges(graph); // Does not need graph.run().
    vector<vector<pair<int, int>>> tree(compressed.n + 1);
    for (auto [u, v, id] : compressed.edges)
    {
        tree[u].push_back({v, id});
        tree[v].push_back({u, id}); // Compressed endpoints are not parent/child.
    }
    vector<int> parent(compressed.n + 1), order{root};
    parent[root] = -1;
    for (int i = 0; i < (int)order.size(); i++)
    {
        int u = order[i];
        for (auto [v, id] : tree[u])
        {
            if (parent[v]) continue;
            parent[v] = u;
            order.push_back(v);
            auto [a, b] = core.edges[id];
            if (core.bel[a] != v) swap(a, b);
            direction[id] = {a, b}; // Original bridge points child -> parent.
        }
    }
    std::cout << compressed.size[root] << '\n';
    for (auto [u, v] : direction) std::cout << u << ' ' << v << '\n';
    return 0;
}
