int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<long long> a(n + 1), values;
    for (int u = 1; u <= n; u++)
    {
        cin >> a[u];
        values.push_back(a[u]);
    }
    sort(values.begin(), values.end());
    values.erase(unique(values.begin(), values.end()), values.end());
    vector<int> color(n + 1), count(values.size());
    for (int u = 1; u <= n; u++)
    {
        color[u] = lower_bound(values.begin(), values.end(), a[u]) - values.begin();
    }
    HLD tree(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        tree.add(u, v);
    }
    tree.build();
    TreeMo mo(tree);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        cin >> u >> v;
        mo.add(u, v);
    }
    vector<int> answer(m);
    int distinct = 0;
    auto add = [&](int u)
    {
        if (count[color[u]]++ == 0) distinct++;
    };
    auto del = [&](int u)
    {
        if (--count[color[u]] == 0) distinct--;
    };
    mo.run(add, del, [&](int id)
    {
        answer[id] = distinct;
    });
    for (int x : answer) cout << x << '\n';
}
