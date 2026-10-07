int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int root = n + 1;
    DagDominator d(root);
    for (int v = 1; v <= n; v++)
    {
        int u;
        cin >> u;
        if (!u)
            d.add(root, v);
        while (u)
        {
            d.add(u, v);
            cin >> u;
        }
    }
    if (!d.build(root))
        return 0;
    vector<int> size(root + 1, 1);
    for (int i = (int)d.order.size() - 1; i >= 0; i--)
    {
        int u = d.order[i];
        if (u != root)
            size[d.idom[u]] += size[u];
    }
    for (int u = 1; u <= n; u++)
        cout << size[u] - 1 << '\n';
    return 0;
}
