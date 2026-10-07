int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<array<long long, 5>> targets(n);
    for (auto &t : targets)
    {
        for (auto &x : t) cin >> x;
    }
    vector<int> order(n);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int x, int y)
    {
        return targets[x][4] < targets[y][4];
    });
    int m;
    cin >> m;
    vector<KDMin::Item> shots(m);
    for (int i = 0; i < m; i++)
    {
        cin >> shots[i].p[0] >> shots[i].p[1];
        shots[i].key = i;
    }
    KDMin kd(shots);
    vector<int> ans(m);
    for (int id : order)
    {
        auto [xl, xr, yl, yr, z] = targets[id];
        int shot = kd.query({xl, yl}, {xr, yr});
        if (shot == -1) continue;
        ans[shot] = id + 1;
        kd.erase(shot);
    }
    for (int x : ans) cout << x << '\n';
}
