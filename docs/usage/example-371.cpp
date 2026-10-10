int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q, down;
    cin >> n >> m >> q >> down;
    KruskalTree tr(n);
    for (int i = 0; i < m; i++)
    {
        int u, v;
        long long w;
        cin >> u >> v >> w;
        tr.add(u, v, w);
    }
    cout << tr.build(down) << '\n';
    int k = tr.ch.size();
    vector<int> cnt(k, 1), low(k);
    iota(low.begin(), low.end(), 0);
    for (int u = n; u < k; u++)
    {
        auto [l, r] = tr.ch[u];
        cnt[u] = cnt[l] + cnt[r];
        low[u] = min(low[l], low[r]);
    }
    while (q--)
    {
        int u, strict;
        long long w;
        cin >> u >> w >> strict;
        int v = tr.component(u, w, strict);
        cout << cnt[v] << ' ' << low[v] << '\n';
    }
}
