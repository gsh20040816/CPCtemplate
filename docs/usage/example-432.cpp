int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<array<int, 3>> a(n);
    vector<int> xs, ys;
    for (auto &[x, y, w] : a)
    {
        cin >> x >> y >> w;
        ys.push_back(y);
    }
    sort(a.begin(), a.end());
    sort(ys.begin(), ys.end());
    ys.erase(unique(ys.begin(), ys.end()), ys.end());
    auto rank = [&](int y)
    {
        return lower_bound(ys.begin(), ys.end(), y) - ys.begin();
    };
    PersistentWeightedIndex tree(ys.size());
    for (int i = 0; i < n; i++)
    {
        auto [x, y, w] = a[i];
        xs.push_back(x);
        tree.add(i, rank(y), w);
    }
    while (q--)
    {
        int l, d, r, u;
        cin >> l >> d >> r >> u;
        int before = lower_bound(xs.begin(), xs.end(), l) - xs.begin();
        int after = lower_bound(xs.begin(), xs.end(), r) - xs.begin();
        long long answer = tree.query(after, rank(d), rank(u)).second;
        answer -= tree.query(before, rank(d), rank(u)).second;
        cout << answer << '\n';
    }
}
