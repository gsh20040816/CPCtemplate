int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    using G = IntegerPlane;
    int t;
    cin >> t;
    while (t--)
    {
        int n, m;
        cin >> n;
        vector<G::Point> p(n);
        for (auto &v : p) cin >> v.x >> v.y;
        cin >> m;
        vector<G::Point> q(m);
        for (auto &v : q) cin >> v.x >> v.y;
        vector<int> f(2 * n);
        for (int i = 0, j = 1; i < n; i++)
        {
            int k = convex_tangents_i64(q, p[i])->second;
            j = max(j, i + 1);
            while (j + 1 < i + n && G::cross(p[i], p[(j + 1) % n], q[k]) >= 0)
                j++;
            f[i] = j;
            f[i + n] = j + n;
        }
        vector<long long> sum(2 * n + 1);
        for (int i = 0; i < 2 * n; i++) sum[i + 1] = sum[i] + f[i];
        long long ans = 0;
        for (int a = 0, g = 0, h = 0; a < n; a++)
        {
            while (f[g] < a + n) g++;
            h = max(h, a + 1);
            while (h <= f[a] && f[h] < g) h++;
            if (h <= f[a])
                ans += sum[f[a] + 1] - sum[h] - 1LL * (f[a] - h + 1) * (g - 1);
        }
        cout << ans / 3 << '\n';
    }
}
