int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<vector<long long>> a(n, vector<long long>(m));
        for (auto &row : a)
        {
            for (auto &x : row) cin >> x;
        }
        StaticRMQ2D<long long, greater<long long>> rmq(a);
        int q;
        cin >> q;
        while (q--)
        {
            int x1, y1, x2, y2;
            cin >> x1 >> y1 >> x2 >> y2;
            if (x1 > x2) swap(x1, x2);
            if (y1 > y2) swap(y1, y2);
            auto [x, y] = rmq.query(x1 - 1, y1 - 1, x2, y2);
            long long value = rmq.a[x][y];
            bool corner = value == a[x1 - 1][y1 - 1] || value == a[x1 - 1][y2 - 1] ||
                          value == a[x2 - 1][y1 - 1] || value == a[x2 - 1][y2 - 1];
            cout << value << ' ' << (corner ? "yes" : "no") << '\n';
        }
    }
}
