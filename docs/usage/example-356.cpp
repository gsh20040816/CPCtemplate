int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    OverallKth solver(a);
    for (int i = 0; i < m; i++)
    {
        char op;
        cin >> op;
        if (op == 'Q')
        {
            int l, r, k;
            cin >> l >> r >> k;
            solver.query(l, r, k);
        }
        else
        {
            int pos;
            long long value;
            cin >> pos >> value;
            solver.set(pos, value);
        }
    }
    for (long long value : solver.run()) cout << value << '\n';
}
