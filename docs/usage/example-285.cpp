int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    CentroidDiameter t(n);
    for (int i = 1; i < n; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        t.add(u, v, w);
    }
    t.build();
    while (q--)
    {
        int op;
        cin >> op;
        if (op == 0)
        {
            int u, on;
            cin >> u >> on;
            t.set(u, on);
        }
        else
        {
            auto ans = t.query();
            if (!ans) cout << -1 << '\n';
            else
            {
                auto [d, u, v] = *ans;
                cout << d << ' ' << u << ' ' << v << '\n';
            }
        }
    }
}
