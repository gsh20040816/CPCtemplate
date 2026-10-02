int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    LazySeg seg(n);
    for (int i = 1; i <= n; i++)
    {
        long long a;
        cin >> a;
        seg.add(i, i, a);
    }
    while (m--)
    {
        int op, l, r;
        cin >> op >> l >> r;
        if (op == 1)
        {
            long long k;
            cin >> k;
            seg.add(l, r, k);
        }
        else
            cout << seg.query(l, r) << '\n';
    }
}
