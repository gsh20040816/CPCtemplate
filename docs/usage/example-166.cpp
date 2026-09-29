int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    BiconnectedCore graph(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        cin >> u >> v;
        graph.add(u, v);
    }
    graph.run();
    auto tree = bridge_component_forest(graph);
    int leaves = 0;
    for (int u = 1; u <= graph.cnt; u++)
        if (tree[u].size() == 1) leaves++;
    cout << (leaves + 1) / 2 << '\n';
    return 0;
}
