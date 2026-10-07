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
        vector<int> a(n), values;
        for (auto &x : a) cin >> x;
        values = a;
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
                values.push_back(y);
                swap(a[x], y);
            }
            ops.push_back({op, x, y});
        }
        sort(values.begin(), values.end());
        values.erase(unique(values.begin(), values.end()), values.end());
        auto index = [&](int x)
        {
            return lower_bound(values.begin(), values.end(), x) - values.begin();
        };
        MergeSplitTree t(values.size());
        for (int u = 0; u < n; u++)
        {
            if (u) t.split(0, 0, 0);
            t.add(u, index(a[u]), 1);
        }
        dsu d(n);
        auto join = [&](int e)
        {
            auto [u, v] = edges[e];
            u = d.find(u);
            v = d.find(v);
            if (u == v) return;
            t.merge(u, v);
            d.merge(u, v);
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
                int r = d.find(x);
                t.add(r, index(a[x]), -1);
                a[x] = y;
                t.add(r, index(a[x]), 1);
            }
            else
            {
                int r = d.find(x);
                long long k = (long long)d.size(r) - y + 1;
                int p = t.kth(r, k);
                if (p != -1) sum += values[p];
                count++;
            }
        }
        cout << "Case " << ++tc << ": " << fixed << setprecision(6)
             << (long double)sum / count << '\n';
    }
}
