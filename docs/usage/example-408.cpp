int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        HLD h(n);
        for (int i = 1; i < n; i++)
        {
            int u, v;
            cin >> u >> v;
            h.add(u, v);
        }
        vector<int> color(n + 1);
        vector<long long> w(n + 1);
        for (int u = 1; u <= n; u++) cin >> color[u];
        for (int u = 1; u <= n; u++) cin >> w[u];
        h.build();
        ColorMax tree(h, color, w);
        int q;
        cin >> q;
        while (q--)
        {
            int op, u;
            cin >> op >> u;
            if (op == 0) cout << tree.query(u) << '\n';
            else if (op == 1) tree.flip(u);
            else
            {
                long long value;
                cin >> value;
                tree.set_weight(u, value);
            }
        }
    }
}
