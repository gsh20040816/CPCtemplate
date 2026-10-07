int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    while (cin >> n)
    {
        vector<long long> a(n);
        for (auto &x : a)
            cin >> x;
        SequenceKth tree(a);
        int q;
        cin >> q;
        int ans = 0;
        while (q--)
        {
            char op;
            int x, y;
            cin >> op >> x >> y;
            x ^= ans;
            y ^= ans;
            if (op == 'Q')
            {
                int k;
                cin >> k;
                k ^= ans;
                ans = (int)tree.kth(x, y, k);
                cout << ans << '\n';
            }
            else if (op == 'M')
                tree.set(x, y);
            else
                tree.insert(x - 1, y);
        }
    }
}
