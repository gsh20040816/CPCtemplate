int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, root, mod;
    cin >> n >> m >> root >> mod;
    vector<long long> values(n + 1);
    for (int u = 1; u <= n; u++) cin >> values[u];
    HLD h(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        cin >> u >> v;
        h.add(u, v);
    }
    h.build(root);
    vector<long long> ordered(n);
    for (int u = 1; u <= n; u++) ordered[h.dfn[u] - 1] = values[u];
    AffineSegTree seg(ordered, mod);
    while (m--)
    {
        int op, u;
        cin >> op >> u;
        if (op == 1)
        {
            int v;
            long long x;
            cin >> v >> x;
            h.path(u, v, [&](int l, int r) { seg.update(l, r, 1, x); });
        }
        else if (op == 2)
        {
            int v;
            cin >> v;
            long long ans = 0;
            h.path(u, v, [&](int l, int r) { ans = (ans + seg.query(l, r)) % mod; });
            cout << ans << '\n';
        }
        else if (op == 3)
        {
            long long x;
            cin >> x;
            seg.update(h.dfn[u], h.dfn[u] + h.siz[u] - 1, 1, x);
        }
        else
            cout << seg.query(h.dfn[u], h.dfn[u] + h.siz[u] - 1) << '\n';
    }
}
