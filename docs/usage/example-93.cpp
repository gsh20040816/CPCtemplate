int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        int s = n + m + 1, t = s + 1;
        BoundedMaxFlow f(t);
        for (int j = 1; j <= m; j++)
        {
            long long g;
            cin >> g;
            f.add(n + j, t, g, 365LL * 30000);
        }
        for (int i = 1; i <= n; i++)
        {
            int c, d;
            cin >> c >> d;
            f.add(s, i, 0, d);
            while (c--)
            {
                int j, lo, hi;
                cin >> j >> lo >> hi;
                f.add(i, n + j + 1, lo, hi);
            }
        }
        auto ans = f.solve(s, t);
        cout << (ans ? *ans : -1) << "\n\n";
    }
}
