int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<int> a(n);
        for (int &x : a)
            cin >> x;
        Mo mo(n);
        for (int i = 0; i < m; i++)
        {
            int l, r;
            cin >> l >> r;
            mo.add(l - 1, r);
        }
        vector<int> cnt(n + 1);
        vector<pair<long long, long long>> ans(m);
        long long sum = 0;
        auto add = [&](int i)
        {
            sum += cnt[a[i]];
            cnt[a[i]]++;
        };
        auto del = [&](int i)
        {
            cnt[a[i]]--;
            sum -= cnt[a[i]];
        };
        auto save = [&](int id, long long len)
        {
            long long den = len * (len - 1) / 2;
            if (sum == 0)
            {
                ans[id] = {0, 1};
                return;
            }
            long long d = gcd(sum, den);
            ans[id] = {sum / d, den / d};
        };
        mo.run(add, del, [&](int id)
        {
            save(id, mo.q[id].r - mo.q[id].l);
        });
        for (auto [num, den] : ans)
            cout << num << '/' << den << '\n';
    }
}
