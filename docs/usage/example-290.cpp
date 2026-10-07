int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    struct Op
    {
        char op;
        int x, y;
    };
    int n, m, tc = 0;
    while (cin >> n >> m && n)
    {
        vector<long long> a(n);
        for (auto &x : a) cin >> x;
        vector<pair<int, int>> edges(m);
        for (auto &[u, v] : edges)
        {
            cin >> u >> v;
            u--;
            v--;
        }
        vector<int> deleted(m);
        vector<Op> ops;
        char op;
        while (cin >> op && op != 'E')
        {
            int x, y = 0;
            cin >> x;
            x--;
            if (op == 'D') deleted[x] = 1;
            else cin >> y;
            if (op == 'C')
            {
                int old = a[x];
                a[x] = y;
                y = old;
            }
            ops.push_back({op, x, y});
        }
        MergeSplay t(a);
        auto join = [&](int e)
        {
            auto [u, v] = edges[e];
            t.merge(u, v);
        };
        for (int e = 0; e < m; e++)
            if (!deleted[e]) join(e);
        long long sum = 0;
        int count = 0;
        for (int i = (int)ops.size() - 1; i >= 0; i--)
        {
            auto [op, x, y] = ops[i];
            if (op == 'D') join(x);
            else if (op == 'C')
            {
                t.set(x, y);
            }
            else
            {
                long long k = (long long)t.size(x) - y + 1;
                auto id = t.kth(x, k);
                if (id) sum += t.value(*id);
                count++;
            }
        }
        cout << "Case " << ++tc << ": " << fixed << setprecision(6)
             << (long double)sum / count << '\n';
    }
}
