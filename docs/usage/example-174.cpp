int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m)
    {
        vector<long long> pre(n + 1);
        for (int i = 1; i <= n; i++)
        {
            cin >> pre[i];
            pre[i] += pre[i - 1];
        }
        PersistentRange tree(n);
        vector<int> ver(m + 1);
        int t = 0;
        while (m--)
        {
            char op;
            cin >> op;
            if (op == 'B')
            {
                cin >> t;
                continue;
            }
            int l, r;
            cin >> l >> r;
            l--;
            if (op == 'C')
            {
                long long d;
                cin >> d;
                int v = tree.add(ver[t], l, r, d);
                ver[++t] = v;
            }
            else
            {
                int h = t;
                if (op == 'H') cin >> h;
                cout << pre[r] - pre[l] + tree.query(ver[h], l, r) << '\n';
            }
        }
    }
    return 0;
}
