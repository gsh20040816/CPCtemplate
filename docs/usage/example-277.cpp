int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    vector<int> a(n);
    for (int &x : a) cin >> x;
    StaticRMQ<int, greater<int>> rmq(a);
    while (q--)
    {
        int l, r;
        cin >> l >> r;
        cout << rmq.a[rmq.query(l - 1, r)] << '\n';
    }
}
