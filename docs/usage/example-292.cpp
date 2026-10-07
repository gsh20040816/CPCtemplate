int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    MergeSplay t(a);
    while (q--)
    {
        int op, x;
        long long y;
        cin >> op >> x;
        if (op <= 2) cin >> y;
        if (op == 0) cout << t.merge(x, y) << '\n';
        else if (op == 1) t.set(x, y);
        else if (op == 2)
        {
            auto id = t.kth(x, y);
            if (id) cout << *id << ' ' << t.value(*id) << '\n';
            else cout << -1 << '\n';
        }
        else cout << t.size(x) << ' ' << t.rank(x) << '\n';
    }
}
