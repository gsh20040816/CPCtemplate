auto op(long long x, long long y)
{
    return max(x, y);
}

auto e()
{
    return numeric_limits<long long>::lowest();
}

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int tests;
    cin >> tests;
    while (tests--)
    {
        int n;
        cin >> n;
        HLD h(n);
        vector<int> a(n), b(n), child(n);
        vector<long long> w(n), base(n, e());
        for (int i = 1; i < n; i++)
        {
            cin >> a[i] >> b[i] >> w[i];
            h.add(a[i], b[i]);
        }
        h.build();
        for (int i = 1; i < n; i++)
        {
            child[i] = h.dep[a[i]] > h.dep[b[i]] ? a[i] : b[i];
            base[h.dfn[child[i]] - 1] = w[i];
        }
        auto seg = segtree<long long, op, e>(base);
        string cmd;
        while (cin >> cmd && cmd != "DONE")
        {
            int u;
            cin >> u;
            if (cmd == "CHANGE")
            {
                long long x;
                cin >> x;
                seg.set(h.dfn[child[u]] - 1, x);
            }
            else
            {
                int v;
                cin >> v;
                long long ans = e();
                h.path(u, v, [&](int l, int r)
                {
                    ans = max(ans, seg.prod(l - 1, r));
                }, true);
                cout << (u == v ? 0 : ans) << '\n';
            }
        }
    }
}
