int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, root;
    cin >> n >> m >> root;
    root++;
    DagDominator d(n);
    while (m--)
    {
        int u, v;
        cin >> u >> v;
        d.add(u + 1, v + 1);
    }
    vector<int> ans;
    if (d.build(root))
        ans = move(d.idom);
    else
    {
        DominatorTree t(n);
        t.g = move(d.g);
        t.build(root);
        ans = move(t.idom);
    }
    for (int u = 1; u <= n; u++)
        cout << ans[u] - 1 << (u == n ? '\n' : ' ');
    return 0;
}
